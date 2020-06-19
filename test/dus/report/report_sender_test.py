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
import smtplib
from shutil import copyfile
from tempfile import TemporaryDirectory
from mockito import mock, when, unstub, ANY, verify, captor
from dus import config as conf
from dus.report import report_sender
from email.message import EmailMessage


class ReportSenderTest(unittest.TestCase):
    def setUp(self) -> None:
        unittest.TestCase.setUp(self)
        self.orig_target_dir = conf.report_target_dir
        self.dummy_password = "mail-password"

    def tearDown(self) -> None:
        unittest.TestCase.tearDown(self)
        unstub()
        conf.report_target_dir = self.orig_target_dir

    def test_send_report(self):
        smtp_mock = mock(spec=smtplib.SMTP)
        when(smtplib).SMTP(ANY(), ANY()).thenReturn(smtp_mock)

        msg_captor = captor(ANY(EmailMessage))

        when(smtp_mock).login(ANY(), ANY())
        when(smtp_mock).send_message(msg_captor)
        when(smtp_mock).quit()

        with TemporaryDirectory("dummy-repo") as td:
            when(os).getenv(report_sender.ENV_MAIL_PASSWD).thenReturn(self.dummy_password)
            conf.report_target_dir = td + "/"
            copyfile(os.path.dirname(__file__) + "/../resources/report.html.expected", td + "/report.html")
            report_sender.send_report()

        verify(smtplib, times=1).SMTP(conf.report_smtp_server, conf.report_smtp_port)
        verify(smtp_mock, times=1).login(conf.report_smtp_user, self.dummy_password)
        verify(smtp_mock, times=1).send_message(...)
        verify(smtp_mock, times=1).quit()

        self.assertEqual(conf.report_sender, msg_captor.value["From"])
        self.assertEqual(conf.report_recipient, msg_captor.value["To"])
        self.assertIsNotNone(msg_captor.value.get_body())


if __name__ == '__main__':
    unittest.main()
