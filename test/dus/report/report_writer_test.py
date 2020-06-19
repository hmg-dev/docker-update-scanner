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
from tempfile import TemporaryDirectory
from mockito import when, unstub

from dus.report import report_writer
from dus import config as conf


class ReportWriterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.orig_target_dir = conf.report_target_dir
        self.maxDiff = None
        unittest.TestCase.setUp(self)

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        unstub()
        conf.report_target_dir = self.orig_target_dir

    def test_generate_report_page(self):
        dummy_projects = {"Pinky", "PRJ", "Brain", "TEST"}
        dummy_repos = [
            {"name": "infra-docker-dummy", "project": "PRJ", "updateDate": "2020-05-14 11:45:23", "needUpdate": False},
            {"name": "infra-docker-narf", "project": "PRJ", "updateDate": "2020-04-14 11:45:23", "needUpdate": False},
            {"name": "prj-docker-zort", "project": "PRJ", "updateDate": "2020-04-12 12:45:23", "needUpdate": False},
            {"name": "client-project-aujunge", "project": "Pinky", "updateDate": "2020-05-10 10:45:23", "needUpdate": False},
            {"name": "world-domination-importer", "project": "Pinky", "updateDate": "2020-04-10 15:45:23", "needUpdate": True},
            {"name": "dictator-song-tool", "project": "Pinky", "updateDate": "2020-03-10 10:45:23", "needUpdate": False},
            {"name": "dummy-problem", "project": "Brain", "updateDate": "ERROR", "needUpdate": False},
            {"name": "chia-earth-proxy", "project": "Brain", "updateDate": "2020-05-10 10:45:23",
             "needUpdate": False, "parent_image_outdated": True, "parent_image": "ubuntu-narf:42"}
        ]

        when(report_writer)._now().thenReturn("2020-05-14 12:33:06.896510")

        with TemporaryDirectory("dummy-repo") as td:
            conf.report_target_dir = td + "/"
            report_writer.generate_report_page(dummy_projects, dummy_repos)

            with open(os.path.dirname(__file__) + "/../resources/report.html.expected", 'r') as f:
                expected_result = f.read()

            with open(td + "/report.html", 'r') as f:
                result = f.read()

            # uncomment if you made changes and copy the file to the resources
            # that's easier than changing the file and hoping that the editor don't mess around with the indentation!
            #
            # with open("/tmp/report.html", "w") as page_file:
            #     page_file.write(result)

            self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
