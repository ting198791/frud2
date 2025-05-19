from taipy.gui import Icon, navigate
import taipy.gui.builder as tgb

menu_lov = [
    ("Transactions", Icon("images/transactions.png", "Transactions")),
    ("Analysis", Icon("images/analysis.png", "Analysis")),
    ("User", Icon("images/profile.png", "User")),
    ("Threshold Selection", Icon("images/threshold.png", "Threshold Selection")),
]

current_page = "Transactions"


def open_dialog_user(state):
    navigate(state, "Login")


def menu_fct(state, var_name, var_value):
    """Function that is called when there is a change in the menu control."""
    state.current_page = var_value["args"][0].replace(" ", "-")
    navigate(state, state.current_page)


with tgb.Page() as root:
    tgb.menu(label="Navigation", lov=menu_lov, on_action=menu_fct)
    tgb.toggle(theme=True)

    with tgb.part("header sticky"):
        with tgb.layout(
            "100px 1 150px 60px",
            columns__mobile="1",
            class_name="header-content",
        ):
            tgb.image("favicon.png", width="50px")
            tgb.text("#### Fraud **Detection** - *{current_page.title()}*", mode="md")

            with tgb.part():
                tgb.text("Welcome, ", mode="md", inline=True)
                tgb.button(
                    "{user.username if user is not None else 'Login'}",
                    inline=True,
                    id="dialog_button",
                    on_action="{open_dialog_user}",
                )
                tgb.text("!", mode="md", inline=True)
            tgb.image(
                "images/{user.username if user is not None else 'Login'}.png",
                width="40px",
                class_name="icon",
            )

    tgb.html("br")

    with tgb.part("content"):
        tgb.content()