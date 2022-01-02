"""Create issue view."""
from typing import Union
import datetime

import pandas as pd
import streamlit as st
import altair as alt

from service.issue import make_issue_df
from view import util


def create_issue_view(group_id: int):
    df = make_issue_df(group_id)
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
    util.show_table("Detail", df)


def create_count_of_created_issue_view(issue_df: pd.DataFrame):
    st.markdown("## Created Issues")
    util.create_count_of_created_view(issue_df)


def create_count_of_closed_issue_view(issue_df: pd.DataFrame):
    st.markdown("## Closed Issues")
    closed_df = issue_df[issue_df["state"] == "closed"].copy()
    util.create_count_of_created_view(closed_df)


def create_assigned_issue_count_view(
    issue_df: pd.DataFrame,
    *,
    state: Union[str, None] = None,
    project_ids: Union[list[int], None] = None,
    due_date: Union[tuple[datetime], None] = None,
    labels: Union[list[str], None] = None
):
    # NOTE: due_date is tuple. if len(due_date) == 2, filter between two date. if len(due_date) == 1, filter until due_date.
    # NOTE: create class for filter condition is better.
    st.markdown("## Assigned Issues")
    target_cols = ["id", "project_id", "assignee-username", "labels", "state", "due_date"]
    df = issue_df[target_cols].copy()
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

    df["assignee-username"] = df["assignee-username"].fillna("Not Assigned!")
    agg_df = df.groupby(["assignee-username", "state"], as_index=False).count()
    chart = (
        alt.Chart(agg_df)
        .mark_bar()
        .encode(x=alt.X("assignee-username", title="assignee"), y=alt.Y("id", title="issue count"), color="state")
    )
    st.altair_chart(chart)
