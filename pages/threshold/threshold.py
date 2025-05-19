import pandas as pd
import numpy as np
import taipy.gui.builder as tgb

from utils import update_threshold, update_table, fraud_style

confusion_data = pd.DataFrame({"Predicted": [], "Actual": [], "Values": []})
confusion_layout = None
confusion_options = {"colorscale": "YlOrRd", "displayModeBar": False}
confusion_config = {"scrollZoom": False, "displayModeBar": False}

selected_table = "True Positives"

threshold_lov = np.arange(0, 1, 0.01)

with tgb.Page() as threshold_page:
    tgb.text(
        "### Select a threshold of confidence to filter the transactions", mode="md"
    )
    tgb.slider(
        "{threshold}",
        on_change=update_threshold,
        lov="0.05;0.1;0.15;0.2;0.25;0.3;0.35;0.4;0.45;0.5;0.55;0.6;0.65;0.7;0.75;0.8;0.85;0.9;0.95",
        continuous=False,
    )

    with tgb.layout(columns="2 3"):
        with tgb.part():
            tgb.chart(
                "{confusion_data}",
                type="heatmap",
                z="Values",
                x="Predicted",
                y="Actual",
                layout="{confusion_layout}",
                options="{confusion_options}",
                plot_config="{confusion_config}",
                height="70vh",
            )

        with tgb.part("card"):
            tgb.selector(
                "{selected_table}",
                lov="True Positives;False Positives;True Negatives;False Negatives",
                on_change=update_table,
                label="Selected a table",
                dropdown=True,
            )
            tgb.table(
                "{displayed_table}",
                row_class_name=fraud_style,
                rebuild=True,
                columns=[
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
                ],
            )