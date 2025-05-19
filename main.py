""" Fraud Detection App """

from data.data import *

import pickle

import numpy as np
import pandas as pd
from taipy.gui import Gui, State
from config.user import User
import traceback

from utils import (
    explain_pred,
    update_threshold,
    update_table,
)


from pages.root import *
from pages.user.user import *
from pages.analysis.analysis import *
from pages.threshold.threshold import *
from pages.transactions.transactions import *
from pages.login.login import *


fraud_text = "No row selected"

threshold = "0.5"

explanation = explanation
original_transactions = data
original_explanation = explanation
specific_transactions = data_transaction

true_positives = None
false_positives = None
true_negatives = None
false_negatives = None
displayed_table = None


transactions = data_transaction


def on_init(state: State) -> None:
    """
    Generate the confusion matrix on start

    Args:
        - state: the state of the app
    """
    state.displayed_table = state.true_positives
    (
        state.true_positives,
        state.true_negatives,
        state.false_positives,
        state.false_negatives,
    ) = update_threshold(state)
    update_table(state)

    state.transactions_to_analyze = state.user.user_info.transactions_to_analyze.read()
    state.historical_transactions = state.user.user_info.historical_transactions.read()


def on_exception(state: State, function_name: str, exception):
    print(f"Exception in {function_name}: {exception}")
    print(traceback.format_exc())


def on_change(state, var_name, var_value):
    if var_name == "user":
        on_init(state)
    if var_name == "transactions_to_analyze":
        transactions_to_analyze_table = state.transactions.loc[
            state.transactions["Transaction Number"].isin(state.transactions_to_analyze)
        ]
        state.transactions_to_analyze_table = transactions_to_analyze_table.round(2)
    elif var_name == "historical_transactions":
        # Extract transaction IDs and decisions
        transaction_ids = [
            item["transaction_id"] for item in state.historical_transactions
        ]
        decisions = [item["decision"] for item in state.historical_transactions]

        # Convert decisions to boolean if necessary
        # Assuming 'decision' is 0 or 1 and 'Fraud' column expects boolean values
        decisions = [bool(decision) for decision in decisions]

        # Create a mapping dictionary
        decision_dict = dict(zip(transaction_ids, decisions))

        # Filter historical transactions and make a copy to avoid SettingWithCopyWarning
        historical_transactions_table = state.transactions[
            state.transactions["Transaction Number"].isin(transaction_ids)
        ].copy()

        # Update the 'Fraud' column using map
        historical_transactions_table["Fraud"] = historical_transactions_table[
            "Transaction Number"
        ].map(decision_dict)

        # Round numeric columns and assign to state
        state.historical_transactions_table = historical_transactions_table.round(2)


def on_navigate(state: State, page):
    if page in ["Transactions", "Analysis", "User", "Threshold-Selection"]:
        state.current_page = page.replace("-", " ")
    if page == "User":
        refresh_newsfeed(state)
    return page


pages = {
    "/": root,
    "Login": login_page,
    "Transactions": transactions_page,
    "Analysis": analysis_page,
    "User": user_page,
    "Threshold-Selection": threshold_page,
}


if __name__ == "__main__":
    stylekit = {"color-primary": "#231E39", "color-secondary": "#FEBB0B"}

    gui = Gui(pages=pages)
    newsfeed_partial = gui.add_partial("")

    # For testing
    User("Vincent")
    User("Alexandre")

    user = User("Florian")

    list_of_users = [
        (s.name, Icon(f"images/{s.name}.png", s.name)) for s in tp.get_scenarios()
    ]

    gui.run(
        title="Fraud Detection Demo",
        dark_mode=False,
        stylekit=stylekit,
        margin="0px",
    )