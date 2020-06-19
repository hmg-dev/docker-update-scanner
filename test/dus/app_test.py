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
from mockito import when, unstub, ANY, verify

from dus import app
from dus.git.repository_fetcher import RepositoryFetcher
from dus.pipeline.pipeline_interaction import Pipeline
from dus.report import report_writer, report_sender
from dus.project import data_fetcher
from dus import repos


class AppTest(unittest.TestCase):
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.orig_repos = repos.to_check

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        repos.to_check = self.orig_repos
        unstub()

    def test_process_repository(self):
        dummy_repo = {
            "name": "infra-docker-contentengine",
            "git": "https://devops@dev.azure.com/handelsblattgroup/CUE/_git/infra-docker-contentengine",
            "acr": "hmgcue",
            "build_pipeline": "infra-docker-contentengine",
            "project": "CUE"
        }
        dummy_latest_tag = {"lastUpdateTime": "2020-03-12T10:11:56.603Z"}
        dummy_git_repo_path = "/data/DUS/infra-docker-contentengine"
        dummy_image_name = "cue-infra-contentengine"
        dummy_parent_image = "ubuntu:18.04"
        dummy_pi_last_update = "2020-04-11T09:18:46.603Z"  # newer than dummy_latest_tag
        dummy_stats = {"tag": dummy_latest_tag,
            "image_name": dummy_image_name,
            "parent_image": dummy_parent_image,
            "parent_last_update": dummy_pi_last_update,
            "update_required": True}

        when(RepositoryFetcher).clone_or_update_repo().thenReturn(dummy_git_repo_path)
        when(data_fetcher).determine_stats(dummy_repo, dummy_git_repo_path).thenReturn(dummy_stats)
        when(Pipeline).validate().thenReturn({"id": 42, "name": "dummy pipeline"})
        when(Pipeline).trigger_build(ANY())
        when(RepositoryFetcher).cleanup()

        result = app.process_repository(dummy_repo)
        self.assertEqual(0, result)

        verify(RepositoryFetcher, times=1).clone_or_update_repo()
        verify(data_fetcher, times=1).determine_stats(dummy_repo, dummy_git_repo_path)
        verify(Pipeline, times=1).validate()
        verify(Pipeline, times=1).trigger_build(42)
        verify(RepositoryFetcher, times=1).cleanup()

    def test_process_repository_for_no_update_required(self):
        dummy_repo = {
            "name": "infra-docker-contentengine",
            "git": "https://devops@dev.azure.com/handelsblattgroup/CUE/_git/infra-docker-contentengine",
            "acr": "hmgcue",
            "build_pipeline": "infra-docker-contentengine",
            "project": "CUE"
        }
        dummy_latest_tag = {"lastUpdateTime": "2020-03-12T10:11:56.603Z"}
        dummy_git_repo_path = "/data/DUS/infra-docker-contentengine"
        dummy_image_name = "cue-infra-contentengine"
        dummy_parent_image = "ubuntu:18.04"
        dummy_pi_last_update = "2020-02-11T09:18:46.603Z"  # older than dummy_latest_tag
        dummy_stats = {"tag": dummy_latest_tag,
            "image_name": dummy_image_name,
            "parent_image": dummy_parent_image,
            "parent_last_update": dummy_pi_last_update,
            "update_required": False}

        when(RepositoryFetcher).clone_or_update_repo().thenReturn(dummy_git_repo_path)
        when(data_fetcher).determine_stats(dummy_repo, dummy_git_repo_path).thenReturn(dummy_stats)
        when(Pipeline).validate()
        when(Pipeline).trigger_build(ANY())
        when(RepositoryFetcher).cleanup()

        result = app.process_repository(dummy_repo)
        self.assertEqual(0, result)

        verify(RepositoryFetcher, times=1).clone_or_update_repo()
        verify(data_fetcher, times=1).determine_stats(dummy_repo, dummy_git_repo_path)
        verify(Pipeline, times=0).validate()
        verify(Pipeline, times=0).trigger_build()
        verify(RepositoryFetcher, times=1).cleanup()

    def test_main(self):
        repos.to_check = self._dummy_repos()

        when(app).process_repository(ANY()).thenReturn(0)
        when(report_writer).generate_report_page(ANY(), ANY())
        when(report_sender).send_report()

        app.main()

        verify(app, times=3).process_repository(ANY())
        verify(report_writer, times=1).generate_report_page(ANY(), ANY())
        verify(report_sender, times=1).send_report()

    @staticmethod
    def _dummy_repos():
        return {
            "dummy_repo1": {
                "name": "infra-docker-dummy",
                "git": "https://user@dev.azure.com/organization/PRJ/_git/infra-docker-dummy",
                "acr": "orgprj",
                "build_pipeline": "infra-docker-dummy",
                "project": "PRJ"
            },
            "dummy_repo2": {
                "name": "infra-docker-dummy2",
                "git": "https://user@dev.azure.com/organization/PRJ/_git/infra-docker-dummy2",
                "acr": "orgprj",
                "build_pipeline": "infra-docker-dummy2",
                "project": "PRJ"
            },
            "dummy_repo3": {
                "name": "infra-docker-dummy3",
                "git": "https://user@dev.azure.com/organization/PRJ/_git/infra-docker-dummy3",
                "acr": "orgprj",
                "build_pipeline": "infra-docker-dummy3",
                "project": "PRJ"
            }}


if __name__ == '__main__':
    unittest.main()
