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
import smtplib
from email.message import EmailMessage
from dus import config as conf


ENV_MAIL_PASSWD = "ENV_MAIL_PASSWD"


def send_report():
    smtp = smtplib.SMTP(conf.report_smtp_server, conf.report_smtp_port)
    smtp.login(conf.report_smtp_user, os.getenv(ENV_MAIL_PASSWD))

    msg = EmailMessage()
    msg.set_default_type("text/html")
    msg["From"] = conf.report_sender
    msg["To"] = conf.report_recipient
    msg["Subject"] = "Docker Update Scan Report"

    with open(conf.report_target_dir + "report.html", "r") as report_file:
        msg.add_alternative(report_file.read(), subtype="html")

    smtp.send_message(msg)
    smtp.quit()
