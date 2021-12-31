"""Provide service for issue dataset."""
from typing import Union

import pandas as pd

from common import util
from repository.mapper import GitlabClient


def make_issue_df(
    group_id: int, *, state: Union[str, None] = None, labels: Union[list[str], None] = None
) -> pd.DataFrame:
    """Make dataset of group issue.

    Parameters
    ----------
    group_id :
        target group you want to get issues.
    state :
        issue state. if you need only opened issue, pass 'opened', by default None
    labels :
        if you need issues has specific labels, pass label list, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame each row has single issue infomation.
    """
    issues = []
    for issue in GitlabClient(group_id).fetch_group_issues(state=state, labels=labels):
        tmp_issue = issue.__dict__["_attrs"].copy()
        util.flatten_dict_in_dict(tmp_issue)
        issues.append(tmp_issue)
    return pd.DataFrame.from_dict(issues)
