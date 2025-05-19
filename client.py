from data.data import data_transaction, data_clients


class Client:
    def __init__(self, client):
        """
        Initializes a Client object from a DataFrame row.

        Parameters:
            row (pd.Series): A row from the DataFrame representing a client.
        """
        row = data_clients[data_clients["Client"] == client].iloc[0]
        self.first_name = row["First Name"]
        self.last_name = row["Last Name"]
        self.gender = row["Gender"]
        self.street_address = row["Street Address"]
        self.city = row["City"]
        self.state = row["State"]
        self.zip_code = row["ZIP Code"]
        self.latitude = row["Latitude"]
        self.longitude = row["Longitude"]
        self.city_population = row["City Population"]
        self.job_title = row["Job Title"]
        self.age = row["Age"]
        self.photo = row["Photo"]

    def __repr__(self):
        return (
            f"Client({self.first_name} {self.last_name}, {self.age} years old, "
            f"{self.gender}, Job: {self.job_title}, City: {self.city})"
        )


class Transaction:
    def __init__(self, transaction_number):
        """
        Initializes a Client object from a DataFrame row.

        Parameters:
            row (pd.Series): A row from the DataFrame representing a client.
        """

        row = data_transaction[
            data_transaction["Transaction Number"] == transaction_number
        ].iloc[0]
        self.client = Client(row["Client"])
        self.is_fraud = row["is_fraud"]
        self.fraud_confidence = row["Fraud Confidence"]
        self.trans_date_trans_time = row["trans_date_trans_time"]
        self.merchant = row["Merchant"]
        self.category = row["Category"]
        self.amount = row["Amount"]
        self.transaction_number = row["Transaction Number"]
        self.cc_number = row["Credit Card Number"]

    def __repr__(self):
        return f"Transaction - {self.transaction_number} - {self.client.first_name} - {self.client.last_name}"