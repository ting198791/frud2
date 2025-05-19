import taipy.gui.builder as tgb
from taipy.gui import navigate
from config.user import User

selected_user = None


def login(state):
    state.user = User(state.selected_user)
    navigate(state, "Transactions")


with tgb.Page() as login_page:
    with tgb.dialog(open=True, title="Login", width="400px"):
        tgb.selector(
            value="{selected_user}",
            lov="{list_of_users}",
            value_by_id=True,
            label="Who are you?",
            class_name="fullwidth",
            on_change=login,
        )