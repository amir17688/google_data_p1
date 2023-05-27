# Copyright 2013 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from django.conf import settings
from django.contrib.auth import get_user_model, SESSION_KEY
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36
from django.utils.text import capfirst
from sky_visitor.models import InvitedUser
from sky_visitor.forms import InvitationCompleteForm
from sky_visitor.tests import SkyVisitorTestCase


FIXTURE_USER_DATA = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'adminadmin'
}


class SkyVisitorViewsTestCase(SkyVisitorTestCase):

    @property
    def default_user(self):
        UserModel = get_user_model()
        if not hasattr(self, '_default_user'):
            self._default_user = UserModel._default_manager.get(email=FIXTURE_USER_DATA['email'])
        return self._default_user

    def login(self, password=FIXTURE_USER_DATA['password']):
        UserModel = get_user_model()
        response = self.client.post('/user/login/', {
            'username': FIXTURE_USER_DATA[UserModel.USERNAME_FIELD],
            'password': password,
        })
        self.assertRedirected(response, settings.LOGIN_REDIRECT_URL)
        self.assertTrue(SESSION_KEY in self.client.session)


class RegisterUserMixin(object):

    def get_register_user_data(self):
        data = {
            'username': 'registeruser',
            'password1': 'password',
            'password2': 'password',
        }
        return data


class RegisterViewTest(RegisterUserMixin, SkyVisitorViewsTestCase):
    view_url = '/user/register/'

    def test_register_view_exists(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_registration_should_succeed(self):
        UserModel = get_user_model()
        data = self.get_register_user_data()
        testuser_username = data[UserModel.USERNAME_FIELD]
        response = self.client.post(self.view_url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirects(response, '/')
        # Lookup the user based on the username field and the value in the test data
        self.assertEqual(UserModel._default_manager.filter(**{UserModel.USERNAME_FIELD: testuser_username}).count(), 1)

    def test_registration_should_fail_on_mismatched_password(self):
        data = self.get_register_user_data()
        data['password2'] = 'mismatch'
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        # Form should have errors for mismatched password
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)


class LoginViewTest(SkyVisitorViewsTestCase):
    view_url = '/user/login/'

    def test_login_form_should_exist(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    def test_login_form_should_succeed(self):
        UserModel = get_user_model()
        data = {
            # Always use username as the field name because that's how contrib.auth.forms.AuthenticationForm is built
            'username': FIXTURE_USER_DATA[UserModel.USERNAME_FIELD],
            'password': FIXTURE_USER_DATA['password'],
        }
        response = self.client.post(self.view_url, data)
        # Should redirect
        self.assertRedirected(response, '/')

        # Should be logged in
        user = UserModel._default_manager.get(**{UserModel.USERNAME_FIELD: FIXTURE_USER_DATA[UserModel.USERNAME_FIELD]})
        self.assertLoggedIn(user, backend='django.contrib.auth.backends.ModelBackend')

    def test_should_have_username_field(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        UserModel = get_user_model()
        username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        self.assertEqual(form.fields['username'].label, capfirst(username_field.verbose_name))


class LogoutViewTest(SkyVisitorViewsTestCase):

    def confirm_logged_out(self):
        self.assertTrue(SESSION_KEY not in self.client.session)

    def test_logout_default(self):
        self.login()
        response = self.client.get('/user/logout/')
        self.assertRedirected(response, '/user/login/')
        self.confirm_logged_out()

    def test_logout_with_overridden_redirect_url(self):
        self.login()
        response = self.client.get('/user/logout/?next=/user/register/')
        self.assertRedirected(response, '/user/register/')
        self.confirm_logged_out()

    def test_redirect_view_override_url(self):
        self.login()
        response = self.client.get('/customlogout/')
        self.assertRedirected(response, '/user/register/')
        self.confirm_logged_out()


class ForgotPasswordProcessTest(SkyVisitorViewsTestCase):

    # TODO TEST: Token older than X weeks (will require removing hard coded reset URL)

    def _get_password_reset_url(self, user=None, with_host=True):
        if user is None:
            user = self.default_user
        url = reverse('reset_password', kwargs={'uidb36': int_to_base36(user.id), 'token': default_token_generator.make_token(user)})
        if with_host:
            url = 'http://testserver%s' % url
        return url

    def test_forgot_password_form_should_send_email(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': FIXTURE_USER_DATA['email']}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        # Should redirect to the check email page
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        # Should send the message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # Should be sent to the right person
        self.assertIn(data['email'], message.to)
        # Should have the correct subject
        self.assertEqual(message.subject, 'Password reset for testserver')
        # Should have the link in the body of the message
        self.assertIn(self._get_password_reset_url(), message.body)
        # Link in email should work and land you on a set password form
        response2 = self.client.get(self._get_password_reset_url())
        self.assertIsInstance(response2.context_data['form'], SetPasswordForm)

    def test_reset_password_form_should_success_with_valid_input(self):
        UserModel = get_user_model()
        response = self.client.get(self._get_password_reset_url())
        # Should succeed and have the appropraite form on the page
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], SetPasswordForm)

        new_pass = 'asdfasdf'
        data = {
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(self._get_password_reset_url(), data)
        user = UserModel._default_manager.get(email=FIXTURE_USER_DATA['email'])
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirected(response, '/')
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertLoggedIn(user, backend='sky_visitor.backends.BaseBackend')

        # Now log the user out and make sure that reset link doesn't work anymore
        self.client.logout()
        response2 = self.client.get(self._get_password_reset_url(), follow=True)
        self.assertRedirects(response2, '/user/login/')

    def test_reset_password_form_should_fail_with_invalid_token(self):
        # Should work fine for normal URL
        response = self.client.get(self._get_password_reset_url())
        self.assertEqual(response.status_code, 200)
        # User ID of this token is modified
        response = self.client.get('/user/forgot_password/2-35t-d4e092280eb134000672/', follow=True)
        self.assertRedirects(response, '/user/login/')
        # Token modified
        response = self.client.get('/user/forgot_password/1-35t-d4e092280eb134000671/', follow=True)
        self.assertRedirects(response, '/user/login/')


class ChangePasswordViewTest(SkyVisitorViewsTestCase):
    view_url = '/user/change_password/'

    def test_view_should_exist(self):
        self.login()
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIn('old_password', form.fields)

    def test_change_password(self):
        self.login()
        newpass = 'newnewnew'
        data = {
            'old_password': FIXTURE_USER_DATA['password'],
            'new_password1': newpass,
            'new_password2': newpass,
        }
        response = self.client.post(self.view_url, data, follow=True)
        form = response.context_data['form']
        self.assertRedirects(response, self.view_url)

    def test_bad_old_password_failed(self):
        self.login()
        newpass = 'newnewnew'
        data = {
            'old_password': 'badoldpass',
            'new_password1': newpass,
            'new_password2': newpass,
        }
        response = self.client.post(self.view_url, data, follow=True)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)

    def test_mismatched_passwords_fail(self):
        self.login()
        newpass = 'newnewnew'
        data = {
            'old_password': FIXTURE_USER_DATA['password'],
            'new_password1': newpass,
            'new_password2': 'mismatch',
        }
        response = self.client.post(self.view_url, data, follow=True)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)


class InvitationProcessTest(RegisterUserMixin, SkyVisitorViewsTestCase):
    view_url = '/user/invitation/'
    invited_user_email = 'invited@example.com'

    def _get_invitation_complete_url(self, user=None, with_host=True):
        url = reverse('invitation_complete', kwargs={'uidb36': int_to_base36(user.id), 'token': default_token_generator.make_token(user)})
        if with_host:
            url = 'http://testserver%s' % url
        return url

    def test_view_should_exist(self):
        self.login()
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIn('email', form.fields)

    def _invite_user(self):
        data = {
            'email': self.invited_user_email
        }
        response = self.client.post(self.view_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Should create an InvitedUser
        invited_user = InvitedUser.objects.get(email=self.invited_user_email)
        self.assertIsNotNone(invited_user)
        return invited_user

    def test_should_invite_user(self):
        invited_user = self._invite_user()

        # Should send the message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # Should be sent to the right person
        self.assertIn(self.invited_user_email, message.to)
        # Should have the correct subject
        self.assertEqual(message.subject, "Invitation to Create Account at testserver")
        invitation_complete_url = self._get_invitation_complete_url(invited_user)
        # Should have the link in the body of the message
        self.assertIn(invitation_complete_url, message.body)
        # Link in email should work and land you on an invitation complete form
        response2 = self.client.get(invitation_complete_url)
        self.assertIsInstance(response2.context_data['form'], InvitationCompleteForm)

    def test_should_not_allow_duplicate_invitation(self):
        data = {
            'email': self.invited_user_email
        }
        response = self.client.post(self.view_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Post again with same data
        response = self.client.post(self.view_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)

    def test_should_not_allow_normal_user_to_be_invited(self):
        # Try to invite the user in the fixture data, since we know it's already an entry in the normal user table
        data = {
            'email': FIXTURE_USER_DATA['email']
        }
        response = self.client.post(self.view_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'], ["User with this email already exists."])

    def test_should_complete_invitation_registration_from(self):
        invited_user = self._invite_user()

        UserModel = get_user_model()
        invitation_complete_url = self._get_invitation_complete_url(invited_user)
        data = self.get_register_user_data()
        data['email'] = self.invited_user_email
        testuser_username = data[UserModel.USERNAME_FIELD]
        response = self.client.post(invitation_complete_url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirects(response, '/')
        # Lookup the user based on the username field and the value in the test data
        user_qs = UserModel._default_manager.filter(**{UserModel.USERNAME_FIELD: testuser_username})
        self.assertEqual(user_qs.count(), 1)
        user = user_qs.get()
        # Make sure the InvitedUser points to the newly created user
        invited_user_updated = InvitedUser.objects.get(email=invited_user.email)
        self.assertEqual(invited_user_updated.created_user.id, user.id)
        self.assertEqual(invited_user_updated.status, InvitedUser.STATUS_REGISTERED)
