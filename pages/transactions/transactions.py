from taipy.gui import notify
import taipy.gui.builder as tgb

from .charts import (
    gen_amt_figure,
    gen_cat_figure,
    gen_day_figure,
    gen_gender_figure,
    gen_hour_figure,
    plot_age_distribution,
    plot_client_density_by_state,
    plot_client_density_heatmap,
    plot_gender_distribution,
    plot_fraud_rate_by_state,
    plot_transactions_by_category_state,
    plot_transactions_sunburst,
    plot_top_categories_back_to_back,
    plot_transactions_sunburst_state_category,
)
from state_class import State
import pandas as pd
from utils import explain_pred, fraud_style


selected_representation = "Fraud"


with tgb.Page() as transactions_page:
    tgb.text(
        "### *Key* Highlights:\n"
        "- **Interactive Transaction Table**: Explore all transactions and select any to explain the prediction.\n"
        "- **Toggleable Analysis Views**: Switch between Fraud, Clients, and Transactions analyses using the toggle button.\n"
        "- **Comprehensive Visualizations**: Gain insights from various charts displaying data distributions and patterns.\n",
        mode="md",
    )

    with tgb.expandable(title="All transactions", expanded=False):
        tgb.text("Select a transaction to explain the prediction", mode="md")

        tgb.table(
            "{transactions}",
            on_action=explain_pred,
            row_class_name=fraud_style,
            filter=True,
            rebuild=True,
        )

    tgb.toggle(
        "{selected_representation}",
        lov=[
            "Fraud",
            "Clients",
            "Transactions",
        ],
    )

    with tgb.part(render="{selected_representation=='Clients'}"):
        tgb.text("### Client **Analysis**", mode="md")
        tgb.text(
            "Here are different charts about the clients in the dataset, such as age distribution, gender distribution, and client density by state.",
            mode="md",
        )

        with tgb.layout("1 1"):
            tgb.chart(figure="{plot_client_density_by_state(data_clients)}")
            tgb.chart(figure="{plot_client_density_heatmap(data_clients)}")
            tgb.chart(figure="{plot_gender_distribution(data_clients)}")
            tgb.chart(figure="{plot_age_distribution(data_clients)}")

    with tgb.part(render="{selected_representation=='Fraud'}"):
        tgb.text("### Fraud **Analysis**", mode="md")
        tgb.text(
            "Here are different charts about the fraud in the dataset, such as fraud rate by state, and amount, category, day, and hour distribution.",
            mode="md",
        )

        with tgb.layout("1 1"):
            tgb.chart(figure="{plot_fraud_rate_by_state(original_transactions)}")

            tgb.chart(figure="{gen_amt_figure(original_transactions)}")
            tgb.chart(figure="{gen_cat_figure(original_transactions)}")
            tgb.chart(figure="{gen_day_figure(original_transactions)}")
            tgb.chart(figure="{gen_hour_figure(original_transactions)}")
            tgb.chart(figure="{gen_gender_figure(original_transactions)}")

    with tgb.part(render="{selected_representation=='Transactions'}"):
        tgb.text("### Transactions **Analysis**", mode="md")
        tgb.text(
            "Here are different charts about the transactions in the dataset, such as transactions by category and state.",
            mode="md",
        )

        with tgb.layout("1 1"):
            tgb.chart(
                figure="{plot_transactions_sunburst_state_category(original_transactions)}"
            )
            tgb.chart(
                figure="{plot_top_categories_back_to_back(original_transactions)}"
            )