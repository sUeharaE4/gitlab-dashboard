from typing import Any, Union

MOCK_STATS = {"additions": 1, "deletions": 1, "total": 2}


class MockGitlabBase:
    def __init__(self, attrs: Union[dict[str, Any], None]):
        if attrs is None:
            attrs = {}
        self._attrs = attrs


class MockMergeRequest(MockGitlabBase):
    def __init__(
        self,
        attrs: Union[dict[str, Any], None] = None,
        project_id: int = 1,
        title: str = "mr_title",
        commits: Union[list, None] = None,
    ):
        self.project_id = project_id
        self.title = title
        if commits is None:
            commits = [MockProjectCommit()]
        self.commits_in_mr = commits
        super().__init__(attrs)

    def commits(self, all: bool = True):
        return self.commits_in_mr


class MockProject(MockGitlabBase):
    def __init__(
        self,
        attrs: Union[dict[str, Any], None] = None,
        id: int = 1,
        name: str = "pj_1",
        commit_info: Union[dict[str, Any], None] = None,
    ):
        self.id = id
        self.name = name
        if commit_info is None:
            mock_commit = MockProjectCommit()
            commit_info = {mock_commit.short_id: mock_commit}
        self.commits = commit_info
        super().__init__(attrs)


class MockProjectCommit(MockGitlabBase):
    def __init__(
        self,
        attrs: Union[dict[str, Any], None] = None,
        short_id: str = "short_id_1",
        stats: dict[str, int] = MOCK_STATS,
        diff: Union[list[dict[str, Any]], None] = None,
    ):
        self.short_id = short_id
        self.stats = stats
        if diff is None:
            diff = [{"new_path": "file_1", "diff": "+additional_diff\n-deletion_diff", "deleted_file": None}]
        self.diff_info = diff
        super().__init__(attrs)

    def diff(self):
        return self.diff_info


class MockProjectCommitManager(MockGitlabBase):
    def __init__(
        self, attrs: Union[dict[str, Any], None] = None, commit_info: Union[dict[str, MockProjectCommit], None] = None
    ):
        if commit_info is None:
            mock_commit = MockProjectCommit()
            commit_info = {mock_commit.short_id: mock_commit}
        self.commits = commit_info
        super().__init__(attrs)


class MockIssue(MockGitlabBase):
    def __init__(self, attrs: Union[dict[str, Any], None]):
        super().__init__(attrs)
