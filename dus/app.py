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

import traceback

from dus import repos
from dus.git.repository_fetcher import RepositoryFetcher
from dus.pipeline.pipeline_interaction import Pipeline
from dus.report import report_writer, report_sender
from dus.project import data_fetcher

update_status = {}
projects = set()
repo_report_data = []


def process_repository(repo):
    git_repo = RepositoryFetcher(repo["git"], repo["name"])
    try:
        git_repo_path = git_repo.clone_or_update_repo()
        stats = data_fetcher.determine_stats(repo, git_repo_path)

        update_status[stats["image_name"]] = stats["update_required"]
        print(f"RepoImage '{stats['image_name']}' was Last updated: {stats['tag'].get('lastUpdateTime')} and extends " +
              f"from: {stats['parent_image']} which was last updated: {stats['parent_last_update']} needs update: {stats['update_required']}")

        if stats["update_required"]:
            _trigger_pipeline(repo)

        _update_report_data(repo, stats)
        return 0
    except (Exception, FileNotFoundError) as e:
        print(f"Unable to process repository: {repo}")
        print(f"{e}\nCaused by: {traceback.format_exc()}")
        _update_report_data(repo, {"tag": {"lastUpdateTime": "ERROR"}, "update_required": False})
        return 1
    finally:
        git_repo.cleanup()


def _trigger_pipeline(repo):
    pipeline = Pipeline(repo["project"], repo["build_pipeline"])
    details = pipeline.validate()
    if details is not None:
        pipeline.trigger_build(details["id"])


def _update_report_data(current_repo, stats):
    projects.add(current_repo["project"])
    repo_report_data.append({"name": current_repo["name"], "project": current_repo["project"],
        "updateDate": stats["tag"]["lastUpdateTime"], "needUpdate": stats["update_required"],
        "parent_image_outdated": stats.get("outdated_parent"), "parent_image": stats.get("parent_image")})


def main():
    print("Checking Docker-Repos...")
    occurred_errors = 0
    for key, repo in repos.to_check.items():
        occurred_errors += process_repository(repo)

    if occurred_errors > 0:
        print(f"Encountered Failures: {occurred_errors}")

    report_writer.generate_report_page(projects, repo_report_data)
    report_sender.send_report()
    print(f"\n\nSTATUS: {update_status}")
    print("DONE")


if __name__ == '__main__':
    main()
