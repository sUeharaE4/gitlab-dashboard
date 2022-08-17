from typing import Any

import pandas as pd

from repository.mapper import GitlabClient
from service import issue
from tests.mock_classes import MockIssue


def test_make_issue_df(mocker, mock_construct_gitlab_client):
    mock_issues = [MockIssue({"id": i, "name": f"name_{i}", "nest": {"id": 1, "name": 1}}) for i in range(3)]
    mocker.patch.object(GitlabClient, "fetch_group_issues", return_value=mock_issues)
    issue_df = issue.make_issue_df(1)
    assert issue_df.shape == (3, 4)
    expect = pd.DataFrame([{"id": i, "name": f"name_{i}", "nest-id": 1, "nest-name": 1} for i in range(3)])
    assert (issue_df == expect).all().all()
