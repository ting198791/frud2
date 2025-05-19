from utils import explain_pred, fraud_style
import pandas as pd

import taipy.gui.builder as tgb


from deepface import DeepFace
import taipy.gui.builder as tgb
from taipy.gui import invoke_long_callback
from state_class import State
from client import Client, Transaction
from data.data import data
from components.id_card import (
    verify_identity,
    create_id_card_component,
)
from components.transaction_card import (
    create_transaction_card_component,
    save_analysis,
)
from .dialog import *


transaction = Transaction(data.loc[0, "Transaction Number"])
client = Client(data.loc[0, "Client"])
default_image = client.photo
path_to_uploaded_image = None
is_client_verified = None
distance = 0
open_verification_dialog = False


selected_transaction = None
exp_data = pd.DataFrame({"Feature": [], "Influence": []})

waterfall_layout = {
    "margin": {"b": 150},
}


def prcess_image_verification(path_to_uploaded_image, client_photo):
    return DeepFace.verify(path_to_uploaded_image, client_photo)


def finish_identity(state: State, status, result):
    state.is_client_verified = result["verified"]
    state.distance = result["distance"]
    if state.is_client_verified:
        notify(state, "success", "The user has been verified!")
    else:
        notify(state, "error", "The user has not been verified!")


def upload_image(state: State):
    state.is_client_verified = None
    invoke_long_callback(
        state,
        user_function=prcess_image_verification,
        user_function_args=[state.path_to_uploaded_image, state.client.photo],
        user_status_function=finish_identity,
    )


def sum_fraud(specific_transactions):
    return (
        specific_transactions["Fraud"].sum()
        if specific_transactions is not None or not specific_transactions.empty
        else 0
    )


with tgb.Page() as analysis_page:
    tgb.text(
        "This page provides an analysis of a transaction to detect potential fraud cases.",
        mode="md",
    )

    with tgb.layout(columns="3 2 2"):
        with tgb.part("card"):
            tgb.text("### {fraud_text}", mode="md")

            tgb.chart(
                "{exp_data}",
                type="waterfall",
                x="Feature",
                y="Influence",
                layout="{waterfall_layout}",
            )

        create_transaction_card_component()

        create_id_card_component()

    tgb.text(
        "#### Transactions of client: *{client.first_name} {client.last_name}*",
        mode="md",
    )

    with tgb.layout(columns="1 1 1 1 1"):
        tgb.metric(
            title="Number of transactions",
            value="{len(specific_transactions) if specific_transactions is not None or not specific_transactions.empty else 0}",
            type="none",
            height=200,
        )
        tgb.metric(
            title="Number of frauds",
            value="{sum_fraud(specific_transactions)}",
            type="none",
            height=200,
        )
        tgb.metric(
            title="Number of non-frauds",
            value="{len(specific_transactions) - specific_transactions['Fraud'].sum() if specific_transactions is not None or not specific_transactions.empty else 0}",
            type="none",
            height=200,
        )
        tgb.metric(
            title="Average amount",
            value="{specific_transactions['Amount'].mean() if specific_transactions is not None or not specific_transactions.empty else 0}",
            type="none",
            height=200,
        )

    tgb.text("### Transaction History", mode="md")
    tgb.text(
        "Below is the list of transactions for the client. Click on a transaction to see more details or to explain the prediction.",
        mode="md",
    )

    tgb.table(
        "{specific_transactions}",
        row_class_name=fraud_style,
        on_action=explain_pred,
    )

    with tgb.dialog(
        title="Identity verification",
        on_action=verify_identity,
        open="{open_verification_dialog}",
        width="70%",
    ):
        tgb.text(
            "Please upload an image of the client to verify their identity. The system will compare it with the stored image.",
            mode="md",
        )
        tgb.file_selector(
            content="{path_to_uploaded_image}",
            label="Upload image",
            on_action=upload_image,
            extensions=["png", "jpg", "jpeg"],
        )
        with tgb.layout("1 1", class_name="text-center", gap="20px"):
            with tgb.part(
                render="{client.photo}",
            ):
                tgb.text("## Default image", mode="md")
                tgb.image(
                    "{client.photo}",
                    width="200px",
                )
            with tgb.part(render="{path_to_uploaded_image}"):
                tgb.text("## Chosen image", mode="md")
                tgb.image(
                    "{path_to_uploaded_image}",
                    width="200px",
                )

        tgb.text("## Result", mode="md")
        tgb.text(
            "Are the two pictures from the same person? ({client.first_name} {client.last_name})",
            mode="md",
        )

        with tgb.part(
            render="{is_client_verified is not None and is_client_verified}",
            id="verified",
        ):
            tgb.text("**The user has been verified!** The images match.", mode="md")
        with tgb.part(
            render="{is_client_verified is not None and not is_client_verified}",
            id="not-verified",
        ):
            tgb.text(
                "**The user has not been verified!** The images do not match.",
                mode="md",
            )

    build_dialog()