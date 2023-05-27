########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import abc


class AgentInstaller(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, cloudify_agent):
        self.cloudify_agent = cloudify_agent

    @property
    def agent_name(self):
        return self.cloudify_agent['name']

    @property
    def agent_queue(self):
        return self.cloudify_agent['queue']

    @abc.abstractmethod
    def create(self):
        pass

    @abc.abstractmethod
    def configure(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    def restart(self):
        pass
