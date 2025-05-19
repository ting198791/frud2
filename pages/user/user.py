import taipy.gui.builder as tgb
from utils import explain_pred, fraud_style
from state_class import State
from components.newsfeed import *


newsfeed = None
transactions_to_analyze = None
historical_transactions = None
transactions_to_analyze_table = None
historical_transactions_table = None


def refresh_newsfeed(state: State):
    state.newsfeed = NewsFeed(state.user)
    state.newsfeed.set_newsfeed_df_to_seen()
    state.newsfeed_partial.update_content(state, state.newsfeed.create_newsfeed())


with tgb.Page() as user_page:

    tgb.text(
        "Here is the list of transactions to analyze. You have *{len(transactions_to_analyze_table) if transactions_to_analyze_table is not None or not transactions_to_analyze_table.empty else 0} transactions* in this table.",
        mode="md",
    )

    tgb.text("### Transactions to **analyze**", mode="md")
    tgb.table(
        "{transactions_to_analyze_table}",
        on_action=explain_pred,
        row_class_name=fraud_style,
        filter=True,
        rebuild=True,
    )

    with tgb.expandable(title="Previous Transactions", expanded=False):
        tgb.table(
            "{historical_transactions_table}",
            on_action=explain_pred,
            row_class_name=fraud_style,
            filter=True,
            rebuild=True,
        )

    tgb.text("## Notifications", mode="md")
    tgb.button("Refresh news feed", on_action=refresh_newsfeed)
    tgb.part(partial="{newsfeed_partial}")