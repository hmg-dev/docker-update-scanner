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

from dus.project.repo_details import RepoDetails
from dus.acr.azure_rest import DockerImageDetails
from dus.project.parent_image_details import ParentImage
from dus import config as conf


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
parent_image_details = ParentImage()


def determine_stats(repo, git_repo):
    image_name = RepoDetails(repo).determine_imagename(git_repo)
    print(f"Determine details for image: {image_name}")

    az_details = DockerImageDetails(repo["acr"], image_name)
    tag = az_details.az_latest_tag()
    parent_image = RepoDetails.determine_parent_image(git_repo)
    parent_last_update = determine_last_updatedate(parent_image, git_repo)
    need_update = is_require_update(tag["lastUpdateTime"], parent_last_update)
    outdated = is_outdated(parent_last_update, datetime.datetime.now(), repo=repo)

    return {"tag": tag,
            "image_name": image_name,
            "parent_image": parent_image,
            "parent_last_update": parent_last_update,
            "update_required": need_update,
            "outdated_parent": outdated}


def is_require_update(tag_udt, parent_udt):
    image_update_dt = datetime.datetime.strptime(tag_udt.rsplit('.')[0], DATETIME_FORMAT)
    parent_update_dt = datetime.datetime.strptime(parent_udt.rsplit('.')[0], DATETIME_FORMAT)

    return image_update_dt < parent_update_dt


def determine_last_updatedate(parent_image, git_repo):
    if ParentImage.is_public_image(parent_image):
        return parent_image_details.determine_last_updatedate(parent_image)

    if ":$" not in parent_image:
        az_details = DockerImageDetails.from_FQDIN(parent_image)
        return az_details.az_image_tag_details()["lastUpdateTime"]

    print("encountered an ARG-variable as tag-version - need to fetch it from pipeline-definition")
    real_tag = RepoDetails.determine_imageversion(git_repo)
    parent_image = parent_image.split(":")[0]
    az_details = DockerImageDetails.from_FQDIN(parent_image, default_tag=real_tag)
    return az_details.az_image_tag_details()["lastUpdateTime"]


def is_outdated(value_str, reference, repo=None):
    if repo is not None and repo.get("outdate_whitelist"):
        return False

    value = datetime.datetime.strptime(value_str.rsplit('.')[0], DATETIME_FORMAT)
    return value + datetime.timedelta(days=conf.max_age_days) < reference
