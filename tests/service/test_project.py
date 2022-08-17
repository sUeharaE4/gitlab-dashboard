import pytest

from repository.mapper import GitlabClient
from service import project
from tests.mock_classes import MockMergeRequest, MockProject, MockProjectCommit


@pytest.mark.usefixtures("mock_construct_gitlab_client")
@pytest.mark.parametrize(
    "mock_list",
    [
        (["pj_1"]),
        (["pj_1", "pj_2"]),
        ([]),
    ],
)
def test_list_project(mocker, mock_list):
    # this function simply return GitlabClient.fetch_projects_in_group so test just return mocked results
    mocker.patch.object(GitlabClient, "fetch_projects_in_group", return_value=mock_list)
    assert project.list_project(1) == mock_list
