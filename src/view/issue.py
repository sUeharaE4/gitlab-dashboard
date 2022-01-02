"""Create issue view."""
import datetime
from typing import Union

import altair as alt
import pandas as pd
import streamlit as st

from common import Const
from service.issue import make_issue_df
from view import util


def create_issue_view(group_id: int):
    """Create streamlit view of issues."""
    df = __fetch_dataset(group_id)
    if df.empty:
        st.error("No issue found in this group.")
        return
    filtered_df = util.filter_by_projects(df, group_id)
    if filtered_df.empty:
        st.error("No issue found in this project.")
        return

    create_count_of_created_issue_view(filtered_df)
    create_count_of_closed_issue_view(filtered_df)
    # TODO: add filter selector. filter should be used globally?
    create_assigned_issue_count_view(filtered_df)
    create_label_issues_view(filtered_df)
    util.show_table("Detail", df)


def create_count_of_created_issue_view(issue_df: pd.DataFrame):
    """Create charts of created issues."""
    st.markdown("## Created Issues")
    util.create_count_of_created_view(issue_df)


def create_count_of_closed_issue_view(issue_df: pd.DataFrame):
    """Create charts of closed issues."""
    st.markdown("## Closed Issues")
    closed_df = issue_df[issue_df["state"] == "closed"].copy()
    util.create_count_of_created_view(closed_df)


def create_assigned_issue_count_view(
    issue_df: pd.DataFrame,
    *,
    state: Union[str, None] = None,
    project_ids: Union[list[int], None] = None,
    due_date: Union[tuple[datetime.date], None] = None,
    labels: Union[list[str], None] = None
):
    """Create a chart of counting issues for assignees."""
    st.markdown("## Assigned Issues")
    target_cols = ["id", "project_id", "assignee-username", "labels", "state", "due_date"]
    df = __filter_issues(issue_df[target_cols], state=state, project_ids=project_ids, due_date=due_date, labels=labels)

    df["assignee-username"] = df["assignee-username"].fillna("Not Assigned!")
    df["count"] = 0
    agg_df = df.groupby(["assignee-username", "state"], as_index=False).count()
    chart = (
        alt.Chart(agg_df)
        .mark_bar()
        .encode(
            x=alt.X("assignee-username", title="assignee"),
            y=alt.Y("id", title="issue count"),
            color="state",
            tooltip=["assignee-username", "state", "count"],
        )
    ).interactive()
    st.altair_chart(chart)


def create_label_issues_view(
    issue_df: pd.DataFrame,
    *,
    state: Union[str, None] = None,
    project_ids: Union[list[int], None] = None,
    due_date: Union[tuple[datetime.date], None] = None,
    labels: Union[list[str], None] = None
):
    """Create a chart of issue count by labels."""
    st.markdown("## Issues for each labels")
    target_cols = ["id", "project_id", "labels", "state", "due_date"]
    df = __filter_issues(issue_df[target_cols], state=state, project_ids=project_ids, due_date=due_date, labels=labels)
    df = df.explode("labels").fillna("No label set!")
    df["count"] = 0

    agg_df = df.groupby(["labels", "state"], as_index=False).count()
    chart = (
        alt.Chart(agg_df)
        .mark_bar()
        .encode(
            x=alt.X("labels", title="label"),
            y=alt.Y("id", title="issue count"),
            color="state",
            tooltip=["labels", "state", "count"],
        )
    ).interactive()
    st.altair_chart(chart)


def __filter_issues(
    issue_df: pd.DataFrame,
    *,
    state: Union[str, None] = None,
    project_ids: Union[list[int], None] = None,
    due_date: Union[tuple[datetime.date], None] = None,
    labels: Union[list[str], None] = None
) -> pd.DataFrame:
    df = issue_df.copy()
    # NOTE: due_date is tuple.
    #       if len(due_date) == 2, filter between two date. if len(due_date) == 1, filter until due_date.
    # NOTE: create class for filter condition is better.
    if state:
        df = df[df["state"] == state]
    if project_ids:
        df = df[df["project_id"].isin(project_ids)]
    if due_date:
        if len(due_date) > 1:
            df = df[df["due_date"] > due_date]
            df = df[df["due_date"] < due_date]
        else:
            df = df[df["due_date"] < due_date]
    if labels:
        df = df[df["labels"].idin(labels)]
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df


@st.cache(ttl=Const.ST_CACHE_TIME_SHORT, suppress_st_warning=True, allow_output_mutation=True)
def __fetch_dataset(group_id: int) -> pd.DataFrame:
    return make_issue_df(group_id)
