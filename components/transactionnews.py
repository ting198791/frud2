import taipy.gui.builder as tgb
import pandas as pd
from taipy.gui import notify
from state_class import State
import os


def accept(state: State, news_id: str):
    try:
        # Copy the data from the state and select the specific row
        data = state.newsfeed.newsfeed_df.copy()
        data.set_index("news_id", inplace=True)

        if news_id not in data.index:
            raise KeyError(f"news_id {news_id} not found in the DataFrame.")

        transaction_to_add_to_transactions_to_analyze = str(
            data.at[news_id, "metadata"]
        )
        state.user.add_transaction_to_analyze(
            transaction_to_add_to_transactions_to_analyze
        )
        delete_news(state, news_id)
        state.transactions_to_analyze = state.user.get_transactions_to_analyze()
        notify(state, "success", "Transaction added")
    except ValueError:
        print(f"Invalid news_id: {news_id}. Must be an integer.")


def delete_news(state: State, news_id: str):
    state.newsfeed.remove_news(news_id)
    state.newsfeed_partial.update_content(state, state.newsfeed.create_newsfeed())


def get_transaction(data, metadata):
    return data[data["Transaction Number"] == metadata]


class TransactionNews:
    def __init__(
        self,
        sender_username,
        receiver_username,
        message,
        metadata,
        message_type,
        news_id,
        timestamp,
        unseen=True,
    ):
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.message = message
        self.metadata = metadata
        self.message_type = message_type
        self.news_id = news_id
        self.timestamp: pd.Timestamp = timestamp
        self.unseen = unseen

    def create_news(self):
        with tgb.part("transaction"):
            with tgb.layout(
                columns="80px 1", gap="20px", class_name="align-columns-center"
            ):
                tgb.image(
                    (
                        f"images/{self.sender_username}.png"
                        if os.path.exists(f"images/{self.sender_username}.png")
                        else "images/recommendation.png"
                    ),
                    class_name="recommendation_image",
                    width="60px",
                )
                with tgb.part():
                    tgb.text(
                        self.timestamp.strftime("%a %d %b %Y"),
                        class_name="timestamp",
                    )
                    tgb.text("### Transaction Notification", mode="md")
                    with tgb.layout(columns="1 200px"):
                        with tgb.part():
                            tgb.text(
                                f"{self.sender_username} is sending you a transaction:\n\n*{self.message}*",
                                mode="md",
                            )

                        with tgb.part("container"):
                            with tgb.layout(
                                columns="1 20px",
                                columns__mobile="1 20px",
                                class_name="align-columns-center",
                            ):
                                tgb.button(
                                    "Add transaction",
                                    on_action=accept,
                                    id=self.news_id,
                                    class_name="fullwidth favorites",
                                )
                                tgb.button(
                                    "{DELETE_BUTTON}",
                                    on_action=delete_news,
                                    id=self.news_id,
                                    class_name="fullwidth hide",
                                )

            with tgb.expandable(title="Show the transaction", expanded=False):
                tgb.table(
                    "{get_transaction(data, '" + str(self.metadata) + "')}",
                    show_all=True,
                )