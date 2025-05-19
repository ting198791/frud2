import pandas as pd
import random
from .preprocess_data import get_all_images_with_folders
import pickle

from shap import Explainer, Explanation

import xgboost as xgb
import datetime as dt

from taipy.gui import notify
from state_class import State


def generate_transactions(
    state: State,
    df: pd.DataFrame,
    model: xgb.XGBRegressor,
    threshold: float,
    start_date="2020-06-21",
    end_date="2030-01-01",
):
    """
    Generates a DataFrame of transactions with the fraud prediction

    Args:
        - state: the state of the app
        - df: the DataFrame containing the transactions
        - model: the model used to predict the fraud
        - threshold: the threshold used to determine if a transaction is fraudulent
        - start_date: the start date of the transactions
        - end_date: the end date of the transactions

    Returns:
        - a DataFrame of transactions with the fraud prediction
    """
    start_date = str(start_date)
    end_date = str(end_date)
    start_date_dt = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")
    # Make sure the dates are separated by at least one day
    if (end_date_dt - start_date_dt).days < 1:
        notify(state, "error", "The start date must be before the end date")
        raise Exception("The start date must be before the end date")
    # Make sure that start_date is between 2020-06-21 and 2020-06-30
    if not (dt.datetime(2020, 6, 21) <= start_date_dt <= dt.datetime(2020, 6, 30)):
        notify(
            state, "error", "The start date must be between 2020-06-21 and 2020-06-30"
        )
        raise Exception("The start date must be between 2020-06-21 and 2020-06-30")
    df["age"] = dt.date.today().year - pd.to_datetime(df["dob"]).dt.year
    df["hour"] = pd.to_datetime(df["trans_date_trans_time"]).dt.hour
    df["day"] = pd.to_datetime(df["trans_date_trans_time"]).dt.dayofweek
    df["month"] = pd.to_datetime(df["trans_date_trans_time"]).dt.month
    test = df[
        [
            "category",
            "amt",
            "zip",
            "city_pop",
            "age",
            "hour",
            "day",
            "month",
            "is_fraud",
        ]
    ]
    test = pd.get_dummies(test, drop_first=True)
    test = test[df["trans_date_trans_time"].between(str(start_date), str(end_date))]

    X_test = test.drop("is_fraud", axis="columns")
    X_test_values = X_test.values

    transactions = df[
        df["trans_date_trans_time"].between(str(start_date), str(end_date))
    ]
    raw_results = model.predict(X_test_values)
    results = [str(min(1, round(result, 2))) for result in raw_results]
    transactions.insert(0, "fraud_value", results)
    # Low if under 0.2, Medium if under 0.5, High if over 0.5
    results = ["Low" if float(result) < 0.2 else "Medium" for result in raw_results]
    for i, result in enumerate(results):
        if result == "Medium" and float(raw_results[i]) > 0.5:
            results[i] = "High"
    transactions.insert(0, "Fraud Confidence", results)
    results = [float(result) > threshold for result in raw_results]
    transactions.insert(0, "Fraud", results)

    explainer = Explainer(model)
    sv = explainer(X_test)
    explanation = Explanation(sv, sv.base_values, X_test, feature_names=X_test.columns)
    # Drop Unnamed: 0 column if it exists
    if "Unnamed: 0" in transactions.columns:
        transactions = transactions.drop(columns=["Unnamed: 0"])
    return transactions, explanation


PATH_TO_TRAINING_DATASET = "data/trainset/"
PATH_TO_DATA = "data/fraud_data.csv"

images_dict = get_all_images_with_folders(PATH_TO_TRAINING_DATASET)
threshold = "0.5"

with open("model.pkl", "rb") as model:
    model = pickle.load(model)


data = pd.read_csv(PATH_TO_DATA)

data["trans_num"] = data["trans_num"].apply(lambda x: x[:8])
data["cc_num"] = data["cc_num"].apply(lambda x: int(str(x)[:8]))

data, explanation = generate_transactions(None, data, model, float(threshold))
# Read the data and select relevant columns


data = data[
    [
        "first",
        "last",
        "gender",
        "street",
        "city",
        "state",
        "zip",
        "lat",
        "long",
        "city_pop",
        "job",
        "is_fraud",
        "trans_num",
        "trans_date_trans_time",
        "cc_num",
        "merchant",
        "category",
        "amt",
        "Fraud",
        "fraud_value",
        "Fraud Confidence",
        "age",
        "hour",
        "day",
    ]
]

# Rename columns for better readability
data.rename(
    columns={
        "first": "First Name",
        "last": "Last Name",
        "gender": "Gender",
        "street": "Street Address",
        "city": "City",
        "state": "State",
        "zip": "ZIP Code",
        "lat": "Latitude",
        "long": "Longitude",
        "city_pop": "City Population",
        "job": "Job Title",
        "trans_num": "Transaction Number",
        "cc_num": "Credit Card Number",
        "merchant": "Merchant",
        "category": "Category",
        "amt": "Amount",
        "age": "Age",
        "hour": "Hour",
        "day": "Day",
        "fraud_value": "Fraud Value",
    },
    inplace=True,
)

data["Client"] = data.apply(
    lambda row: row["First Name"] + " " + row["Last Name"], axis=1
)

data_transaction = data[
    [
        "Fraud",
        "Fraud Confidence",
        "Client",
        "Amount",
        "Category",
        "Merchant",
        "Transaction Number",
        "Credit Card Number",
        "trans_date_trans_time",
        "is_fraud",
        "Fraud Value",
    ]
].reset_index(drop=True)

data_clients = (
    data[
        [
            "First Name",
            "Last Name",
            "Gender",
            "Street Address",
            "Client",
            "City",
            "State",
            "ZIP Code",
            "Job Title",
            "Age",
            "Latitude",
            "Longitude",
            "City Population",
        ]
    ]
    .groupby(by=["Client"])
    .first()
    .reset_index(drop=False)
)

# Generate a random age for each client (range 18-75)
data_clients["Photo"] = list(images_dict.values())[: len(data_clients)]
data_clients.to_csv("data/clients.csv", index=False)