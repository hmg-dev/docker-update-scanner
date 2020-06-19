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

import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
from dus import config as conf


def generate_report_page(projects, repos):
    env = Environment(
        loader=PackageLoader("dus", "templates"),
        autoescape=select_autoescape(["html", "xml"])
    )
    sorted_projects = list(projects)
    sorted_projects.sort()
    template = env.get_template("report.html")
    page = template.render(projects=sorted_projects, repos=repos, report_date=_now())

    with open(conf.report_target_dir + "report.html", "w") as page_file:
        page_file.write(page)


def _now():
    return str(datetime.datetime.now())
