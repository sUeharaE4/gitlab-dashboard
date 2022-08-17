"""Provide service for issue dataset."""
from collections import defaultdict
from typing import Union

import pandas as pd
from gitlab.v4.objects.commits import ProjectCommit
from gitlab.v4.objects.projects import Project
from stqdm import stqdm
from tqdm import tqdm

from common import util
from common.Logger import get_logger, logging_start_end
from repository.mapper import GitlabClient

logger = get_logger()


@logging_start_end(logger)
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
    # TODO: get each commit info per merge requests to keep commiter information and aggregate by id at view layer.
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
        logger.debug(f"Collect commits from merge requests {mr.title=}")
        tmp_mergerequest = mr.__dict__["_attrs"].copy()
        tmp_mergerequest["group_id"] = group_id
        util.flatten_dict_in_dict(tmp_mergerequest)
        mr_project = id_pj_map[mr.project_id]
        mr_commit_stat = __make_commit_stats(mr.commits(all=True), mr_project)
        tmp_mergerequest.update(mr_commit_stat)
        mergerequests.append(tmp_mergerequest)
    return pd.DataFrame.from_dict(mergerequests)


def __make_commit_stats(mr_commits: list[ProjectCommit], project: Project) -> dict:
    def agg_diff(commit_diffs: list[dict]) -> dict[str, dict[str, int]]:
        diffs = dict()
        for diff in commit_diffs:
            if diff["deleted_file"]:
                continue
            file_name = diff["new_path"]
            diff_lines = diff["diff"].split("\n")
            add_lines = len(list(filter(lambda s: s.startswith("+"), diff_lines)))
            del_lines = len(list(filter(lambda s: s.startswith("-"), diff_lines)))
            diffs[file_name] = {"add": add_lines, "del": del_lines}
        return diffs

    def merge_diff(total_diff: dict, new_diff: dict):
        for file_name, diff in new_diff.items():
            add_lines = total_diff[file_name].get("add", 0) + diff["add"]
            del_lines = total_diff[file_name].get("del", 0) + diff["del"]
            change_cnt = total_diff[file_name].get("change_cnt", 0) + 1
            total_diff[file_name]["add"] = add_lines
            total_diff[file_name]["del"] = del_lines
            total_diff[file_name]["change_cnt"] = change_cnt

    # NOTE: this is not pythonic...
    mr_commit_stat: dict[str, Union[int, dict]] = {"total_commits": len(mr_commits)}
    total_changed_file_count = 0
    total_additions = 0
    total_deletions = 0
    total_changes = 0
    diffs: defaultdict[str, dict[str, int]] = defaultdict(dict)

    commit_count = len(mr_commits)
    for i, mr_commit in enumerate(mr_commits):
        logger.debug(f"Fetch commit from this merge requests {i+1}/{commit_count}")
        commit = project.commits.get(mr_commit.short_id)
        stats = commit.stats
        total_additions += stats["additions"]
        total_deletions += stats["deletions"]
        total_changes += stats["total"]
        total_changed_file_count += len(mr_commit.diff())

        merge_diff(diffs, agg_diff(commit.diff()))

    mr_commit_stat["total_additions"] = total_additions
    mr_commit_stat["total_deletions"] = total_deletions
    mr_commit_stat["total_changes"] = total_changes
    mr_commit_stat["total_changed_file_count"] = total_changed_file_count
    mr_commit_stat["diff"] = diffs
    return mr_commit_stat
