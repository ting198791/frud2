from client import Client
import taipy.gui.builder as tgb
from state_class import State
from taipy.gui import notify, navigate


def save_analysis(state: State):
    state.user.remove_transaction_to_analyze(
        state.transaction.transaction_number, state.transaction.is_fraud
    )
    state.transactions_to_analyze = state.user.user_info.transactions_to_analyze.read()
    state.historical_transactions = state.user.user_info.historical_transactions.read()
    notify(state, "success", "Analysis saved!")
    navigate(state, "User")


def create_transaction_card_component():
    with tgb.part("transaction-card"):
        tgb.text("Transaction information")

        tgb.text(
            " ### {transaction.client.first_name} {transaction.client.last_name}",
            mode="md",
        )

        tgb.text(
            "Number {transaction.transaction_id}",
            class_name="h6",
            mode="md",
        )

        tgb.text(
            "**Amount**: ${transaction.amount}",
            mode="md",
        )

        tgb.text(
            "**Category**: {transaction.category}",
            mode="md",
        )

        tgb.text(
            "**Date**: {transaction.trans_date_trans_time}",
            mode="md",
        )

        with tgb.part("more-info"):
            tgb.text(
                "Fraud Confidence",
            )
            with tgb.part("text-center"):
                tgb.toggle(
                    "{transaction.fraud_confidence}",
                    lov=["Low", "Medium", "High"],
                    class_name="{transaction.fraud_confidence}",
                )

            tgb.text("Is this transaction fraudulent?")

            tgb.toggle(
                "{transaction.is_fraud}",
            )
        tgb.button("Save Analysis", on_action=save_analysis, inline=True)
        tgb.button("Share", on_action="{open_dialog}", class_name="plain", inline=True)