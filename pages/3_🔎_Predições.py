import streamlit as st
from Authenticate import check_password

st.set_page_config(
    page_title="Predições",
    page_icon="🔎",
    )

hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""

check_password() 
