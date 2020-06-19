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

import requests
import json


class ParentImage(object):
    def __init__(self):
        self.parent_image_cache = {}

    def determine_last_updatedate(self, name_and_tag):
        if name_and_tag in self.parent_image_cache:
            return self.parent_image_cache.get(name_and_tag)

        url = self._build_request_uri(name_and_tag)
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Request to '{url}' failed! Got status code: {response.status_code}")

        json_data = json.loads(response.text)

        self.parent_image_cache[name_and_tag] = json_data["last_updated"]

        return self.parent_image_cache.get(name_and_tag)

    @staticmethod
    def _build_request_uri(name_and_tag):
        name_tag_parts = name_and_tag.split(":")
        sub_path = name_tag_parts[0]
        tag = "latest" if len(name_tag_parts) <= 1 else name_tag_parts[1]
        if "/" not in sub_path:  # TODO: check for acr (own parents)
            sub_path = "library/" + sub_path

        return f"https://hub.docker.com/v2/repositories/{sub_path}/tags/{tag}"

    @staticmethod
    def is_public_image(name_and_tag):
        return "azurecr.io/" not in name_and_tag
