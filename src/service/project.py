"""Provide service for project dataset."""
from gitlab.v4.objects.projects import Project

from common.Logger import get_logger, logging_start_end
from repository.mapper import GitlabClient

logger = get_logger()


@logging_start_end(logger)
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
