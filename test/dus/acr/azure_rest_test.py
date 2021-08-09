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

import unittest
import os
import requests
from mockito import mock, when, unstub, ANY, verify
from dus.acr import azure_rest


class AzureRestTest(unittest.TestCase):
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.dummy_acr = "orgprj"
        self.dummy_img = "prj-infra-dummy"
        self.dummy_tag = "3.7"
        self.dummy_passwd = "NARF"
        self.expected_headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        unstub()

    def test_az_latest_tag(self):
        expected_url = f"https://{self.dummy_acr}.azurecr.io/acr/v1/{self.dummy_img}/_tags?n=500"
        expected_credentials = (self.dummy_acr, self.dummy_passwd)
        with open(os.path.dirname(__file__) + "/../resources/acr_tags.json", 'r') as f:
            dummy_response = f.read()

        response = mock({
            "status_code": 200, "text": dummy_response
        }, spec=requests.Response)

        when(os).getenv(f"ACR_PASSWD_{self.dummy_acr}").thenReturn(self.dummy_passwd)
        when(requests).get(ANY(), headers=ANY(), auth=ANY()).thenReturn(response)

        did = azure_rest.DockerImageDetails(self.dummy_acr, self.dummy_img)
        result = did.az_latest_tag()

        self.assertIsNotNone(result)
        self.assertEqual("20200505.4", result["name"])
        self.assertEqual("2020-05-05T10:11:44.1997799Z", result["lastUpdateTime"])

        verify(requests, times=1).get(expected_url, headers=self.expected_headers, auth=expected_credentials)
        verify(os, times=1).getenv(f"ACR_PASSWD_{self.dummy_acr}")

    def test_az_image_tag_details(self):
        expected_url = f"https://{self.dummy_acr}.azurecr.io/acr/v1/{self.dummy_img}/_tags/{self.dummy_tag}"
        expected_credentials = (self.dummy_acr, self.dummy_passwd)
        dummy_response = self._tag_details_dummy_response()
        full_image_name = f"{self.dummy_acr}.azurecr.io/{self.dummy_img}:{self.dummy_tag}"

        response = mock({
            "status_code": 200, "text": dummy_response
        }, spec=requests.Response)

        when(os).getenv(f"ACR_PASSWD_{self.dummy_acr}").thenReturn(self.dummy_passwd)
        when(requests).get(ANY(), headers=ANY(), auth=ANY()).thenReturn(response)

        did = azure_rest.DockerImageDetails.from_FQDIN(full_image_name)
        result = did.az_image_tag_details()

        self.assertIsNotNone(result)
        self.assertEqual(self.dummy_tag, result["name"])
        self.assertEqual("2020-05-05T10:11:44.1997799Z", result["lastUpdateTime"])

        verify(requests, times=1).get(expected_url, headers=self.expected_headers, auth=expected_credentials)
        verify(os, times=1).getenv(f"ACR_PASSWD_{self.dummy_acr}")

    def _tag_details_dummy_response(self):
        return "{\"registry\":\"orgprj.azurecr.io\",\"imageName\":\"prj-infra-dummy\"," \
               "\"tag\":{\"name\":\"" + self.dummy_tag + '\",' \
               "\"digest\":\"sha256:5e6790a35bf8eaf185d0fffd0e951b3f17c16631172fd74603ba3f54160bbc70\"," \
               "\"createdTime\":\"2020-05-05T10:11:44.1997799Z\",\"lastUpdateTime\":\"2020-05-05T10:11:44.1997799Z\"," \
               "\"signed\":false,\"changeableAttributes\":{\"deleteEnabled\":true,\"writeEnabled\":true," \
               "\"readEnabled\":true,\"listEnabled\":true}}}"


if __name__ == '__main__':
    unittest.main()
