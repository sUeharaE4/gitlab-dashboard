"""Provide utility functions for make view."""
from typing import Union

import altair as alt
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from service import project

VIEW_TARGETS = ("issues", "merge_requests")


def show_table(
    markdown_title: str,
    df: pd.DataFrame,
    *,
    height: int = 400,
    editable: bool = False,
    use_checkbox: bool = False,
    check_box_selection_mode="single",
    fit_columns_on_grid_load=False
) -> dict:
    """Show streamlit AgGrid table."""
    st.markdown(markdown_title)
    option_builder = GridOptionsBuilder.from_dataframe(df, editable=editable)
    option_builder.configure_pagination()
    if use_checkbox:
        option_builder.configure_selection(check_box_selection_mode, use_checkbox)
    grid = AgGrid(
        df, option_builder.build(), theme="streamlit", fit_columns_on_grid_load=fit_columns_on_grid_load, height=height
    )
    return grid


def to_datetime(series: pd.Series, fmt: str = "%Y-%m-%dT%H:%M:%S.%f%z") -> pd.Series:
    """Convert string to datetime.

    Parameters
    ----------
    series
        single col of dataframe(str type).
    fmt
        datetime format, by default "%Y-%m-%dT%H:%M:%S.%f%z"

    Returns
    -------
    pd.Series
        converted col.
    """
    return pd.to_datetime(series, format=fmt)


def filter_by_projects(df: pd.DataFrame, group_id: int, add_pj_name_col: bool = True) -> pd.DataFrame:
    """Filter dataframe by user selected project.

    Parameters
    ----------
    df
        base dataset.
    group_id
        id of target group.
    add_pj_name_col
        flags to add col of project_name, by default True

    Returns
    -------
    pd.DataFrame
        filtered dataset.
    """
    pj_name_id_map = {p.name: p.id for p in project.list_project(group_id)}
    pj_id_name_map = {v: k for k, v in pj_name_id_map.items()}

    st.markdown("## Filter by projects")
    pj_names = st.multiselect(
        "Select projects you want to see graphs", sorted(pj_name_id_map.keys()), pj_name_id_map.keys()
    )
    pj_ids = [pj_name_id_map[n] for n in pj_names]
    if add_pj_name_col:
        df["project_name"] = df["project_id"].map(pj_id_name_map)
    filtered_df = df[df["project_id"].isin(pj_ids)]
    if filtered_df.empty:
        st.error("Selected project(s) has no mergerequests!")
    return filtered_df


def create_count_of_created_view(dataset_df: pd.DataFrame, datetime_col: str = "created_at"):
    """Create views of count something like created issues, MRs.

    Parameters
    ----------
    dataset_df
        data source of view.
    datetime_col
        col name of datetime to use aggregate, by default "created_at"
    """
    df = dataset_df.copy()
    cnt_bar1, cnt_bar2, cnt_bar3 = st.columns(3)
    with cnt_bar1:
        st.markdown("Count at quater")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "Q", "project_name"),
            use_container_width=True,
        )
    with cnt_bar2:
        st.markdown("Count at month")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "M", "project_name"),
            use_container_width=True,
        )
    with cnt_bar3:
        st.markdown("Count at week")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "W", "project_name"),
            use_container_width=True,
        )


def count_by_datetime(
    df: pd.DataFrame, datetime_col: str, agg_targets: list[str], agg_methods: list[str], unit: str
) -> pd.DataFrame:
    """Aggregate by datetime.

    Parameters
    ----------
    df
        dataset.
    datetime_col
        col name of datetime col.
    agg_targets
        target col names of aggregation.
    agg_methods
        list of aggregation methods. count, mean, sum and so on.
    unit
        aggregate unit of pandas resampling like D(ay), W(eek), M(onth).

    Returns
    -------
    pd.DataFrame
        aggregated result.
    """
    count_df = df[[datetime_col] + agg_targets].set_index(datetime_col)
    return count_df.resample(unit).agg(agg_methods)


def create_time_count_chart(df: pd.DataFrame, datetime_col: str, unit: str, color_col: Union[str, None] = None):
    """Create a chart of count something by time."""

    def aggregate(df: pd.DataFrame, target_col: str, unit: str):
        agg_df = df[[target_col, df.columns[0]]].set_index(target_col).resample(unit).agg(["count"])
        agg_df.columns = ["count"]
        return agg_df

    tmp_df = df.copy()
    tmp_df[datetime_col] = to_datetime(tmp_df[datetime_col])
    tool_tips = ["count", datetime_col]
    if color_col:
        tool_tips.append(color_col)
        items = set(tmp_df[color_col].to_list())
        agg_dfs = []
        for item in items:
            tmp_agg = aggregate(tmp_df[tmp_df[color_col] == item], datetime_col, unit)
            tmp_agg[color_col] = item
            agg_dfs.append(tmp_agg)
        agg_df = pd.concat(agg_dfs)
    else:
        agg_df = aggregate(tmp_df, datetime_col, unit)
    agg_df = agg_df.reset_index()
    x_axis = alt.X(datetime_col, title="datetime")
    y_axis = alt.Y("count", title="count")
    return alt.Chart(agg_df).mark_bar().encode(x=x_axis, y=y_axis, color=color_col, tooltip=tool_tips).interactive()
