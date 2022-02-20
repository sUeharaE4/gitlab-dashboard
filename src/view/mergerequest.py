"""Create issue view."""
import copy

import altair as alt
import pandas as pd
import streamlit as st

from service.mergerequest import make_mergerequest_df
from view import util

size_view_tooltip = [
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
]


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
    create_changed_amount_view(filtered_df)

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

    # if target project never merged requests, merged_by-username does not exists.
    tooltip = copy.deepcopy(size_view_tooltip)
    if "merged_by-username" not in df.columns:
        tooltip.remove("merged_by-username")
    chart = (
        alt.Chart(df)
        .mark_point()
        .encode(
            alt.X("mean_changes", title="mean changes (total changes / commits)"),
            alt.Y("mean_change_files", title="mean change files(sum of change files / commits)"),
            color="project_name",
            size=alt.Size("user_notes_count", bin=True),
            tooltip=tooltip,
        )
    ).interactive()
    st.altair_chart(chart, use_container_width=True)


def create_changed_amount_view(merge_request_df: pd.DataFrame):
    """Create chart to show how many changes in the repository."""
    st.markdown("## Amount of changes.")
    st.markdown(
        "Check how much of each file has been modified and the number of modifications. "
        "Files that are changed frequently and in large amounts may have too much responsibility."
    )
    df = merge_request_df.copy()

    target_projects = sorted(set(df["project_name"]))
    view_target_project = st.selectbox("Select target project you want to see graphs", target_projects, 0)
    df = df[df["project_name"] == view_target_project]
    total_diffs = dict()
    for commit_diff in df["diff"].to_list():
        for file_path, diff in commit_diff.items():
            if file_path not in total_diffs:
                total_diffs[file_path] = dict()
            total_diffs[file_path]["add"] = total_diffs[file_path].get("add", 0) + diff["add"]
            total_diffs[file_path]["del"] = total_diffs[file_path].get("del", 0) + diff["del"]
            total_diffs[file_path]["change_cnt"] = total_diffs[file_path].get("change_cnt", 0) + diff["change_cnt"]
    diff_df = pd.DataFrame(
        [
            {"file_path": k, "add": v["add"], "del": v["del"], "change_cnt": v["change_cnt"]}
            for k, v in total_diffs.items()
        ]
    )
    diff_df["total_changes"] = diff_df["add"] + diff_df["del"]
    diff_df["add/del"] = diff_df["add"] / (diff_df["del"] + 1)
    diff_df = diff_df.sort_values("total_changes", ascending=False).reset_index()

    top_n = st.slider("Set top N files changes a lot of lines", 1, diff_df.shape[0], min(1000, diff_df.shape[0]))
    diff_df = diff_df[diff_df.index < top_n]

    tooltip = diff_df.columns.tolist()
    chart = (
        alt.Chart(diff_df)
        .mark_point()
        .encode(
            alt.X("change_cnt", title="change times"),
            alt.Y("total_changes", title="total changes"),
            size="add/del",
            tooltip=tooltip,
        )
    ).interactive()
    st.altair_chart(chart, use_container_width=True)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def __fetch_mergerequest_dataset(group_id) -> pd.DataFrame:
    return make_mergerequest_df(group_id, from_streamlit_view=True)
