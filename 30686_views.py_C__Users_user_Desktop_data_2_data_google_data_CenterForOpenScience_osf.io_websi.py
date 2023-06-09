# -*- coding: utf-8 -*-

import datetime
import logging
import httplib
import httplib as http  # TODO: Inconsistent usage of aliased import
from dateutil.parser import parse as parse_date

from flask import request
import markupsafe
from modularodm.exceptions import ValidationError, NoResultsFound, MultipleResultsFound
from modularodm import Q

from framework import sentry
from framework.auth import utils as auth_utils
from framework.auth.decorators import collect_auth
from framework.auth.decorators import must_be_logged_in
from framework.auth.exceptions import ChangePasswordError
from framework.auth.views import send_confirm_email
from framework.auth.signals import user_merged
from framework.exceptions import HTTPError, PermissionsError
from framework.flask import redirect  # VOL-aware redirect
from framework.status import push_status_message

from website import mails
from website import mailchimp_utils
from website import settings
from website.project.model import Node
from website.models import ApiOAuth2Application, ApiOAuth2PersonalToken, User
from website.oauth.utils import get_available_scopes
from website.profile import utils as profile_utils
from website.util.time import throttle_period_expired
from website.util import api_v2_url, web_url_for, paths
from website.util.sanitize import escape_html
from website.util.sanitize import strip_html
from website.views import _render_nodes
from website.addons.base import utils as addon_utils

logger = logging.getLogger(__name__)


def get_public_projects(uid=None, user=None):
    user = user or User.load(uid)

    nodes = Node.find_for_user(
        user,
        subquery=(
            Q('category', 'eq', 'project') &
            Q('is_public', 'eq', True) &
            Q('is_registration', 'eq', False) &
            Q('is_deleted', 'eq', False)
        )
    )
    return _render_nodes(list(nodes))


def get_public_components(uid=None, user=None):
    user = user or User.load(uid)
    # TODO: This should use User.visible_contributor_to?

    nodes = list(
        Node.find_for_user(
            user,
            (
                Q('category', 'ne', 'project') &
                Q('is_public', 'eq', True) &
                Q('is_registration', 'eq', False) &
                Q('is_deleted', 'eq', False)
            )
        )
    )
    return _render_nodes(nodes, show_path=True)


@must_be_logged_in
def current_user_gravatar(size=None, **kwargs):
    user_id = kwargs['auth'].user._id
    return get_gravatar(user_id, size=size)


def get_gravatar(uid, size=None):
    return {'gravatar_url': profile_utils.get_gravatar(User.load(uid), size=size)}


def date_or_none(date):
    try:
        return parse_date(date)
    except Exception as error:
        logger.exception(error)
        return None


def validate_user(data, user):
    """Check if the user in request is the user who log in """
    if 'id' in data:
        if data['id'] != user._id:
            raise HTTPError(httplib.FORBIDDEN)
    else:
        # raise an error if request doesn't have user id
        raise HTTPError(httplib.BAD_REQUEST, data={'message_long': '"id" is required'})

@must_be_logged_in
def resend_confirmation(auth):
    user = auth.user
    data = request.get_json()

    validate_user(data, user)
    if not throttle_period_expired(user.email_last_sent, settings.SEND_EMAIL_THROTTLE):
        raise HTTPError(httplib.BAD_REQUEST,
                        data={'message_long': 'Too many requests. Please wait a while before sending another confirmation email.'})

    try:
        primary = data['email']['primary']
        confirmed = data['email']['confirmed']
        address = data['email']['address'].strip().lower()
    except KeyError:
        raise HTTPError(httplib.BAD_REQUEST)

    if primary or confirmed:
        raise HTTPError(httplib.BAD_REQUEST, data={'message_long': 'Cannnot resend confirmation for confirmed emails'})

    user.add_unconfirmed_email(address)

    # TODO: This setting is now named incorrectly.
    if settings.CONFIRM_REGISTRATIONS_BY_EMAIL:
        send_confirm_email(user, email=address)
        user.email_last_sent = datetime.datetime.utcnow()

    user.save()

    return _profile_view(user, is_profile=True)

@must_be_logged_in
def update_user(auth):
    """Update the logged-in user's profile."""

    # trust the decorator to handle auth
    user = auth.user
    data = request.get_json()

    validate_user(data, user)

    # TODO: Expand this to support other user attributes

    ##########
    # Emails #
    ##########

    if 'emails' in data:

        emails_list = [x['address'].strip().lower() for x in data['emails']]

        if user.username.strip().lower() not in emails_list:
            raise HTTPError(httplib.FORBIDDEN)

        available_emails = [
            each.strip().lower() for each in
            user.emails + user.unconfirmed_emails
        ]
        # removals
        removed_emails = [
            each.strip().lower()
            for each in available_emails
            if each not in emails_list
        ]

        if user.username.strip().lower() in removed_emails:
            raise HTTPError(httplib.FORBIDDEN)

        for address in removed_emails:
            if address in user.emails:
                try:
                    user.remove_email(address)
                except PermissionsError as e:
                    raise HTTPError(httplib.FORBIDDEN, e.message)
            user.remove_unconfirmed_email(address)

        # additions
        added_emails = [
            each['address'].strip().lower()
            for each in data['emails']
            if each['address'].strip().lower() not in available_emails
        ]

        for address in added_emails:
            try:
                user.add_unconfirmed_email(address)
            except (ValidationError, ValueError):
                raise HTTPError(http.BAD_REQUEST, data=dict(
                    message_long="Invalid Email")
                )

            # TODO: This setting is now named incorrectly.
            if settings.CONFIRM_REGISTRATIONS_BY_EMAIL:
                send_confirm_email(user, email=address)

        ############
        # Username #
        ############

        # get the first email that is set to primary and has an address
        primary_email = next(
            (
                each for each in data['emails']
                # email is primary
                if each.get('primary') and each.get('confirmed')
                # an address is specified (can't trust those sneaky users!)
                and each.get('address')
            )
        )

        if primary_email:
            primary_email_address = primary_email['address'].strip().lower()
            if primary_email_address not in [each.strip().lower() for each in user.emails]:
                raise HTTPError(httplib.FORBIDDEN)
            username = primary_email_address

        # make sure the new username has already been confirmed
        if username and username in user.emails and username != user.username:
            mails.send_mail(user.username,
                            mails.PRIMARY_EMAIL_CHANGED,
                            user=user,
                            new_address=username)

            # Remove old primary email from subscribed mailing lists
            for list_name, subscription in user.mailchimp_mailing_lists.iteritems():
                if subscription:
                    mailchimp_utils.unsubscribe_mailchimp_async(list_name, user._id, username=user.username)
            user.username = username

    ###################
    # Timezone/Locale #
    ###################

    if 'locale' in data:
        if data['locale']:
            locale = data['locale'].replace('-', '_')
            user.locale = locale
    # TODO: Refactor to something like:
    #   user.timezone = data.get('timezone', user.timezone)
    if 'timezone' in data:
        if data['timezone']:
            user.timezone = data['timezone']

    user.save()

    # Update subscribed mailing lists with new primary email
    # TODO: move to user.save()
    for list_name, subscription in user.mailchimp_mailing_lists.iteritems():
        if subscription:
            mailchimp_utils.subscribe_mailchimp(list_name, user._id)

    return _profile_view(user, is_profile=True)


def _profile_view(profile, is_profile=False):
    # TODO: Fix circular import
    from website.addons.badges.util import get_sorted_user_badges

    if profile and profile.is_disabled:
        raise HTTPError(http.GONE)

    if 'badges' in settings.ADDONS_REQUESTED:
        badge_assertions = get_sorted_user_badges(profile),
        badges = _get_user_created_badges(profile)
    else:
        # NOTE: While badges, are unused, 'assertions' and 'badges' can be
        # empty lists.
        badge_assertions = []
        badges = []

    if profile:
        profile_user_data = profile_utils.serialize_user(profile, full=True, is_profile=is_profile)
        return {
            'profile': profile_user_data,
            'assertions': badge_assertions,
            'badges': badges,
            'user': {
                'is_profile': is_profile,
                'can_edit': None,  # necessary for rendering nodes
                'permissions': [],  # necessary for rendering nodes
            },
        }

    raise HTTPError(http.NOT_FOUND)


def _get_user_created_badges(user):
    from website.addons.badges.model import Badge
    addon = user.get_addon('badges')
    if addon:
        return [badge for badge in Badge.find(Q('creator', 'eq', addon._id)) if not badge.is_system_badge]
    return []


@must_be_logged_in
def profile_view(auth):
    return _profile_view(auth.user, True)


@collect_auth
def profile_view_id(uid, auth):
    user = User.load(uid)
    is_profile = auth and auth.user == user
    return _profile_view(user, is_profile)


@must_be_logged_in
def edit_profile(**kwargs):
    # NOTE: This method is deprecated. Use update_user instead.
    # TODO: Remove this view
    user = kwargs['auth'].user

    form = request.form

    ret = {'response': 'success'}
    if form.get('name') == 'fullname' and form.get('value', '').strip():
        user.fullname = strip_html(form['value']).strip()
        user.save()
        ret['name'] = user.fullname
    return ret


def get_profile_summary(user_id, formatter='long'):

    user = User.load(user_id)
    return user.get_summary(formatter)


@must_be_logged_in
def user_profile(auth, **kwargs):
    user = auth.user
    return {
        'user_id': user._id,
        'user_api_url': user.api_url,
    }


@must_be_logged_in
def user_account(auth, **kwargs):
    user = auth.user
    user_addons = addon_utils.get_addons_by_config_type('user', user)

    return {
        'user_id': user._id,
        'addons': user_addons,
        'addons_js': collect_user_config_js([addon for addon in settings.ADDONS_AVAILABLE if 'user' in addon.configs]),
        'addons_css': []
    }


@must_be_logged_in
def user_account_password(auth, **kwargs):
    user = auth.user
    old_password = request.form.get('old_password', None)
    new_password = request.form.get('new_password', None)
    confirm_password = request.form.get('confirm_password', None)

    try:
        user.change_password(old_password, new_password, confirm_password)
        user.save()
    except ChangePasswordError as error:
        for m in error.messages:
            push_status_message(m, kind='warning', trust=False)
    else:
        push_status_message('Password updated successfully.', kind='success', trust=False)

    return redirect(web_url_for('user_account'))


@must_be_logged_in
def user_addons(auth, **kwargs):

    user = auth.user

    ret = {
        'addon_settings': addon_utils.get_addons_by_config_type('accounts', user),
    }
    accounts_addons = [addon for addon in settings.ADDONS_AVAILABLE if 'accounts' in addon.configs]
    ret.update({
        'addon_enabled_settings': [addon.short_name for addon in accounts_addons],
        'addons_js': collect_user_config_js(accounts_addons),
        'addon_capabilities': settings.ADDON_CAPABILITIES,
        'addons_css': []
    })
    return ret

@must_be_logged_in
def user_notifications(auth, **kwargs):
    """Get subscribe data from user"""
    return {
        'mailing_lists': dict(auth.user.mailchimp_mailing_lists.items() + auth.user.osf_mailing_lists.items())
    }

@must_be_logged_in
def oauth_application_list(auth, **kwargs):
    """Return app creation page with list of known apps. API is responsible for tying list to current user."""
    app_list_url = api_v2_url("applications/")
    return {
        "app_list_url": app_list_url
    }

@must_be_logged_in
def oauth_application_register(auth, **kwargs):
    """Register an API application: blank form view"""
    app_list_url = api_v2_url("applications/")  # POST request to this url
    return {"app_list_url": app_list_url,
            "app_detail_url": ''}

@must_be_logged_in
def oauth_application_detail(auth, **kwargs):
    """Show detail for a single OAuth application"""
    client_id = kwargs.get('client_id')

    # The client ID must be an active and existing record, and the logged-in user must have permission to view it.
    try:
        #
        record = ApiOAuth2Application.find_one(Q('client_id', 'eq', client_id))
    except NoResultsFound:
        raise HTTPError(http.NOT_FOUND)
    if record.owner != auth.user:
        raise HTTPError(http.FORBIDDEN)
    if record.is_active is False:
        raise HTTPError(http.GONE)

    app_detail_url = api_v2_url("applications/{}/".format(client_id))  # Send request to this URL
    return {"app_list_url": '',
            "app_detail_url": app_detail_url}

@must_be_logged_in
def personal_access_token_list(auth, **kwargs):
    """Return token creation page with list of known tokens. API is responsible for tying list to current user."""
    token_list_url = api_v2_url("tokens/")
    return {
        "token_list_url": token_list_url
    }

@must_be_logged_in
def personal_access_token_register(auth, **kwargs):
    """Register a personal access token: blank form view"""
    token_list_url = api_v2_url("tokens/")  # POST request to this url
    return {"token_list_url": token_list_url,
            "token_detail_url": '',
            "scope_options": get_available_scopes()}

@must_be_logged_in
def personal_access_token_detail(auth, **kwargs):
    """Show detail for a single personal access token"""
    _id = kwargs.get('_id')

    # The ID must be an active and existing record, and the logged-in user must have permission to view it.
    try:
        record = ApiOAuth2PersonalToken.find_one(Q('_id', 'eq', _id))
    except NoResultsFound:
        raise HTTPError(http.NOT_FOUND)
    if record.owner != auth.user:
        raise HTTPError(http.FORBIDDEN)
    if record.is_active is False:
        raise HTTPError(http.GONE)

    token_detail_url = api_v2_url("tokens/{}/".format(_id))  # Send request to this URL
    return {"token_list_url": '',
            "token_detail_url": token_detail_url,
            "scope_options": get_available_scopes()}


def collect_user_config_js(addon_configs):
    """Collect webpack bundles for each of the addons' user-cfg.js modules. Return
    the URLs for each of the JS modules to be included on the user addons config page.

    :param list addons: List of user's addon config records.
    """
    js_modules = []
    for addon_config in addon_configs:
        js_path = paths.resolve_addon_path(addon_config, 'user-cfg.js')
        if js_path:
            js_modules.append(js_path)
    return js_modules


@must_be_logged_in
def user_choose_addons(**kwargs):
    auth = kwargs['auth']
    json_data = escape_html(request.get_json())
    auth.user.config_addons(json_data, auth)

@must_be_logged_in
def user_choose_mailing_lists(auth, **kwargs):
    """ Update mailing list subscription on user model and in mailchimp

        Example input:
        {
            "Open Science Framework General": true,
            ...
        }

    """
    user = auth.user
    json_data = escape_html(request.get_json())
    if json_data:
        for list_name, subscribe in json_data.items():
            # TO DO: change this to take in any potential non-mailchimp, something like try: update_subscription(), except IndexNotFound: update_mailchimp_subscription()
            if list_name == settings.OSF_HELP_LIST:
                update_osf_help_mails_subscription(user=user, subscribe=subscribe)
            else:
                update_mailchimp_subscription(user, list_name, subscribe)
    else:
        raise HTTPError(http.BAD_REQUEST, data=dict(
            message_long="Must provide a dictionary of the format {'mailing list name': Boolean}")
        )

    user.save()
    all_mailing_lists = {}
    all_mailing_lists.update(user.mailchimp_mailing_lists)
    all_mailing_lists.update(user.osf_mailing_lists)
    return {'message': 'Successfully updated mailing lists', 'result': all_mailing_lists}, 200


@user_merged.connect
def update_mailchimp_subscription(user, list_name, subscription, send_goodbye=True):
    """ Update mailing list subscription in mailchimp.

    :param obj user: current user
    :param str list_name: mailing list
    :param boolean subscription: true if user is subscribed
    """
    if subscription:
        mailchimp_utils.subscribe_mailchimp(list_name, user._id)
    else:
        try:
            mailchimp_utils.unsubscribe_mailchimp_async(list_name, user._id, username=user.username, send_goodbye=send_goodbye)
        except mailchimp_utils.mailchimp.ListNotSubscribedError:
            raise HTTPError(http.BAD_REQUEST,
                data=dict(message_short="ListNotSubscribedError",
                        message_long="The user is already unsubscribed from this mailing list.",
                        error_type="not_subscribed")
            )


def mailchimp_get_endpoint(**kwargs):
    """Endpoint that the mailchimp webhook hits to check that the OSF is responding"""
    return {}, http.OK


def sync_data_from_mailchimp(**kwargs):
    """Endpoint that the mailchimp webhook sends its data to"""
    key = request.args.get('key')

    if key == settings.MAILCHIMP_WEBHOOK_SECRET_KEY:
        r = request
        action = r.values['type']
        list_name = mailchimp_utils.get_list_name_from_id(list_id=r.values['data[list_id]'])
        username = r.values['data[email]']

        try:
            user = User.find_one(Q('username', 'eq', username))
        except NoResultsFound:
            sentry.log_exception()
            sentry.log_message("A user with this username does not exist.")
            raise HTTPError(404, data=dict(message_short='User not found',
                                        message_long='A user with this username does not exist'))
        if action == 'unsubscribe':
            user.mailchimp_mailing_lists[list_name] = False
            user.save()

        elif action == 'subscribe':
            user.mailchimp_mailing_lists[list_name] = True
            user.save()

    else:
        # TODO: get tests to pass with sentry logging
        # sentry.log_exception()
        # sentry.log_message("Unauthorized request to the OSF.")
        raise HTTPError(http.UNAUTHORIZED)


@must_be_logged_in
def impute_names(**kwargs):
    name = request.args.get('name', '')
    return auth_utils.impute_names(name)


def update_osf_help_mails_subscription(user, subscribe):
    user.osf_mailing_lists[settings.OSF_HELP_LIST] = subscribe
    user.save()

@must_be_logged_in
def serialize_names(**kwargs):
    user = kwargs['auth'].user
    return {
        'full': user.fullname,
        'given': user.given_name,
        'middle': user.middle_names,
        'family': user.family_name,
        'suffix': user.suffix,
    }


def get_target_user(auth, uid=None):
    target = User.load(uid) if uid else auth.user
    if target is None:
        raise HTTPError(http.NOT_FOUND)
    return target


def fmt_date_or_none(date, fmt='%Y-%m-%d'):
    if date:
        try:
            return date.strftime(fmt)
        except ValueError:
            raise HTTPError(
                http.BAD_REQUEST,
                data=dict(message_long='Year entered must be after 1900')
            )
    return None


def append_editable(data, auth, uid=None):
    target = get_target_user(auth, uid)
    data['editable'] = auth.user == target


def serialize_social_addons(user):
    ret = {}
    for user_settings in user.get_addons():
        config = user_settings.config
        if user_settings.public_id:
            ret[config.short_name] = user_settings.public_id
    return ret


@collect_auth
def serialize_social(auth, uid=None, **kwargs):
    target = get_target_user(auth, uid)
    ret = target.social
    append_editable(ret, auth, uid)
    if ret['editable']:
        ret['addons'] = serialize_social_addons(target)
    return ret


def serialize_job(job):
    return {
        'institution': job.get('institution'),
        'department': job.get('department'),
        'title': job.get('title'),
        'startMonth': job.get('startMonth'),
        'startYear': job.get('startYear'),
        'endMonth': job.get('endMonth'),
        'endYear': job.get('endYear'),
        'ongoing': job.get('ongoing', False),
    }


def serialize_school(school):
    return {
        'institution': school.get('institution'),
        'department': school.get('department'),
        'degree': school.get('degree'),
        'startMonth': school.get('startMonth'),
        'startYear': school.get('startYear'),
        'endMonth': school.get('endMonth'),
        'endYear': school.get('endYear'),
        'ongoing': school.get('ongoing', False),
    }


def serialize_contents(field, func, auth, uid=None):
    target = get_target_user(auth, uid)
    ret = {
        'contents': [
            func(content)
            for content in getattr(target, field)
        ]
    }
    append_editable(ret, auth, uid)
    return ret


@collect_auth
def serialize_jobs(auth, uid=None, **kwargs):
    ret = serialize_contents('jobs', serialize_job, auth, uid)
    append_editable(ret, auth, uid)
    return ret


@collect_auth
def serialize_schools(auth, uid=None, **kwargs):
    ret = serialize_contents('schools', serialize_school, auth, uid)
    append_editable(ret, auth, uid)
    return ret


@must_be_logged_in
def unserialize_names(**kwargs):
    user = kwargs['auth'].user
    json_data = escape_html(request.get_json())
    # json get can return None, use `or` here to ensure we always strip a string
    user.fullname = (json_data.get('full') or '').strip()
    user.given_name = (json_data.get('given') or '').strip()
    user.middle_names = (json_data.get('middle') or '').strip()
    user.family_name = (json_data.get('family') or '').strip()
    user.suffix = (json_data.get('suffix') or '').strip()
    user.save()


def verify_user_match(auth, **kwargs):
    uid = kwargs.get('uid')
    if uid and uid != auth.user._id:
        raise HTTPError(http.FORBIDDEN)


@must_be_logged_in
def unserialize_social(auth, **kwargs):

    verify_user_match(auth, **kwargs)

    user = auth.user
    json_data = escape_html(request.get_json())

    for soc in user.SOCIAL_FIELDS.keys():
        user.social[soc] = json_data.get(soc)

    try:
        user.save()
    except ValidationError as exc:
        raise HTTPError(http.BAD_REQUEST, data=dict(
            message_long=exc.args[0]
        ))


def unserialize_job(job):
    return {
        'institution': job.get('institution'),
        'department': job.get('department'),
        'title': job.get('title'),
        'startMonth': job.get('startMonth'),
        'startYear': job.get('startYear'),
        'endMonth': job.get('endMonth'),
        'endYear': job.get('endYear'),
        'ongoing': job.get('ongoing'),
    }


def unserialize_school(school):
    return {
        'institution': school.get('institution'),
        'department': school.get('department'),
        'degree': school.get('degree'),
        'startMonth': school.get('startMonth'),
        'startYear': school.get('startYear'),
        'endMonth': school.get('endMonth'),
        'endYear': school.get('endYear'),
        'ongoing': school.get('ongoing'),
    }


def unserialize_contents(field, func, auth):
    user = auth.user
    json_data = escape_html(request.get_json())
    setattr(
        user,
        field,
        [
            func(content)
            for content in json_data.get('contents', [])
        ]
    )
    user.save()


@must_be_logged_in
def unserialize_jobs(auth, **kwargs):
    verify_user_match(auth, **kwargs)
    unserialize_contents('jobs', unserialize_job, auth)
    # TODO: Add return value


@must_be_logged_in
def unserialize_schools(auth, **kwargs):
    verify_user_match(auth, **kwargs)
    unserialize_contents('schools', unserialize_school, auth)
    # TODO: Add return value


@must_be_logged_in
def request_export(auth):
    user = auth.user
    if not throttle_period_expired(user.email_last_sent, settings.SEND_EMAIL_THROTTLE):
        raise HTTPError(httplib.BAD_REQUEST,
                        data={'message_long': 'Too many requests. Please wait a while before sending another account export request.',
                              'error_type': 'throttle_error'})

    mails.send_mail(
        to_addr=settings.SUPPORT_EMAIL,
        mail=mails.REQUEST_EXPORT,
        user=auth.user,
    )
    user.email_last_sent = datetime.datetime.utcnow()
    user.save()
    return {'message': 'Sent account export request'}


@must_be_logged_in
def request_deactivation(auth):
    user = auth.user
    if not throttle_period_expired(user.email_last_sent, settings.SEND_EMAIL_THROTTLE):
        raise HTTPError(http.BAD_REQUEST,
                        data={
                            'message_long': 'Too many requests. Please wait a while before sending another account deactivation request.',
                            'error_type': 'throttle_error'
                        })

    mails.send_mail(
        to_addr=settings.SUPPORT_EMAIL,
        mail=mails.REQUEST_DEACTIVATION,
        user=auth.user,
    )
    user.email_last_sent = datetime.datetime.utcnow()
    user.save()
    return {'message': 'Sent account deactivation request'}


def redirect_to_twitter(twitter_handle):
    """Redirect GET requests for /@TwitterHandle/ to respective the OSF user
    account if it associated with an active account

    :param uid: uid for requested User
    :return: Redirect to User's Twitter account page
    """
    try:
        user = User.find_one(Q('social.twitter', 'iexact', twitter_handle))
    except NoResultsFound:
        raise HTTPError(http.NOT_FOUND, data={
            'message_short': 'User Not Found',
            'message_long': 'There is no active user associated with the Twitter handle: {0}.'.format(twitter_handle)
        })
    except MultipleResultsFound:
        users = User.find(Q('social.twitter', 'iexact', twitter_handle))
        message_long = 'There are multiple OSF accounts associated with the ' \
                       'Twitter handle: <strong>{0}</strong>. <br /> Please ' \
                       'select from the accounts below. <br /><ul>'.format(markupsafe.escape(twitter_handle))
        for user in users:
            message_long += '<li><a href="{0}">{1}</a></li>'.format(user.url, markupsafe.escape(user.fullname))
        message_long += '</ul>'
        raise HTTPError(http.MULTIPLE_CHOICES, data={
            'message_short': 'Multiple Users Found',
            'message_long': message_long
        })

    return redirect(user.url)
