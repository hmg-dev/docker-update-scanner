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
import requests
from mockito import mock, when, unstub, ANY, verify
from dus.project.parent_image_details import ParentImage


class ParentImageTest(unittest.TestCase):

    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.dummy_name_tag = "ubuntu:18.04"
        self.sut = ParentImage()
        self.dummy_response = '{"creator":1156886,"id":18189966,"image_id":null,"images":[{"architecture":"amd64",' \
                              '"features":"","variant":null,' \
                              '"digest":"sha256:b58746c8a89938b8c9f5b77de3b8cf1fe78210c696ab03a1442e235eea65d84f",' \
                              '"os":"linux","os_features":"","os_version":null,"size":26726177},' \
                              '{"architecture":"ppc64le","features":"","variant":null,' \
                              '"digest":"sha256:43d4ac7d7f07cb5e0558b2f95a9f493cf8c85e36b048473c67c9eeaffe7a5e64",' \
                              '"os":"linux","os_features":"","os_version":null,"size":30436536},' \
                              '{"architecture":"386","features":"","variant":null,' \
                              '"digest":"sha256:15db3648b32edb76770d0e0297099ce7bfb5f14a3eeaa19d252c82dcb6d155d9",' \
                              '"os":"linux","os_features":"","os_version":null,"size":27158701},' \
                              '{"architecture":"s390x","features":"","variant":null,' \
                              '"digest":"sha256:a69390df0911533dd2fc552a8765481bf6a93b5d5952a9ddbe9cb64ca3479e17",' \
                              '"os":"linux","os_features":"","os_version":null,"size":25402547},' \
                              '{"architecture":"arm","features":"","variant":"v7",' \
                              '"digest":"sha256:214d66c966334f0223b036c1e56d9794bc18b71dd20d90abb28d838a5e7fe7f1",' \
                              '"os":"linux","os_features":"","os_version":null,"size":22312750},' \
                              '{"architecture":"arm64","features":"","variant":"v8",' \
                              '"digest":"sha256:03e4a3b262fd97281d7290c366cae028e194ae90931bc907991444d026d6392a",' \
                              '"os":"linux","os_features":"","os_version":null,"size":23756636}],' \
                              '"last_updated":"2020-04-24T01:30:34.54497Z","last_updater":1156886,' \
                              '"last_updater_username":"doijanky","name":"18.04","repository":130,' \
                              '"full_size":26726177,"v2":true} '

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        unstub()

    def test_determine_last_updatedate(self):
        expected_uri = "https://hub.docker.com/v2/repositories/library/ubuntu/tags/18.04"
        response = mock({
            "status_code": 200,
            "text": self.dummy_response
        }, spec=requests.Response)
        when(requests).get(ANY(str)).thenReturn(response)

        result = self.sut.determine_last_updatedate(self.dummy_name_tag)
        self.assertIsNotNone(result)
        self.assertEqual("2020-04-24T01:30:34.54497Z", result)

        result = self.sut.determine_last_updatedate(self.dummy_name_tag)
        self.assertIsNotNone(result)
        self.assertEqual("2020-04-24T01:30:34.54497Z", result)

        verify(requests, times=1).get(expected_uri)

    def test_determine_last_updatedate_for_non_official_image(self):
        dummy_name_tag = "jwilder/nginx-proxy:0.4.0"
        expected_uri = "https://hub.docker.com/v2/repositories/jwilder/nginx-proxy/tags/0.4.0"
        response = mock({
            "status_code": 200,
            "text": self.dummy_response
        }, spec=requests.Response)
        when(requests).get(ANY(str)).thenReturn(response)

        result = self.sut.determine_last_updatedate(dummy_name_tag)
        self.assertIsNotNone(result)
        self.assertEqual("2020-04-24T01:30:34.54497Z", result)

        verify(requests, times=1).get(expected_uri)

    def test_determine_last_updatedate_for_no_tag_specified(self):
        dummy_name_tag = "jwilder/nginx-proxy"
        expected_uri = "https://hub.docker.com/v2/repositories/jwilder/nginx-proxy/tags/latest"
        response = mock({
            "status_code": 200,
            "text": self.dummy_response
        }, spec=requests.Response)
        when(requests).get(ANY(str)).thenReturn(response)

        result = self.sut.determine_last_updatedate(dummy_name_tag)
        self.assertIsNotNone(result)
        self.assertEqual("2020-04-24T01:30:34.54497Z", result)

        verify(requests, times=1).get(expected_uri)

    def test_is_public_image(self):
        self.assertTrue(self.sut.is_public_image("jwilder/nginx-proxy:0.4.0"))
        self.assertTrue(self.sut.is_public_image("jwilder/nginx-proxy"))
        self.assertTrue(self.sut.is_public_image("ubuntu:18.04"))
        self.assertFalse(self.sut.is_public_image("orgprj.azurecr.io/prj-infra-dummy:7.7"))
        self.assertFalse(self.sut.is_public_image("orgprj2.azurecr.io/prj-dummynarf:20200419.1"))


if __name__ == '__main__':
    unittest.main()
