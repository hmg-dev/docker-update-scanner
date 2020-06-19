# Copyright (C) 2020, Martin Drößler <m.droessler@handelsblattgroup.com>
# Copyright (C) 2020, Handelsblatt GmbH
#
# This file is part of Docker-Update-Scanner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class AzureException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occurred"
        super(AzureException, self).__init__(msg)


class AzureAuthenticationException(AzureException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Error during authentication"
        super(AzureException, self).__init__(msg)


class AzureContainerRegistryException(AzureException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Error during operation with ACR"
        super(AzureException, self).__init__(msg)
