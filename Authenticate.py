import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had a correct password."""

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

    # Initialize session state variables if they don't exist
    if "show_error_message" not in st.session_state:
        st.session_state.show_error_message = False
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = None

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
            st.markdown(hide_bar, unsafe_allow_html=True)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state.password_correct = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state.password_correct = False
            st.session_state.show_error_message = True
            st.markdown(hide_bar, unsafe_allow_html=True)

    def logout():
        """Logs the user out and returns to the login form."""
        st.session_state.password_correct = None
        st.session_state.show_error_message = False
    
    st.sidebar.header(f"Bem vindo!")
    icon = "/Users/Admin/Documents/pages/icon.png"
    st.sidebar.image(icon, use_column_width=True)
    
    # Return True if the username + password is validated.
    if st.session_state.password_correct is True:
        st.sidebar.button("Sair", on_click=logout)
        return True

    # Show inputs for username + password.
    login_form()
    if st.session_state.show_error_message:
        st.error("Usuário ou senha inválidas, tente novamente.")
        st.markdown(hide_bar, unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()