import sys
from pathlib import Path

import pytest
from gitlab.client import Gitlab
from gitlab.v4.objects import GroupManager
from gitlab.v4.objects.groups import Group

sys.path.append(str(Path(__file__).parents[1].joinpath("src")))
from repository.mapper import GitlabClient


def make_dummy_client(mocker, has_group: bool = True):
    mock_gl = mocker.Mock(spec=Gitlab)
    mock_group = mocker.Mock(spec=Group)
    mock_goup_manager = mocker.Mock(spec=GroupManager)
    mock_gl.groups = mock_goup_manager
    mock_client = mocker.Mock(spec=GitlabClient)
    mock_client.id = 1
    mock_client.gl = mock_gl
    if has_group:
        mocker.patch("gitlab.v4.objects.GroupManager.get", mock_group)
        mock_client.group = mock_group
    else:
        mocker.patch("gitlab.v4.objects.GroupManager.get", None)
        mock_client.group = None
    return mock_client


@pytest.fixture
def mock_construct_gitlab_client(mocker):
    mocker.patch("repository.mapper.GitlabClient", make_dummy_client(mocker))
