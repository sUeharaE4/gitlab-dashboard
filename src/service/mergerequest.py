"""Provide service for issue dataset."""
from typing import Union

import pandas as pd
from gitlab.v4.objects.commits import ProjectCommit
from gitlab.v4.objects.projects import Project
from stqdm import stqdm
from tqdm import tqdm

from common import util
from repository.mapper import GitlabClient


def make_mergerequest_df(
    group_id: int,
    *,
    state: Union[str, None] = None,
    target_pj_names: Union[list[str], None] = None,
    from_streamlit_view: bool = False,
) -> pd.DataFrame:
    """Make dataset of group mergerequest.

    Parameters
    ----------
    group_id :
        target group you want to get mergerequests.
    state :
        mergerequest state. if you need only opened mergerequest, pass 'opened', by default None

    Returns
    -------
    pd.DataFrame
        DataFrame each row has single mergerequest infomation.
    """
    client = GitlabClient(group_id)
    pg_bar = tqdm
    if from_streamlit_view:
        pg_bar = stqdm
    # GroupMergeRequest does not have commit info. So get from Project commits.
    # Project.commits.list() has not stats of commit so fetch each single commit.
    group_mr = client.fetch_mergerrequests_in_group(state=state)
    pj_in_group = client.fetch_projects_in_group([mr.project_id for mr in group_mr])
    if target_pj_names is not None:
        pj_in_group = [pj for pj in pj_in_group if pj.name in target_pj_names]
    id_pj_map = {pj.id: pj for pj in pj_in_group}
    group_mr = [mr for mr in group_mr if mr.project_id in id_pj_map]

    mergerequests = []
    for mr in pg_bar(group_mr, desc="Collect commits from MRs"):
        tmp_mergerequest = mr.__dict__["_attrs"].copy()
        tmp_mergerequest["group_id"] = group_id
        util.flatten_dict_in_dict(tmp_mergerequest)
        mr_project = id_pj_map[mr.project_id]
        mr_commit_stat = __make_commit_stats(mr.commits(all=True), mr_project)
        tmp_mergerequest.update(mr_commit_stat)
        mergerequests.append(tmp_mergerequest)
    return pd.DataFrame.from_dict(mergerequests)


def __make_commit_stats(mr_commits: list[ProjectCommit], project: Project) -> dict:
    mr_commit_stat = {"total_commits": len(mr_commits)}
    mr_commit_stat["total_changed_file_count"] = 0
    mr_commit_stat["total_additions"] = 0
    mr_commit_stat["total_deletions"] = 0
    mr_commit_stat["total_changes"] = 0

    for mr_commit in mr_commits:
        commit = project.commits.get(mr_commit.short_id)
        mr_commit_stat["total_changed_file_count"] += len(mr_commit.diff())
        stats = commit.stats
        mr_commit_stat["total_additions"] += stats["additions"]
        mr_commit_stat["total_deletions"] += stats["deletions"]
        mr_commit_stat["total_changes"] += stats["total"]
    return mr_commit_stat
