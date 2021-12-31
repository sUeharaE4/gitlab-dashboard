"""Streamlit main page."""
import streamlit as st
from streamlit.commands.page_config import set_page_config

from common import GitlabConst
from view.issue import create_issue_view
from view.mergerequest import create_mergerequest_view

VIEW_TARGETS = ("about", "issues", "merge_requests")

set_page_config(layout="wide")
st.title("Gitlab Dashboard")
st.sidebar.markdown("# Select view")
view_target = st.sidebar.radio("", VIEW_TARGETS)
target_group_id = st.sidebar.selectbox("GroupId", GitlabConst.GROUP_IDS)

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
