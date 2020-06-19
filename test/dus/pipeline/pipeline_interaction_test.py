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
import unittest
import requests
from mockito import mock, when, unstub, ANY, verify
from dus.pipeline.pipeline_interaction import Pipeline
from dus import config as conf


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.dummy_project = "PRJ"
        self.dummy_pipeline_name = "build-dummy-pipeline"
        self.sut = Pipeline(self.dummy_project, self.dummy_pipeline_name)
        self.dummy_azure_pat = "totalgeheim"
        self.expected_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.expected_credentials = (conf.git_user, self.dummy_azure_pat)
        when(os).getenv("DEVOPS_PAT").thenReturn(self.dummy_azure_pat)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        unstub()

    def test_validate_pipeline_for_invalid_name(self):
        expected_url = f"{conf.azure_org}{self.dummy_project}/_apis/build/definitions?api-version=5.1&name={self.dummy_pipeline_name}"
        dummy_result = "{\"count\":0,\"value\":[]}"
        response = mock({"status_code": 200, "text": dummy_result}, spec=requests.Response)
        when(requests).get(ANY(), headers=ANY(), auth=ANY()).thenReturn(response)

        result = self.sut.validate()
        self.assertIsNone(result)

        verify(requests, times=1).get(expected_url, headers=self.expected_headers, auth=self.expected_credentials)
        verify(os, times=1).getenv("DEVOPS_PAT")

    def test_validate_pipeline_for_valid_name(self):
        expected_url = conf.azure_org + self.dummy_project + \
                       "/_apis/build/definitions?api-version=5.1&name=" + self.dummy_pipeline_name
        with open(os.path.dirname(__file__) + "/../resources/pipeline_details.json", 'r') as f:
            dummy_response = f.read()

        response = mock({"status_code": 200, "text": dummy_response}, spec=requests.Response)
        when(requests).get(ANY(), headers=ANY(), auth=ANY()).thenReturn(response)

        result = self.sut.validate()
        self.assertIsNotNone(result)
        self.assertEqual(91, result["id"])
        self.assertEqual("infra-docker-dummy", result["name"])

        verify(requests, times=1).get(expected_url, headers=self.expected_headers, auth=self.expected_credentials)
        verify(os, times=1).getenv("DEVOPS_PAT")

    def test_trigger_build_pipeline(self):
        dummy_pipeline_id = 42
        expected_url = conf.azure_org + self.dummy_project + "/_apis/build/builds?api-version=5.1"
        expected_data = "{\"definition\": {\"id\": " + str(dummy_pipeline_id) + "}}"

        with open(os.path.dirname(__file__) + "/../resources/pipeline_queue_result.json", 'r') as f:
            dummy_response = f.read()

        response = mock({"status_code": 200, "text": dummy_response}, spec=requests.Response)
        when(requests).post(ANY(), data=ANY(), headers=ANY(), auth=ANY()).thenReturn(response)

        result = self.sut.trigger_build(dummy_pipeline_id)
        self.assertIsNotNone(result)
        self.assertEqual(26624, result["id"])
        self.assertEqual("notStarted", result["status"])
        self.assertEqual("20200512.1", result["buildNumber"])

        verify(requests, times=1).post(expected_url, data=expected_data, headers=self.expected_headers,
                                      auth=self.expected_credentials)
        verify(os, times=1).getenv("DEVOPS_PAT")


if __name__ == '__main__':
    unittest.main()
