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
from django.core.urlresolvers import reverse
from sky_visitor import views as sky_visitor_views


class CustomLogoutView(sky_visitor_views.LogoutView):
    # View to allow testing of overriden URL attribute
    redirect_url_overrides_redirect_field = True
    url = '/user/register/'


class CustomInvitationCompleteView(sky_visitor_views.InvitationCompleteView):

    def get_success_url(self):
        return reverse('home')
