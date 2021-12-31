"""Create issue view."""
import pandas as pd
import streamlit as st

from service.issue import make_issue_df
from view import util


def create_issue_view(group_id: int):
    df = make_issue_df(group_id)
    filtered_df = util.filter_by_projects(df, group_id)
    create_count_of_created_issue_view(filtered_df)
    create_count_of_closed_issue_view(filtered_df)
    util.show_table("Detail", df)


def create_count_of_created_issue_view(issue_df: pd.DataFrame):
    st.markdown("## Created Issues")
    util.create_count_of_created_view(issue_df)


def create_count_of_closed_issue_view(issue_df: pd.DataFrame):
    st.markdown("## Closed Issues")
    closed_df = issue_df[issue_df["state"] == "closed"].copy()
    util.create_count_of_created_view(closed_df)
