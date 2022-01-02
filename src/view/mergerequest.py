"""Create issue view."""
import altair as alt
import pandas as pd
import streamlit as st

from service.mergerequest import make_mergerequest_df
from service.project import list_project
from view import util


def create_mergerequest_view(group_id: int):
    pj_in_groups = list_project(group_id)
    pj_names = [pj.name for pj in pj_in_groups]
    target_pj_names = st.multiselect("Select projects to fetch MergeRequests", pj_names, pj_names)
    df = make_mergerequest_df(group_id, target_pj_names=target_pj_names)
    if df.empty:
        st.error("No merge request found in this group.")
        return
    filtered_df = util.filter_by_projects(df, group_id)
    if filtered_df.empty:
        st.error("No merge request found in this project.")

    create_count_of_created_mr_view(filtered_df)
    create_size_view(filtered_df)

    st.markdown("## Detail")
    util.show_table("All of MergeRequests", df, height=200)


def aggregate_created_count(df: pd.DataFrame, unit: str):
    created_df = df.copy()
    created_df["created_at"] = util.to_datetime(created_df["created_at"])
    agg_df = util.count_by_datetime(created_df, "created_at", ["id"], ["count"], unit)
    agg_df.columns = ["count"]
    return agg_df.reset_index()


def create_count_of_created_mr_view(mergerequest_df: pd.DataFrame):
    st.markdown("## Created MergeRequests")
    util.create_count_of_created_view(mergerequest_df)


def create_size_view(mergerequest_df: pd.DataFrame):
    st.markdown("## Size of MergeRequests")
    df = mergerequest_df.copy()
    df["mean_change_files"] = df["total_changed_file_count"] / df["total_commits"]
    df["mean_changes"] = df["total_changes"] / df["total_commits"]
    df["mean_additions"] = df["total_additions"] / df["total_commits"]
    df["mean_deletions"] = df["total_deletions"] / df["total_commits"]
    chart = (
        alt.Chart(df)
        .mark_point()
        .encode(
            alt.X("mean_changes", title="mean changes (total changes / commits)"),
            alt.Y("mean_change_files", title="mean change files(sum of change files / commits)"),
            color="project_name",
            size=alt.Size("user_notes_count", bin=True),
            tooltip=[
                "title",
                "project_name",
                "state",
                "target_branch",
                "source_branch",
                "author-username",
                "merged_by-username",
                "user_notes_count",
                "total_commits",
                "changes_count",
                "total_additions",
                "total_deletions",
                "created_at",
                "merged_at",
                "closed_at",
            ],
        )
    )
    st.altair_chart(chart, use_container_width=True)
    print(df[[n for n in df.columns if "mean_" in n]])
