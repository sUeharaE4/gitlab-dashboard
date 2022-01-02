"""Fetch gitlab data by rest api."""
from dataclasses import dataclass, field
from typing import Union

from gitlab.client import Gitlab
from gitlab.v4.objects.commits import ProjectCommit
from gitlab.v4.objects.groups import Group
from gitlab.v4.objects.issues import GroupIssue
from gitlab.v4.objects.merge_requests import GroupMergeRequest, MergeRequest
from gitlab.v4.objects.projects import GroupProject, Project

from common import GitlabConst, errors


@dataclass
class GitlabClient:
    """API Client for fetch gitlab specific group data."""

    group_id: int
    gl: Gitlab = field(init=False, metadata={"metadata": "gitlab_client"})
    group: Group = field(init=False, metadata={"metadata": "gitlab_group"})

    def __post_init__(self):
        """Set group_id and fetch group."""
        self.gl = Gitlab(GitlabConst.URL, private_token=GitlabConst.TOKEN)
        self.group = self.gl.groups.get(self.group_id)
        if self.group is None:
            raise errors.ResourceNotFoundError("group", {"group_id": self.group_id})

    def fetch_group_issues(
        self, *, state: Union[str, None] = None, labels: Union[list[str], None] = None
    ) -> list[GroupIssue]:
        """Fetch issues in group.

        Parameters
        ----------
        state :
            issue state. if you need only opened issue, pass 'opened', by default None
        labels :
            if you need issues has specific labels, pass label list, by default None

        Returns
        -------
        list[GroupIssue]
            list of issues.
        """
        if labels:
            return self.group.issues.list(all=True, state=state, labels=labels)
        else:
            return self.group.issues.list(all=True, state=state)

    def fetch_group_mergerequests(self, *, state: Union[str, None] = None) -> list[GroupMergeRequest]:
        """Fetch mergerequests in group.

        Parameters
        ----------
        state :
            issue state. if you need only opened issue, pass 'opened', by default None

        Returns
        -------
        list[GroupMergeRequest]
            list of mergerequests.
        """
        return self.group.mergerequests.list(all=True, state=state)

    def fetch_mergerrequests_in_group(self, *, state: Union[str, None] = None) -> list[MergeRequest]:
        group_mr = self.fetch_group_mergerequests(state=state)
        pj_ids = set(mr.project_id for mr in group_mr)
        id_pj_map = {pj_id: self.fetch_single_project(pj_id) for pj_id in pj_ids}
        return [id_pj_map[mr.project_id].mergerequests.get(mr.iid) for mr in group_mr]

    def fetch_single_project(self, project_id: int) -> Project:
        return self.gl.projects.get(project_id)

    def fetch_group_projects(self) -> list[GroupProject]:
        """Fetch groups in this group."""
        return self.group.projects.list(all=True)

    def fetch_projects_in_group(self) -> list[Project]:
        group_pj = self.fetch_group_projects()
        return [self.fetch_single_project(p.id) for p in group_pj]

    def fetch_commits_in_group_projects(self) -> dict[int, list[ProjectCommit]]:
        """Fetch commits in each projects. May be very heavy."""
        pj_commits = dict()
        for project in self.fetch_projects_in_group():
            pj_commits[project.id] = project.commits.list(all=True)
        return pj_commits

    def fetch_single_commit(self, project_id: int, short_id: str) -> Union[ProjectCommit, None]:
        """Fetch commit has specific id."""
        pj = next((p for p in self.fetch_group_projects() if p.id == project_id), None)
        if pj:
            return pj.commits.get(short_id)
        else:
            return None
