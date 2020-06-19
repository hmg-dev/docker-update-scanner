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
from datetime import datetime
from mockito import mock, when, unstub, ANY, eq, verify, verifyZeroInteractions

from dus.project.parent_image_details import ParentImage
from dus.acr.azure_rest import DockerImageDetails
from dus.project.repo_details import RepoDetails
from dus.project import data_fetcher as sut
from dus import config as conf


class DataFetcherTest(unittest.TestCase):
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.max_age_days_orig = conf.max_age_days
        self.dummy_image_name = "infra-dummyimage"
        self.dummy_repo = {
            "name": "infra-docker-dummyrepo",
            "git": "https://user@dev.azure.com/organization/PRJ/_git/infra-docker-dummyrepo",
            "acr": "orgdummy",
            "build_pipeline": "infra-docker-dummyrepo",
            "project": "PRJ"
        }

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        conf.max_age_days = self.max_age_days_orig
        unstub()

    def test_determine_stats(self):
        dummy_git_repo = "/data/DUS/infra-docker-dummyrepo"
        dummy_latest_tag = {"lastUpdateTime": "2020-03-12T10:11:56.603Z"}
        dummy_parent_image = "ubuntu:18.04"
        dummy_pi_last_update = "2020-04-11T09:18:46.603Z"  # newer than dummy_latest_tag

        when(RepoDetails).determine_imagename(ANY(str)).thenReturn(self.dummy_image_name)
        when(DockerImageDetails).az_latest_tag().thenReturn(dummy_latest_tag)
        when(RepoDetails).determine_parent_image(ANY(str)).thenReturn(dummy_parent_image)
        when(sut).determine_last_updatedate(ANY(str), ANY(str)).thenReturn(dummy_pi_last_update)
        when(sut).is_outdated(ANY(str), ANY(datetime), repo=ANY).thenReturn(True)

        stats = sut.determine_stats(self.dummy_repo, dummy_git_repo)

        self.assertIsNotNone(stats)
        self.assertEqual(dummy_latest_tag, stats["tag"])
        self.assertEqual(self.dummy_image_name, stats["image_name"])
        self.assertEqual(dummy_parent_image, stats["parent_image"])
        self.assertEqual(dummy_pi_last_update, stats["parent_last_update"])
        self.assertTrue(stats["update_required"])
        self.assertTrue(stats["outdated_parent"])

        verify(RepoDetails, times=1).determine_imagename(dummy_git_repo)
        verify(DockerImageDetails, times=1).az_latest_tag()
        verify(RepoDetails, times=1).determine_parent_image(dummy_git_repo)
        verify(sut, times=1).determine_last_updatedate(dummy_parent_image, dummy_git_repo)
        verify(sut, times=1).is_outdated(eq(dummy_pi_last_update), ANY(datetime), repo=eq(self.dummy_repo))

    def test_is_outdated_for_uptodate_image(self):
        conf.max_age_days = 90
        dummy_image_last_update = "2020-04-11T09:18:46.603Z"
        dummy_reference_time = datetime.strptime("2020-05-10T19:18:46", sut.DATETIME_FORMAT)

        result = sut.is_outdated(dummy_image_last_update, dummy_reference_time, repo={"name": "No whitelist"})
        self.assertFalse(result)

    def test_is_outdated_for_abandoned_image(self):
        conf.max_age_days = 30
        dummy_image_last_update = "2020-03-11T09:18:46.603Z"
        dummy_reference_time = datetime.strptime("2020-05-10T19:18:46", sut.DATETIME_FORMAT)

        result = sut.is_outdated(dummy_image_last_update, dummy_reference_time)
        self.assertTrue(result)

    def test_is_outdated_for_whitelisted_image(self):
        conf.max_age_days = 30
        dummy_repo = {"name": "dummy", "outdate_whitelist": True}
        dummy_image_last_update = "2020-03-11T09:18:46.603Z"
        dummy_reference_time = datetime.strptime("2020-05-10T19:18:46", sut.DATETIME_FORMAT)

        result = sut.is_outdated(dummy_image_last_update, dummy_reference_time, repo=dummy_repo)
        self.assertFalse(result)

    def test_is_require_update(self):
        dummy_dt1 = "2020-03-12T10:11:56.603Z"
        dummy_dt1_with_ns = "2020-03-12T10:11:56.6034538Z"  # nanoseconds -> 7 digits after dot, instead of max 6
        dummy_dt2 = "2020-04-11T09:18:46.603Z"

        self.assertTrue(sut.is_require_update(dummy_dt1, dummy_dt2))
        self.assertTrue(sut.is_require_update(dummy_dt1_with_ns, dummy_dt2))
        self.assertFalse(sut.is_require_update(dummy_dt2, dummy_dt1))
        self.assertFalse(sut.is_require_update(dummy_dt2, dummy_dt2))

    def test_determine_last_updatedate_for_public_image(self):
        expected_result = "2020-03-12T10:11:56.603Z"
        dummy_parent_image = "ubuntu:18.04"

        when(DockerImageDetails)
        when(RepoDetails)
        when(ParentImage).is_public_image(ANY(str)).thenReturn(True)
        when(ParentImage).determine_last_updatedate(ANY(str)).thenReturn(expected_result)

        result = sut.determine_last_updatedate(dummy_parent_image, "")
        self.assertEqual(expected_result, result)

        verify(ParentImage, times=1).is_public_image(dummy_parent_image)
        verify(ParentImage, times=1).determine_last_updatedate(dummy_parent_image)
        verifyZeroInteractions(DockerImageDetails)
        verifyZeroInteractions(RepoDetails)

    def test_determine_last_updatedate_for_private_image_with_static_version(self):
        expected_result = "2020-03-12T10:11:56.603Z"
        expected_json = {"lastUpdateTime": expected_result}
        dummy_parent_image = "orgdummy.azurecr.io/prj-infra-dummy:7.7"
        dummy_details = mock(DockerImageDetails)

        when(DockerImageDetails).from_FQDIN(ANY(str)).thenReturn(dummy_details)
        when(dummy_details).az_image_tag_details().thenReturn(expected_json)
        when(RepoDetails)
        when(ParentImage).is_public_image(ANY(str)).thenReturn(False)
        when(ParentImage).determine_last_updatedate(ANY(str)).thenReturn(expected_result)

        result = sut.determine_last_updatedate(dummy_parent_image, "")
        self.assertEqual(expected_result, result)

        verify(ParentImage, times=1).is_public_image(dummy_parent_image)
        verify(ParentImage, times=0).determine_last_updatedate(ANY(str))
        verify(DockerImageDetails, times=1).from_FQDIN(dummy_parent_image)
        verify(dummy_details, times=1).az_image_tag_details()
        verifyZeroInteractions(RepoDetails)

    def test_determine_last_updatedate_for_private_image_with_dyn_version(self):
        expected_result = "2020-03-12T10:11:56.603Z"
        expected_json = {"lastUpdateTime": expected_result}
        dummy_parent_image = "orgdummy.azurecr.io/prj-infra-dummy:$VERSION"
        expected_parent_image = "orgdummy.azurecr.io/prj-infra-dummy"
        dummy_details = mock(DockerImageDetails)
        dummy_git_repo = "https://user@dev.azure.com/organization/PRJ/_git/prj-infra-dummy"
        dummy_real_tag = "7.6"

        when(DockerImageDetails).from_FQDIN(ANY(str), default_tag=ANY(str)).thenReturn(dummy_details)
        when(dummy_details).az_image_tag_details().thenReturn(expected_json)
        when(RepoDetails).determine_imageversion(dummy_git_repo).thenReturn(dummy_real_tag)
        when(ParentImage).is_public_image(ANY(str)).thenReturn(False)
        when(ParentImage).determine_last_updatedate(ANY(str)).thenReturn(expected_result)

        result = sut.determine_last_updatedate(dummy_parent_image, dummy_git_repo)
        self.assertEqual(expected_result, result)

        verify(ParentImage, times=1).is_public_image(dummy_parent_image)
        verify(ParentImage, times=0).determine_last_updatedate(ANY(str))
        verify(DockerImageDetails, times=1).from_FQDIN(expected_parent_image, default_tag=dummy_real_tag)
        verify(dummy_details, times=1).az_image_tag_details()
        verify(RepoDetails, times=1).determine_imageversion(dummy_git_repo)


if __name__ == '__main__':
    unittest.main()
