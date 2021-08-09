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

import os
import json
import requests
from datetime import datetime

ENV_ACR_PREFIX = "ACR_PASSWD_"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json"}


class DockerImageDetails(object):
    DEFAULT_AZ_SUBSCRIPTION = "hmg-services"

    def __init__(self, acr, image_name, tag=""):
        self.acr = acr
        self.image_name = image_name
        self.tag = tag

    @classmethod
    def from_FQDIN(cls, fq_docker_imge_name, default_tag="latest"):
        acr = fq_docker_imge_name.split(".", 1)[0]
        name_and_tag = fq_docker_imge_name.split("/")[1]
        parts = name_and_tag.split(":")
        name = parts[0]
        tag = default_tag if len(parts) <= 1 else parts[1]

        return cls(acr, name, tag=tag)

    def az_latest_tag(self):
        url = f"https://{self.acr}.azurecr.io/acr/v1/{self.image_name}/_tags?n=500"
        credentials = (self.acr, os.getenv(ENV_ACR_PREFIX + self.acr))

        response = requests.get(url, headers=HEADERS_JSON, auth=credentials)
        if response.status_code != 200:
            raise RuntimeError(f"Request to '{url}' failed! Got status code: {response.status_code}")

        data = json.loads(response.text)
        tags = data["tags"]
        tags.sort(reverse=True, key=lambda t: datetime.strptime(t["lastUpdateTime"].rsplit('.')[0], DATETIME_FORMAT))

        return tags[0]

    def az_image_tag_details(self):
        url = f"https://{self.acr}.azurecr.io/acr/v1/{self.image_name}/_tags/{self.tag}"
        credentials = (self.acr, os.getenv(ENV_ACR_PREFIX + self.acr))

        response = requests.get(url, headers=HEADERS_JSON, auth=credentials)
        if response.status_code != 200:
            raise RuntimeError(f"Request to '{url}' failed! Got status code: {response.status_code}")

        data = json.loads(response.text)
        return data["tag"]
