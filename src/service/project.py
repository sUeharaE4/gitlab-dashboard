"""Provide service for project dataset."""
from gitlab.v4.objects.projects import Project

from repository.mapper import GitlabClient


def list_project(group_id: int) -> list[Project]:
    """Make list of projects in group.

    Parameters
    ----------
    group_id :
        target group you want to get issues.

    Returns
    -------
    list[Project]
        projects in the group.
    """
    return GitlabClient(group_id).fetch_projects_in_group()
