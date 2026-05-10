"""Dashboard / overview page."""
import streamlit as st


def show_dashboard() -> None:
    st.header("Welcome")
    st.info("Select a feature from the sidebar to begin analysing a deal.")
    st.write("Dashboard content can be displayed here.")
