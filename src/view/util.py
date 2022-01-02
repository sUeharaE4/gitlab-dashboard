"""Provide utility functions for make view."""
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
    return pd.to_datetime(series, format=fmt)


def filter_by_projects(df: pd.DataFrame, group_id: int, add_pj_name_col: bool = True):
    pj_name_id_map = {p.name: p.id for p in project.list_project(group_id)}
    pj_id_name_map = {v: k for k, v in pj_name_id_map.items()}

    st.markdown("## Filter by projects")
    pj_names = st.multiselect("Select projects you want to see graphs", pj_name_id_map.keys(), pj_name_id_map.keys())
    pj_ids = [pj_name_id_map[n] for n in pj_names]
    if add_pj_name_col:
        df["project_name"] = df["project_id"].map(pj_id_name_map)
    filtered_df = df[df["project_id"].isin(pj_ids)]
    if filtered_df.empty:
        st.error("Selected project(s) has no mergerequests!")
    return filtered_df


def create_count_of_created_view(dataset_df: pd.DataFrame, datetime_col: str = "created_at"):
    df = dataset_df.copy()
    cnt_bar1, cnt_bar2, cnt_bar3 = st.columns(3)
    with cnt_bar1:
        st.markdown("Count at quater")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "Q"),
            use_container_width=True,
        )
    with cnt_bar2:
        st.markdown("Count at month")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "M"),
            use_container_width=True,
        )
    with cnt_bar3:
        st.markdown("Count at week")
        st.altair_chart(
            create_time_count_chart(df, datetime_col, "W"),
            use_container_width=True,
        )


def count_by_datetime(df: pd.DataFrame, datetime_col: str, agg_targets: list[str], agg_methods: list[str], unit: str):
    count_df = df[[datetime_col] + agg_targets].set_index(datetime_col)
    return count_df.resample(unit).agg(agg_methods)


def create_time_count_chart(df: pd.DataFrame, datetime_col: str, unit: str):
    tmp_df = df.copy()
    tmp_df[datetime_col] = to_datetime(tmp_df[datetime_col])
    agg_df = tmp_df[[datetime_col, tmp_df.columns[0]]].set_index(datetime_col).resample(unit).agg(["count"])
    agg_df.columns = ["count"]
    agg_df = agg_df.reset_index()
    x_axis = alt.X(datetime_col, title="datetime")
    y_axis = alt.Y("count", title="count")
    return alt.Chart(agg_df).mark_bar().encode(x=x_axis, y=y_axis).interactive()
