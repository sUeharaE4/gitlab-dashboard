"""Provide service for issue dataset."""
from typing import Union

import pandas as pd

from common import util
from repository.mapper import GitlabClient


def make_mergerequest_df(
    group_id: int, *, state: Union[str, None] = None, target_pj_names: Union[list[str], None] = None
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
    # GroupMergeRequest does not have commit info. So get from Project commits.
    # Project.commits.list() has not stats of commit so fetch each single commit.
    group_mr = client.fetch_mergerrequests_in_group(state=state)
    pj_in_group = client.fetch_projects_in_group([mr.project_id for mr in group_mr])
    if target_pj_names is not None:
        pj_in_group = [pj for pj in pj_in_group if pj.name in target_pj_names]
    id_pj_map = {pj.id: pj for pj in pj_in_group}

    mergerequests = []
    for mr in group_mr:
        tmp_mergerequest = mr.__dict__["_attrs"].copy()
        tmp_mergerequest["group_id"] = group_id
        util.flatten_dict_in_dict(tmp_mergerequest)
        mr_commits = mr.commits(all=True)
        mr_commit_stat = {"total_commits": len(mr_commits)}
        for mr_commit in mr_commits:
            commit = id_pj_map[mr.project_id].commits.get(mr_commit.short_id)
            mr_commit_stat["total_changed_file_count"] = mr_commit_stat.get("total_changed_file_count", 0) + len(
                mr_commit.diff()
            )
            if commit:
                stats = commit.stats
                mr_commit_stat["total_additions"] = mr_commit_stat.get("total_additions", 0) + stats["additions"]
                mr_commit_stat["total_deletions"] = mr_commit_stat.get("total_deletions", 0) + stats["deletions"]
                mr_commit_stat["total_changes"] = mr_commit_stat.get("total_changes", 0) + stats["total"]
        tmp_mergerequest.update(mr_commit_stat)
        mergerequests.append(tmp_mergerequest)
    return pd.DataFrame.from_dict(mergerequests)
