"""Streamlit main page."""
import traceback

import streamlit as st
from streamlit.commands.page_config import set_page_config

from common import GitlabConst
from repository.mapper import GitlabClient
from view.issue import create_issue_view
from view.mergerequest import create_mergerequest_view

VIEW_TARGETS = ("about", "issues", "merge_requests")

set_page_config(layout="wide")
st.title("Gitlab Dashboard")
st.sidebar.markdown("# Select view")
view_target = st.sidebar.radio("", VIEW_TARGETS)
try:
    group_name_id_map = {GitlabClient(id).group.name: id for id in GitlabConst.GROUP_IDS}
    target_group_name = st.sidebar.selectbox("GroupName", group_name_id_map.keys())
    target_group_id = group_name_id_map[target_group_name]

    if view_target == VIEW_TARGETS[0]:
        st.markdown("## About this application")
        st.markdown(
            """
        This application will help you visualize how active your development team is.

        You will be able to see how many issues your team have found and resolved,
         and how development and review is going on.
        """
        )
    elif view_target == VIEW_TARGETS[1]:
        create_issue_view(target_group_id)
    elif view_target == VIEW_TARGETS[2]:
        create_mergerequest_view(target_group_id)
except Exception as e:
    st.error(f"Failed to something: {str(e)}")
    st.error(f"{traceback.format_exc()}")
