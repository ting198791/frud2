import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def gen_amt_figure(transactions: pd.DataFrame) -> px.histogram:
    """
    Generates a histogram of transaction amounts for fraudulent and non-fraudulent transactions.

    Args:
        transactions: The transactions DataFrame.

    Returns:
        A Plotly histogram figure.
    """
    # Map fraud boolean to labels
    df = transactions.copy()
    df["Fraudulence"] = df["Fraud"].map({True: "Fraud", False: "Not Fraud"})

    # Create histogram using Plotly Express
    fig = px.histogram(
        df,
        x="Amount",
        color="Fraudulence",
        nbins=200,
        histnorm="probability",
        opacity=0.8,
        color_discrete_map={"Not Fraud": "#4A4", "Fraud": "#A33"},
        title="Transaction Amount Distribution",
        labels={"amt": "Amount ($)", "y": "Probability"},
    )
    fig.update_layout(barmode="overlay", showlegend=True, xaxis=dict(range=[0, 2000]))
    fig.update_traces(xbins=dict(start=0, end=2000, size=10))
    return fig


def gen_gender_figure(transactions: pd.DataFrame) -> px.bar:
    """
    Generates a bar chart showing the distribution of fraud by gender.

    Args:
        transactions: The transactions DataFrame.

    Returns:
        A Plotly bar chart figure.
    """
    # Calculate percentages

    fraud_gender = (
        transactions.groupby(["Fraud", "Gender"]).size().reset_index(name="count")
    )

    # Calculate percentages using transform
    fraud_gender["Percentage"] = fraud_gender.groupby("Fraud")["count"].transform(
        lambda x: x / x.sum()
    )

    # Map fraud boolean to labels
    fraud_gender["Fraudulence"] = fraud_gender["Fraud"].map(
        {True: "Fraud", False: "Not Fraud"}
    )

    # Create bar chart
    fig = go.Figure()
    for gender in fraud_gender["Gender"].unique():
        df_gender = fraud_gender[fraud_gender["Gender"] == gender]
        fig.add_trace(
            go.Bar(x=df_gender["Fraudulence"], y=df_gender["Percentage"], name=gender)
        )

    fig.update_layout(
        title="Distribution of Fraud by Gender",
        xaxis_title="Fraudulence",
        yaxis_title="Percentage",
        barmode="group",
    )
    return fig


def gen_cat_figure(transactions: pd.DataFrame) -> px.bar:
    """
    Generates a bar chart showing the difference in fraudulence by category.

    Args:
        transactions: The transactions DataFrame.

    Returns:
        A Plotly bar chart figure.
    """
    # Calculate normalized counts
    fraud_counts = (
        transactions[transactions["Fraud"]]["Category"]
        .value_counts(normalize=True)
        .fillna(0)
    )
    not_fraud_counts = (
        transactions[~transactions["Fraud"]]["Category"]
        .value_counts(normalize=True)
        .fillna(0)
    )

    # Calculate differences
    diff = (fraud_counts - not_fraud_counts).fillna(0).reset_index()
    diff.columns = ["Category", "Difference"]
    diff = diff.sort_values(by="Difference", ascending=False)

    # Create bar chart using Plotly Express
    fig = px.bar(
        diff,
        x="Category",
        y="Difference",
        color="Difference",
        color_continuous_midpoint=0,
        color_continuous_scale="RdBu",
        title="Difference in Fraudulence by Category (Positive = More Fraudulent)",
        labels={"Difference": "Difference in Proportion"},
    )
    return fig


def gen_hour_figure(transactions: pd.DataFrame) -> go.Figure:
    """
    Generates a polar bar chart showing the distribution of fraudulent and non-fraudulent transactions by hour.

    Args:
        transactions: The transactions DataFrame.

    Returns:
        A Plotly polar bar chart figure.
    """
    # Prepare data
    # Calculate counts per hour for fraud and non-fraud
    fraud_counts = (
        transactions[transactions["Fraud"]]["Hour"].value_counts().sort_index()
    )
    non_fraud_counts = (
        transactions[~transactions["Fraud"]]["Hour"].value_counts().sort_index()
    )

    # Ensure all hours are represented
    all_hours = pd.DataFrame({"Hour": range(24)})
    fraud_counts = all_hours.merge(
        fraud_counts.rename("Fraud"), left_on="Hour", right_index=True, how="left"
    ).fillna(0)
    non_fraud_counts = all_hours.merge(
        non_fraud_counts.rename("Not Fraud"),
        left_on="Hour",
        right_index=True,
        how="left",
    ).fillna(0)

    # Prepare data for plotting
    df = fraud_counts.merge(non_fraud_counts, on="Hour")
    total_non_fraud = df["Not Fraud"].sum()
    total_fraud = df["Fraud"].sum()

    df["Fraud_Percentage"] = df["Fraud"] / total_fraud
    df["Not_Fraud_Percentage"] = df["Not Fraud"] / total_non_fraud

    # Set theta (angle) for each hour
    df["Theta"] = df["Hour"] * 15  # Each hour corresponds to 15 degrees
    theta = df["Theta"].tolist()
    width = [15] * 24  # Width of each bar

    # Prepare radial values
    r_fraud = df["Fraud_Percentage"].tolist()
    r_not_fraud = df["Not_Fraud_Percentage"].tolist()

    # Prepare tick texts
    tickvals = df["Theta"]
    ticktexts = df["Hour"].astype(str)

    # Create the figure
    fig = go.Figure()

    # Add non-fraud trace
    fig.add_trace(
        go.Barpolar(
            r=r_not_fraud,
            theta=theta,
            width=width,
            name="Not Fraud",
            marker_color="#4A4",
            marker_line_color="white",
            marker_line_width=1,
            opacity=0.8,
        )
    )

    # Add fraud trace
    fig.add_trace(
        go.Barpolar(
            r=r_fraud,
            theta=theta,
            width=width,
            name="Fraud",
            marker_color="#A33",
            marker_line_color="white",
            marker_line_width=1,
            opacity=0.8,
        )
    )

    # Update the layout
    fig.update_layout(
        title="Distribution of Transactions by Hour",
        polar=dict(
            hole=0.4,
            radialaxis=dict(
                showticklabels=False,
                ticks="",
                linewidth=2,
                linecolor="white",
                showgrid=False,
            ),
            angularaxis=dict(
                tickvals=tickvals,
                ticktext=ticktexts,
                ticks="",
                rotation=90,
                direction="clockwise",
                period=360,
                linecolor="white",
                gridcolor="white",
                showline=True,
                showticklabels=True,
            ),
        ),
        legend=dict(
            title="Fraud Status", orientation="h", x=0.5, xanchor="center", y=-0.1
        ),
    )

    return fig


def gen_day_figure(transactions: pd.DataFrame) -> px.bar_polar:
    """
    Generates a polar bar chart showing the distribution of fraud by day of the week.

    Args:
        transactions: The transactions DataFrame.

    Returns:
        A Plotly polar bar chart figure.
    """
    # Map day numbers to names
    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df = transactions.copy()
    df["Day"] = df["Day"].map(dict(enumerate(day_names)))

    # Prepare data
    fraud_days = df[df["Fraud"]]["Day"].value_counts(normalize=True).reset_index()
    fraud_days.columns = ["Day", "Percentage"]
    fraud_days["Fraudulence"] = "Fraud"

    not_fraud_days = df[~df["Fraud"]]["Day"].value_counts(normalize=True).reset_index()
    not_fraud_days.columns = ["Day", "Percentage"]
    not_fraud_days["Fraudulence"] = "Not Fraud"

    day_data = pd.concat([fraud_days, not_fraud_days], ignore_index=True)

    # Ensure days are in correct order
    day_data["Day"] = pd.Categorical(
        day_data["Day"], categories=day_names, ordered=True
    )
    day_data = day_data.sort_values("Day")

    # Create polar bar chart using Plotly Express
    fig = px.bar_polar(
        day_data,
        r="Percentage",
        theta="Day",
        color="Fraudulence",
        color_discrete_map={"Not Fraud": "#4A4", "Fraud": "#A33"},
        title="Distribution of Fraud by Day",
        labels={"Percentage": "Percentage", "Day": "Day of Week"},
        start_angle=90,
        direction="clockwise",
    )
    fig.update_traces(opacity=0.8)
    fig.update_layout(
        polar=dict(
            hole=0.4,
            angularaxis=dict(
                tickmode="array",
                tickvals=day_names,
                ticktext=day_names,
                rotation=90,
                direction="clockwise",
            ),
            radialaxis=dict(showticklabels=False),
        )
    )
    return fig


def plot_gender_distribution(data_clients: pd.DataFrame):
    """
    Creates a bar chart showing the distribution of clients by gender.

    Args:
        data_clients: DataFrame containing client information.

    Returns:
        A Plotly Figure object representing the bar chart.
    """
    gender_counts = data_clients["Gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]
    fig = px.bar(
        gender_counts,
        x="Gender",
        y="Count",
        title="Distribution of Clients by Gender",
        labels={"Count": "Number of Clients"},
        color="Gender",
        color_discrete_map={"F": "#FF69B4", "M": "#1E90FF"},
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_age_distribution(data_clients: pd.DataFrame):
    """
    Creates a histogram showing the distribution of clients by age.

    Args:
        data_clients: DataFrame containing client information.

    Returns:
        A Plotly Figure object representing the histogram.
    """
    fig = px.histogram(
        data_clients,
        x="Age",
        nbins=20,
        title="Age Distribution of Clients",
        labels={"Age": "Age", "count": "Number of Clients"},
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_layout(bargap=0.1)
    return fig


def plot_client_density_by_state(data_clients: pd.DataFrame):
    """
    Creates a choropleth map showing the number of clients in each state.

    Args:
        data_clients: DataFrame containing client information.

    Returns:
        A Plotly Figure object representing the choropleth map.
    """
    # Count clients per state
    state_counts = data_clients["State"].value_counts().reset_index()
    state_counts.columns = ["State", "Count"]

    # Convert state abbreviations to full state names if necessary
    # For this example, we'll assume 'State' contains state abbreviations

    # Load state geometry data
    import json
    import urllib.request

    url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA.geo.json"
    with urllib.request.urlopen(url) as response:
        us_states = json.load(response)

    fig = px.choropleth(
        state_counts,
        locations="State",
        locationmode="USA-states",
        color="Count",
        color_continuous_scale="Viridis",
        scope="usa",
        title="Client Density by State",
        labels={"Count": "Number of Clients"},
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return fig


def plot_client_density_heatmap(data_clients: pd.DataFrame):
    """
    Creates a heatmap showing the density of client locations.

    Args:
        data_clients: DataFrame containing client information.

    Returns:
        A Plotly Figure object representing the density heatmap.
    """
    # Ensure that the latitude and longitude columns are numeric
    data_clients["Latitude"] = pd.to_numeric(data_clients["Latitude"], errors="coerce")
    data_clients["Longitude"] = pd.to_numeric(
        data_clients["Longitude"], errors="coerce"
    )

    # Drop rows with invalid coordinates
    data_clients = data_clients.dropna(subset=["Latitude", "Longitude"])

    fig = px.density_mapbox(
        data_clients,
        lat="Latitude",
        lon="Longitude",
        z=None,
        radius=10,
        center=dict(
            lat=data_clients["Latitude"].mean(), lon=data_clients["Longitude"].mean()
        ),
        zoom=3,
        mapbox_style="open-street-map",
        title="Client Density Heatmap",
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return fig


def plot_fraud_rate_by_state(data: pd.DataFrame):
    """
    Creates a choropleth map showing the fraud rate by state.

    Args:
        data: DataFrame containing transaction information.

    Returns:
        A Plotly Figure object representing the choropleth map.
    """
    # Calculate fraud rate per state
    state_fraud = (
        data.groupby("State")
        .agg(
            Total_Transactions=("Fraud", "count"),
            Fraudulent_Transactions=("Fraud", "sum"),
        )
        .reset_index()
    )
    state_fraud["Fraud_Rate"] = (
        state_fraud["Fraudulent_Transactions"] / state_fraud["Total_Transactions"]
    )

    fig = px.choropleth(
        state_fraud,
        locations="State",
        locationmode="USA-states",
        color="Fraud_Rate",
        color_continuous_scale="Reds",
        scope="usa",
        title="Fraud Rate by State",
        labels={"Fraud_Rate": "Fraud Rate"},
        hover_data={"Total_Transactions": True, "Fraudulent_Transactions": True},
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    return fig


def plot_transactions_by_category_state(data: pd.DataFrame):
    """
    Creates a treemap showing transaction amounts by category and state.

    Args:
        data: DataFrame containing transaction information.

    Returns:
        A Plotly Figure object representing the treemap.
    """
    fig = px.treemap(
        data,
        path=["State", "Category"],
        values="Amount",
        color="Amount",
        color_continuous_scale="Blues",
        title="Transaction Amounts by Category and State",
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    return fig


def plot_transactions_sunburst(data: pd.DataFrame):
    """
    Creates a sunburst chart showing transactions by category and merchant.

    Args:
        data: DataFrame containing transaction information.

    Returns:
        A Plotly Figure object representing the sunburst chart.
    """
    fig = px.sunburst(
        data,
        path=["Category", "Merchant"],
        values="Amount",
        color="Amount",
        color_continuous_scale="Viridis",
        title="Transaction Amounts by Category and Merchant",
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    return fig


def plot_top_categories_back_to_back(data: pd.DataFrame):
    """
    Creates a horizontal back-to-back bar chart showing the top 10 categories consumed by male and female clients.

    Args:
        data: DataFrame containing transaction information, including 'Category', 'Amount', and 'Gender'.

    Returns:
        A Plotly Figure object representing the back-to-back bar chart.
    """
    # Ensure 'Amount' is numeric
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["Amount", "Category", "Gender"])

    category_gender = (
        data.groupby(["Category", "Gender", "Client"])["Amount"].sum().reset_index()
    )
    category_gender = (
        data.groupby(
            [
                "Category",
                "Gender",
            ]
        )["Amount"]
        .mean()
        .reset_index()
    )

    # Get total amounts for categories across all genders
    total_category_amounts = (
        category_gender.groupby("Category")["Amount"].sum().reset_index()
    )

    # Get top 10 categories overall
    top_categories = total_category_amounts.nlargest(10, "Amount")["Category"]

    # Filter data for top categories
    category_gender_top = category_gender[
        category_gender["Category"].isin(top_categories)
    ]

    # Pivot the data to have 'Category' as index and 'Gender' as columns
    pivot_data = category_gender_top.pivot(
        index="Category", columns="Gender", values="Amount"
    ).fillna(0)

    # Ensure both 'M' and 'F' columns exist
    if "M" not in pivot_data.columns:
        pivot_data["M"] = 0
    if "F" not in pivot_data.columns:
        pivot_data["F"] = 0

    # Sort categories by total amount
    pivot_data["Total"] = pivot_data["M"] + pivot_data["F"]
    pivot_data = pivot_data.sort_values("Total", ascending=True)
    pivot_data = pivot_data.drop("Total", axis=1)

    # Reverse male amounts to negative for back-to-back chart
    pivot_data["M"] = -pivot_data["M"]

    # Reset index for plotting
    pivot_data = pivot_data.reset_index()
    pivot_data["Category"] = pivot_data["Category"].astype(str).str.title()

    # Create the figure
    fig = go.Figure()

    # Add male bars (negative amounts)
    fig.add_trace(
        go.Bar(
            y=pivot_data["Category"],
            x=pivot_data["M"],
            name="Male",
            orientation="h",
            marker=dict(color="#1E90FF"),
            hovertemplate="Category: %{y}<br>Amount: %{x:$,.2f}<extra></extra>",
        )
    )

    # Add female bars (positive amounts)
    fig.add_trace(
        go.Bar(
            y=pivot_data["Category"],
            x=pivot_data["F"],
            name="Female",
            orientation="h",
            marker=dict(color="#FF69B4"),
            hovertemplate="Category: %{y}<br>Amount: %{x:$,.2f}<extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(
        title="Top 10 Categories Consumed by Gender",
        xaxis_title="Total Amount Spent ($)",
        yaxis_title="Category",
        barmode="overlay",
        bargap=0.1,
        xaxis=dict(
            tickformat="$,.0f",
            showgrid=True,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            title_standoff=10,
        ),
        legend=dict(title="Gender", x=0.5, xanchor="center", orientation="h", y=-0.1),
        margin=dict(l=100, r=50, t=100, b=100),
    )

    # Adjust x-axis to show absolute values in tick labels
    max_value = max(abs(pivot_data["M"].min()), pivot_data["F"].max())
    tick_vals = [-max_value, -max_value / 2, 0, max_value / 2, max_value]
    tick_texts = [f"${abs(val):,.0f}" if val != 0 else "0" for val in tick_vals]
    fig.update_xaxes(tickvals=tick_vals, ticktext=tick_texts)

    return fig


def plot_transactions_sunburst_state_category(data: pd.DataFrame):
    """
    Creates a sunburst chart showing transaction amounts by state and category.

    Args:
        data: DataFrame containing transaction information, including 'State', 'Category', and 'Amount'.

    Returns:
        A Plotly Figure object representing the sunburst chart.
    """
    # Ensure 'Amount' is numeric
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")

    # Drop rows with missing values in 'Amount', 'State', or 'Category'
    data = data.dropna(subset=["Amount", "State", "Category"])

    # Aggregate data
    aggregated_data = data.groupby(["State", "Category"])["Amount"].sum().reset_index()

    # Create sunburst chart
    fig = px.sunburst(
        aggregated_data,
        path=["State", "Category"],
        values="Amount",
        color="Amount",
        color_continuous_scale="Blues",
        title="Transaction Amounts by State and Category",
        labels={"Amount": "Total Amount ($)", "State": "State", "Category": "Category"},
    )

    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))

    return fig