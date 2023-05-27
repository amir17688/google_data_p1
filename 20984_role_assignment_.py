# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class RoleAssignmentPropertiesWithScope(Model):
    """
    Role assignment properties with scope.

    :param scope: Gets or sets role assignment scope.
    :type scope: str
    :param role_definition_id: Gets or sets role definition id.
    :type role_definition_id: str
    :param principal_id: Gets or sets principal Id.
    :type principal_id: str
    """ 

    _attribute_map = {
        'scope': {'key': 'scope', 'type': 'str'},
        'role_definition_id': {'key': 'roleDefinitionId', 'type': 'str'},
        'principal_id': {'key': 'principalId', 'type': 'str'},
    }

    def __init__(self, scope=None, role_definition_id=None, principal_id=None):
        self.scope = scope
        self.role_definition_id = role_definition_id
        self.principal_id = principal_id
