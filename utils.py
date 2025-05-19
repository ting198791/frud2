""" Data Manipulation and Callbacks """

import datetime as dt
import numpy as np
import pandas as pd

from taipy.gui import State, navigate, notify
import xgboost as xgb
from shap import Explainer, Explanation
from sklearn.metrics import confusion_matrix

from client import Transaction, Client

column_names = [
    "amt",
    "zip",
    "city_pop",
    "age",
    "hour",
    "day",
    "month",
    "category_food_dining",
    "category_gas_transport",
    "category_grocery_net",
    "category_grocery_pos",
    "category_health_fitness",
    "category_home",
    "category_kids_pets",
    "category_misc_net",
    "category_misc_pos",
    "category_personal_care",
    "category_shopping_net",
    "category_shopping_pos",
    "category_travel",
]


def fraud_style(_: State, index: int, values: list) -> str:
    """
    Style the transactions table: red if fraudulent

    Args:
        - state: the state of the app
        - index: the index of the row

    Returns:
        - the style of the row
    """
    if values["Fraud Confidence"] == "High":
        return "red-row"
    elif values["Fraud Confidence"] == "Medium":
        return "orange-row"
    return ""


def explain_pred(state: State, var_name: str, payload: dict) -> None:
    """
    When a transaction is selected in the table
    Explain the prediction using SHAP, update the waterfall chart

    Args:
        - state: the state of the app
        - payload: the payload of the event containing the index of the transaction
    """
    idx = payload["index"]
    exp = state.explanation[idx]

    feature_values = [-value for value in list(exp.values)]
    data_values = list(exp.data)

    for i, value in enumerate(data_values):
        if isinstance(value, float):
            value = round(value, 2)
            data_values[i] = value

    names = [f"{name}: {value}" for name, value in zip(column_names, data_values)]

    exp_data = pd.DataFrame({"Feature": names, "Influence": feature_values})
    exp_data["abs_importance"] = exp_data["Influence"].abs()
    exp_data = exp_data.sort_values(by="abs_importance", ascending=False)
    exp_data = exp_data.drop(columns=["abs_importance"])
    exp_data = exp_data[:5]
    state.exp_data = exp_data

    if state.transactions.iloc[idx]["Fraud"]:
        state.fraud_text = "Why is this transaction fraudulent?"
    else:
        state.fraud_text = "Why is this transaction not fraudulent?"

    client = state.transactions.iloc[idx]["Client"]

    state.specific_transactions = state.transactions[
        (state.transactions["Client"] == client)
    ]

    state.selected_transaction = state.transactions.loc[[idx]]

    navigate(state, "Analysis")

    data = getattr(state, var_name)
    state.transaction = Transaction(data.loc[idx, "Transaction Number"])
    state.client = Client(data.loc[idx, "Client"])


def update_threshold(state: State) -> None:
    """
    Change the threshold used to determine if a transaction is fraudulent
    Generate the confusion matrix

    Args:
        - state: the state of the app
    """
    threshold = float(state.threshold)
    results = [
        float(result) > threshold for result in state.transactions["Fraud Value"]
    ]
    state.transactions["Fraud"] = results
    state.transactions = state.transactions
    results = [
        float(result) > threshold
        for result in state.original_transactions["Fraud Value"]
    ]
    state.original_transactions["Fraud"] = results
    state.original_transactions = state.original_transactions
    y_pred = results
    y_true = state.original_transactions["is_fraud"]
    cm = confusion_matrix(y_true, y_pred)
    cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    tp, tn, fp, fn = cm[1][1], cm[0][0], cm[0][1], cm[1][0]

    dataset = state.original_transactions[:10000]
    state.true_positives = dataset[
        (dataset["is_fraud"] == True) & (dataset["Fraud"] == True)
    ]
    state.true_negatives = dataset[
        (dataset["is_fraud"] == False) & (dataset["Fraud"] == False)
    ]
    state.false_positives = dataset[
        (dataset["is_fraud"] == False) & (dataset["Fraud"] == True)
    ]
    state.false_negatives = dataset[
        (dataset["is_fraud"] == True) & (dataset["Fraud"] == False)
    ]

    data = {
        "Values": [
            [fn, tp],
            [tn, fp],
        ],
        "Actual": ["Fraud", "Not Fraud"],
        "Predicted": ["Not Fraud", "Fraud"],
    }

    layout = {
        "annotations": [],
        "xaxis": {"ticks": "", "side": "top"},
        "yaxis": {"ticks": "", "ticksuffix": " "},
    }

    predicted = data["Predicted"]
    actuals = data["Actual"]
    for actual, _ in enumerate(actuals):
        for pred, _ in enumerate(predicted):
            value = data["Values"][actual][pred]
            annotation = {
                "x": predicted[pred],
                "y": actuals[actual],
                "text": f"{str(round(value, 3)*100)[:4]}%",
                "font": {"color": "white" if value < 0.5 else "black", "size": 30},
                "showarrow": False,
            }
            layout["annotations"].append(annotation)

    state.confusion_data = data
    state.confusion_layout = layout
    update_table(state)
    return (
        state.true_positives,
        state.true_negatives,
        state.false_positives,
        state.false_negatives,
    )


def update_table(state: State) -> None:
    """
    Updates the table of transactions displayed

    Args:
        - state: the state of the app
    """
    if state.selected_table == "True Positives":
        state.displayed_table = state.true_positives
    elif state.selected_table == "False Positives":
        state.displayed_table = state.false_positives
    elif state.selected_table == "True Negatives":
        state.displayed_table = state.true_negatives
    elif state.selected_table == "False Negatives":
        state.displayed_table = state.false_negatives