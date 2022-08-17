import pytest

from repository.mapper import GitlabClient
from service import mergerequest
from tests.mock_classes import MockMergeRequest, MockProject, MockProjectCommit


@pytest.mark.usefixtures("mock_construct_gitlab_client")
@pytest.mark.parametrize(
    "target_pj_names",
    [
        (["pj_1"]),
        (["pj_1", "pj_2"]),
        (None),
    ],
)
def test_make_issue_df(mocker, target_pj_names):
    mock_commits = [MockProjectCommit(short_id=f"short_id{str(i)}") for i in range(3)]
    mock_commits.append(MockProjectCommit(short_id=f"short_id{len(mock_commits)}", diff=[{"deleted_file": "file_d"}]))
    mock_mrs = [MockMergeRequest(project_id=i, commits=mock_commits) for i in range(3)]
    mock_pjs = [MockProject(id=i, name=f"pj_{i}", commit_info={m.short_id: m for m in mock_commits}) for i in range(3)]
    mocker.patch.object(GitlabClient, "fetch_mergerrequests_in_group", return_value=mock_mrs)
    mocker.patch.object(GitlabClient, "fetch_projects_in_group", return_value=mock_pjs)
    mergerequest_df = mergerequest.make_mergerequest_df(1, target_pj_names=target_pj_names, from_streamlit_view=True)
    if target_pj_names is None:
        expect_rows = 3
    else:
        expect_rows = len(target_pj_names)
    assert mergerequest_df.shape[0] == expect_rows
    for group_id in mergerequest_df["group_id"]:
        assert group_id == 1
