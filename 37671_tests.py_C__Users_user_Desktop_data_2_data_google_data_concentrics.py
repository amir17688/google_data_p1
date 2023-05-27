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

from django.contrib.auth import get_user_model
from normal_tests import tests as normaltests


class RegisterUserMixin(normaltests.RegisterUserMixin):

    def get_register_user_data(self):
        data = {
            'email': 'registeruser@example.com',
            'date_of_birth': '1976-11-08',
            'password1': 'password',
            'password2': 'password',
        }
        return data


class RegisterViewTest(RegisterUserMixin, normaltests.RegisterViewTest):

    def test_registration_should_fail_on_duplicate_email(self):
        UserModel = get_user_model()
        testuser_email = 'testuser1@example.com'
        data1 = self.get_register_user_data()
        data1['email'] = testuser_email
        response1 = self.client.post(self.view_url, data=data1, follow=True)
        self.assertEqual(response1.status_code, 200)
        # Test user should exist
        self.assertEqual(UserModel._default_manager.filter(**{UserModel.USERNAME_FIELD: testuser_email}).count(), 1)

        data2 = data1
        response2 = self.client.post(self.view_url, data=data2, follow=True)
        self.assertEqual(response2.status_code, 200)
        form = response2.context_data['form']
        # Form should have errors for the duplicate email
        self.assertEqual(len(form.errors), 1)
        self.assertIn('email', form.errors)

        # Test user should only be in the database one time
        self.assertEqual(UserModel._default_manager.filter(**{UserModel.USERNAME_FIELD: testuser_email}).count(), 1)


class LoginViewTest(normaltests.LoginViewTest):
    pass


class LogoutViewTest(normaltests.LogoutViewTest):
    pass


class ForgotPasswordProcessTest(normaltests.ForgotPasswordProcessTest):
    pass


class ChangePasswordViewTest(normaltests.ChangePasswordViewTest):
    pass


class InvitationProcessTest(RegisterUserMixin, normaltests.InvitationProcessTest):
    pass