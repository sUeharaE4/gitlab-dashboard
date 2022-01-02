"""Create issue view."""
import altair as alt
import pandas as pd
import streamlit as st

from service.mergerequest import make_mergerequest_df
from view import util


def create_mergerequest_view(group_id: int):
    """Create a view of streamlit MRs."""
    # pj_in_groups = list_project(group_id)
    # pj_names = [pj.name for pj in pj_in_groups]
    # target_pj_names = st.multiselect("Select projects to fetch MergeRequests", pj_names, pj_names)
    # df = make_mergerequest_df(group_id, target_pj_names=target_pj_names, from_streamlit_view=True)
    df = __fetch_mergerequest_dataset(group_id)
    if df.empty:
        st.error("No merge request found in this group.")
        return
    filtered_df = util.filter_by_projects(df, group_id)
    if filtered_df.empty:
        st.error("No merge request found in this project.")

    create_count_of_created_mr_view(filtered_df)
    create_size_view(filtered_df)

    st.markdown("## Detail")
    util.show_table("All of MergeRequests", df)


def create_count_of_created_mr_view(mergerequest_df: pd.DataFrame):
    """Create charts of counting created issues."""
    st.markdown("## Created MergeRequests")
    util.create_count_of_created_view(mergerequest_df)


def create_size_view(mergerequest_df: pd.DataFrame):
    """Create chart to show size of MRs.."""
    st.markdown("## Size of MergeRequests")
    df = mergerequest_df.copy()

    target_branches = sorted(set(df["target_branch"]))
    view_target_branches = st.multiselect(
        "Select target branches you want to see graphs", target_branches, target_branches
    )
    df = df[df["target_branch"].isin(view_target_branches)]

    source_branches = sorted(set(df["source_branch"]))
    view_source_branches = st.multiselect(
        "Select source branches you want to see graphs", source_branches, source_branches
    )
    df = df[df["source_branch"].isin(view_source_branches)]

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
    ).interactive()
    st.altair_chart(chart, use_container_width=True)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def __fetch_mergerequest_dataset(group_id) -> pd.DataFrame:
    return make_mergerequest_df(group_id, from_streamlit_view=True)
