import pandas as pd
import datetime as dt
from typing import List
import uuid


import taipy as tp
from taipy.gui import invoke_callback, notify
from taipy import Config, Scope, Scenario, Status
from taipy.core.notification import (
    CoreEventConsumerBase,
    EventEntityType,
    EventOperation,
    Notifier,
)


Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)

# Data Nodes

newsfeed_cfg = Config.configure_data_node(
    id="newsfeed",
    storage_type="csv",
    default_data={
        "news_id": ["2524-1", "6024-1"],
        "sender_username": ["Alexandre", "Vincent"],
        "receiver_username": ["Florian", "Alexandre"],
        "message": ["Hey, check this out", "I have this to show you"],
        "metadata": [
            "2da90c7d74bd46a0caf3777415b3ebd3",
            "798db04aaceb4febd084f1a7c404da93",
        ],
        "message_type": ["Transaction", "Transaction"],
        "timestamp": ["2023-05-08T00:00:00", "2022-01-01T00:00:00"],
        "unseen": [True, True],
    },
)


historical_transactions_cfg = Config.configure_data_node(
    id="historical_transactions",
    storage_type="json",
    default_data=[
        {"transaction_id": "b1324ea98fabfe3da5892bca97df044a", "decision": 0},
        {"transaction_id": "23a7ea9b024ac2e29779d492c43db29d", "decision": 0},
        {"transaction_id": "eeea3ee693080de725eb677b3fc8f20e", "decision": 0},
        {"transaction_id": "4a6d4559b878c7fbc1f82ce90cdedab3", "decision": 0},
    ],
)

transactions_to_analyze_cfg = Config.configure_data_node(
    id="transactions_to_analyze",
    storage_type="json",
    default_data=[
        "6337ebf236753a68a2697295960a30b7",
        "5558dbb992a7ac2e4e44a3a19b44c6ec",
        "41e4c34661b52aabd9f953f25a9088d6",
        "bfb6c721657f3116d4533879167db922",
        "2da90c7d74bd46a0caf3777415b3ebd3",
    ],
)


user_cfg = Config.configure_scenario(
    id="user_info",
    additional_data_node_configs=[
        transactions_to_analyze_cfg,
        historical_transactions_cfg,
        newsfeed_cfg,
    ],
)


Config.export("config/config.toml")


class User:
    def __init__(self, username: str, state_id: str = None):
        self.username: str = username

        users: List[Scenario] = [
            s for s in tp.get_scenarios() if s.name == self.username
        ]
        if len(users) == 0:
            self.user_info = tp.create_scenario(user_cfg, name=self.username)
        else:
            self.user_info = users[0]

    def get_transactions_to_analyze(self) -> List[str]:
        return self.user_info.transactions_to_analyze.read()

    def write_transactions_to_analyze(self, transactions_to_analyze):
        self.user_info.transactions_to_analyze.write(transactions_to_analyze)

    def get_newsfeed(self) -> pd.DataFrame:
        return self.user_info.newsfeed.read()

    def write_newsfeed(self, newsfeed):
        newsfeed["timestamp"] = pd.to_datetime(newsfeed["timestamp"]).apply(
            lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")
        )
        self.user_info.newsfeed.write(newsfeed)

    def add_transaction_to_analyze(self, transaction):
        transactions_to_analyze = self.get_transactions_to_analyze()
        if transaction in transactions_to_analyze:
            return
        transactions_to_analyze.append(transaction)
        self.write_transactions_to_analyze(transactions_to_analyze)

    def remove_transaction_to_analyze(self, transaction, decision=0):
        transactions_to_analyze = self.get_transactions_to_analyze()
        historical_transactions = self.user_info.historical_transactions.read()
        if transaction not in transactions_to_analyze:
            return
        transactions_to_analyze.remove(transaction)

        historical_transactions.append(
            {"transaction_id": transaction, "decision": decision}
        )

        self.user_info.historical_transactions.write(historical_transactions)
        self.write_transactions_to_analyze(transactions_to_analyze)

    def share_transaction(
        self, transaction_number: str, receiver_username: str, comment: str
    ):
        news = pd.DataFrame(
            {
                "news_id": [str(uuid.uuid4())],
                "sender_username": [self.username],
                "receiver_username": [receiver_username],
                "message": [comment],
                "metadata": [transaction_number],
                "message_type": ["Transaction"],
                "timestamp": [dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")],
                "unseen": [True],
            }
        )
        User(receiver_username).add_to_newsfeed(news)

    def add_to_newsfeed(self, news: pd.DataFrame):
        newsfeed = self.get_newsfeed()
        newsfeed = pd.concat([newsfeed, news], ignore_index=True)
        newsfeed["timestamp"] = pd.to_datetime(
            newsfeed["timestamp"], format="%Y-%m-%dT%H:%M:%S"
        )
        self.write_newsfeed(newsfeed)


"""
def notify_user(state, data_node):
    if data_node.config_id == "uploaded_file":
        pass
    elif data_node.config_id == "clean_uploaded_file":
        state.clean_data_dn = data_node
        state.logs += "Cleaned file loaded.\n"
        state.logs += f"Waiting to compare {len(data_node.read())} rates to the existing database...\n"
    elif data_node.config_id == "rates_not_included":
        state.rates_not_included = data_node.read()
        if not state.rates_not_included.empty:
            error_messages = "\n".join(
                f"    Error in sheet '{row['SheetName']}'"
                for index, row in state.rates_not_included.iterrows()
            )
        else:
            error_messages = ""
        state.logs += f"{error_messages}\n"
    elif data_node.config_id == "compared_rates":
        state.logs += "Rebasing the results...\n"
    elif data_node.config_id == "rebased_compared_rates":
        state.rebased_compared_rates = data_node.read()
        state.logs = ""
        state.rebased_compared_rates_path = data_node.path
        notify(state, "success", "Comparison complete.")


class SpecificCoreConsumer(CoreEventConsumerBase):
    def __init__(self, gui):
        self.gui = gui
        reg_id, queue = (
            Notifier.register()
        )  # Adapt the registration to the events you want to listen to
        super().__init__(reg_id, queue)

    def process_event(self, event):
        # with Authorize(login(ADMIN, ADMIN)):
        if (
            event.entity_type == EventEntityType.JOB
            and event.operation == EventOperation.UPDATE
        ):
            if (
                event.attribute_name == "status"
                and event.attribute_value == Status.COMPLETED
            ):
                task = tp.get(event.entity_id).task
                for data_node in task.output.values():
                    try:
                        self.gui.broadcast_callback(notify_user, [data_node])
                    except Exception as e:
                        print(e)
"""