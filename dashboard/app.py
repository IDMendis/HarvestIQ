
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sri Lankan Vegetable Price Prediction",
    page_icon="🥬",
    layout="wide"
)


# VEGETABLE HERO BANNER
import base64

banner_path = (
    "/content/drive/MyDrive/"
    "SriLanka_Vegetable_Price_ML/"
    "dashboard/assets/vegetable_dashboard_banner.jpg"
)

with open(banner_path, "rb") as image_file:
    banner_base64 = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

st.markdown(
    f"""
    <style>
    .vegetable-hero {{
        background-image:
            linear-gradient(
                90deg,
                rgba(7, 40, 25, 0.85),
                rgba(7, 40, 25, 0.25)
            ),
            url("data:image/jpeg;base64,{banner_base64}");
        background-size: cover;
        background-position: center;
        border-radius: 18px;
        min-height: 300px;
        padding: 55px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 25px;
    }}

    .vegetable-hero h1 {{
        color: #ffffff !important;
        font-size: clamp(28px, 3.5vw, 46px);
        font-weight: 800;
        line-height: 1.2;
        max-width: 850px;
    }}

    .vegetable-hero p {{
        color: #e8f7ed !important;
        font-size: 19px;
        font-weight: 500;
        margin-top: 12px;
    }}
    </style>

    <div class="vegetable-hero">
        <h1>Sri Lankan Vegetable Price Prediction Dashboard</h1>
        <p>Machine Learning-Based 7-Day Vegetable Price Forecasting</p>
    </div>
    """,
    unsafe_allow_html=True
)


st.divider()

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_PATH = "/content/drive/MyDrive/SriLanka_Vegetable_Price_ML"

DATA_PATH = f"{BASE_PATH}/dashboard/dashboard_data.csv"

MODEL_PATH = f"{BASE_PATH}/models/vegetable_price_stacking.joblib"

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df

# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

try:
    df = load_data()
    saved_model = load_model()

except Exception as e:
    st.error(f"Error loading dashboard files: {e}")
    st.stop()

# --------------------------------------------------
# EXTRACT MODEL COMPONENTS
# --------------------------------------------------

preprocessor = saved_model["preprocessor"]

base_models = saved_model["base_models"]

meta_model = saved_model["meta_model"]

feature_columns = saved_model["feature_columns"]

forecast_horizon = saved_model["forecast_horizon_days"]

# --------------------------------------------------



# FIXED LIGHT DASHBOARD THEME

st.markdown("""
<style>

/* Main background */
.stApp {
    background: #f4f8f5 !important;
    color: #172b20 !important;
}

/* General text */
.stApp p,
.stApp label,
.stApp li {
    color: #263d30;
}

/* Headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #174c32 !important;
}

/* Main content */
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #d5e5d9;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

[data-testid="stMetricLabel"] p {
    color: #526b5b !important;
}

[data-testid="stMetricValue"] {
    color: #174c32 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #526b5b !important;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #16804a !important;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #173b29 !important;
    border: 1px solid #cbded1;
    border-radius: 10px;
}

div[data-baseweb="select"] input {
    color: #173b29 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

/* Data tables */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Dividers */
hr {
    border-color: #d5e5d9;
}

</style>
""", unsafe_allow_html=True)


# HERO BANNER VISUAL FIX

st.markdown("""
<style>

/* Ensure hero heading is white */
.stApp .vegetable-hero h1 {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: clamp(28px, 3.2vw, 46px) !important;
    font-weight: 800 !important;
    line-height: 1.18 !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.35);
}

/* Hero subtitle */
.stApp .vegetable-hero p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 18px !important;
    text-shadow: 0 1px 5px rgba(0,0,0,0.35);
}

/* Improve hero layout */
.stApp .vegetable-hero {
    min-height: 230px !important;
    padding: 35px 45px !important;
    margin-bottom: 8px !important;
}

/* Reduce excessive divider spacing */
.stApp [data-testid="stVerticalBlock"] > div:has(> [data-testid="stDivider"]) {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

/* Make notification messages readable */
.stApp [data-testid="stAlert"] p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Improve dark notification background */
.stApp [data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)



# FINAL UI CONTRAST FIX

st.markdown("""
<style>

/* Notification messages */
.stApp [data-testid="stAlert"] {
    border-radius: 12px;
}

.stApp [data-testid="stAlert"] p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Light dropdown boxes */
.stApp div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #173b29 !important;
    border: 1px solid #cbded1 !important;
    border-radius: 10px !important;
}

/* Dropdown selected text */
.stApp div[data-baseweb="select"] [class*="singleValue"] {
    color: #173b29 !important;
}

/* Dropdown arrows */
.stApp div[data-baseweb="select"] svg {
    fill: #173b29 !important;
}

/* General form labels */
.stApp [data-testid="stWidgetLabel"] p {
    color: #244b34 !important;
}

/* Tabs */
.stApp button[data-baseweb="tab"] {
    color: #45624e !important;
}

.stApp button[data-baseweb="tab"][aria-selected="true"] {
    color: #16804a !important;
}

</style>
""", unsafe_allow_html=True)


# NAVIGATION TABS START
# INTERACTIVE FILTERS
# --------------------------------------------------

st.divider()

st.subheader("🔎 Select Vegetable and Market")

col1, col2, col3 = st.columns(3)

with col1:
    selected_vegetable = st.selectbox(
        "Select Vegetable",
        sorted(df["vegetable"].dropna().unique())
    )

# Only show markets available for this vegetable
vegetable_df = df[
    df["vegetable"] == selected_vegetable
]

with col2:
    selected_market = st.selectbox(
        "Select Market",
        sorted(vegetable_df["market"].dropna().unique())
    )

market_df = vegetable_df[
    vegetable_df["market"] == selected_market
]

with col3:
    selected_price_type = st.selectbox(
        "Select Price Type",
        sorted(market_df["price_type"].dropna().unique())
    )

# Filter dataset
filtered_df = market_df[
    market_df["price_type"] == selected_price_type
].copy()

filtered_df = filtered_df.sort_values("date")

st.success(
    f"Showing {len(filtered_df):,} observations for "
    f"{selected_vegetable} in {selected_market.title()} "
    f"({selected_price_type.title()})"
)

# --------------------------------------------------


tab1, tab2, tab3, tab4 = st.tabs([
    " Price Prediction",
    " Historical Analysis",
    " Model Comparison",
    " Dataset Overview"
])

with tab1:
    # FILTERED DATA OVERVIEW
    # --------------------------------------------------

    st.subheader("📊 Selected Vegetable Overview")

    if filtered_df.empty:
        st.warning("No observations available for this selection.")

    else:
        latest_record = filtered_df.iloc[-1]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Latest Recorded Price",
                f"Rs. {latest_record['price']:,.2f}/kg"
            )

        with col2:
            st.metric(
                "Available Observations",
                f"{len(filtered_df):,}"
            )

        with col3:
            st.metric(
                "Latest Observation Date",
                latest_record["date"].strftime("%Y-%m-%d")
            )

        st.subheader("Recent Price Records")

        st.dataframe(
            filtered_df[
                ["date", "vegetable", "market",
                 "price_type", "price"]
            ].tail(10).sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------

    # 7-DAY VEGETABLE PRICE PREDICTION
    # --------------------------------------------------

    st.divider()
    st.subheader("🔮 7-Day Vegetable Price Prediction")

    st.write(
        "Generate a 7-day price forecast using the trained "
        "Random Forest, Gradient Boosting, XGBoost, "
        "and Ridge Stacking Ensemble."
    )

    if filtered_df.empty:
        st.warning("No data available for prediction.")

    else:
        # Use only records with complete model features
        valid_records = filtered_df.dropna(
            subset=feature_columns
        ).sort_values("date")

        if valid_records.empty:
            st.warning(
                "No records with complete model features "
                "are available for this selection."
            )

        else:
            latest_record = valid_records.iloc[-1]

            latest_date = latest_record["date"]
            current_price = float(latest_record["price"])

            forecast_date = (
                latest_date +
                pd.Timedelta(days=forecast_horizon)
            )

            st.info(
                f"Latest usable observation: "
                f"{latest_date.strftime('%Y-%m-%d')}"
            )

            if st.button(
                "Predict Vegetable Price",
                type="primary"
            ):

                # Prepare model input
                X_input = latest_record[
                    feature_columns
                ].to_frame().T

                # Apply saved preprocessing
                X_processed = preprocessor.transform(X_input)

                # Generate base model predictions
                base_predictions = {}

                for name, model in base_models.items():
                    prediction = model.predict(X_processed)
                    base_predictions[name] = float(prediction[0])

                # Prepare stacking inputs
                stacking_input = np.array([
                    list(base_predictions.values())
                ])

                # Generate final stacking prediction
                predicted_change = float(
                    meta_model.predict(stacking_input)[0]
                )

                # Convert predicted change into price
                predicted_price = (
                    current_price + predicted_change
                )

                st.success("Prediction generated successfully!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Latest Recorded Price",
                        f"Rs. {current_price:,.2f}/kg"
                    )

                with col2:
                    st.metric(
                        "Predicted Price After 7 Days",
                        f"Rs. {predicted_price:,.2f}/kg"
                    )

                with col3:
                    st.metric(
                        "Predicted Price Change",
                        f"Rs. {predicted_change:+,.2f}/kg"
                    )

                st.write(
                    "Forecast Date:",
                    forecast_date.strftime("%Y-%m-%d")
                )

                # Base model comparison
                st.subheader("Base Model Predictions")

                comparison_df = pd.DataFrame({
                    "Model": list(base_predictions.keys()),
                    "Predicted Price Change": list(
                        base_predictions.values()
                    )
                })

                comparison_df["Predicted Price"] = (
                    current_price +
                    comparison_df["Predicted Price Change"]
                )

                st.dataframe(
                    comparison_df.round(2),
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "These are model-generated forecasts, "
                    "not guaranteed future market prices."
                )


    # --------------------------------------------------

with tab2:
    # HISTORICAL PRICE ANALYSIS
    # --------------------------------------------------

    st.divider()
    st.subheader("📈 Historical Vegetable Price Trends")

    if filtered_df.empty:
        st.warning("No historical data available.")

    else:
        # Select time range
        time_range = st.selectbox(
            "Select Historical Time Range",
            [
                "Last 30 Days",
                "Last 90 Days",
                "Last 6 Months",
                "Last 1 Year",
                "All Available Data"
            ],
            index=2
        )

        latest_date = filtered_df["date"].max()

        if time_range == "Last 30 Days":
            start_date = latest_date - pd.Timedelta(days=30)

        elif time_range == "Last 90 Days":
            start_date = latest_date - pd.Timedelta(days=90)

        elif time_range == "Last 6 Months":
            start_date = latest_date - pd.DateOffset(months=6)

        elif time_range == "Last 1 Year":
            start_date = latest_date - pd.DateOffset(years=1)

        else:
            start_date = filtered_df["date"].min()

        chart_df = filtered_df[
            filtered_df["date"] >= start_date
        ].copy()

        if chart_df.empty:
            st.warning("No observations in the selected time range.")

        else:
            fig = px.line(
                chart_df,
                x="date",
                y="price",
                title=(
                    f"{selected_vegetable} Price Trends — "
                    f"{selected_market.title()} "
                    f"({selected_price_type.title()})"
                ),
                labels={
                    "date": "Date",
                    "price": "Price (LKR/kg)"
                },
                markers=True
            )

            fig.update_layout(
                hovermode="x unified",
                xaxis_title="Date",
                yaxis_title="Price (LKR/kg)",
                height=450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.caption(
                "The chart displays recorded historical prices, "
                "not model predictions."
            )

            # Historical statistics
            st.subheader("Historical Price Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Average Price",
                    f"Rs. {chart_df['price'].mean():,.2f}"
                )

            with col2:
                st.metric(
                    "Minimum Price",
                    f"Rs. {chart_df['price'].min():,.2f}"
                )

            with col3:
                st.metric(
                    "Maximum Price",
                    f"Rs. {chart_df['price'].max():,.2f}"
                )

            with col4:
                st.metric(
                    "Price Observations",
                    f"{len(chart_df):,}"
                )


    # --------------------------------------------------

with tab3:
    # MODEL PERFORMANCE COMPARISON
    # --------------------------------------------------

    st.divider()
    st.subheader("🏆 Machine Learning Model Performance")

    st.write(
        "Comparison of Bagging, Boosting, Stacking Ensemble "
        "and Naive Baseline using saved evaluation results."
    )

    RESULTS_PATH = (
        f"{BASE_PATH}/models/final_model_results.csv"
    )

    @st.cache_data
    def load_evaluation_results():
        return pd.read_csv(RESULTS_PATH)

    try:
        evaluation_df = load_evaluation_results()

    except Exception as e:
        st.error(f"Unable to load evaluation results: {e}")
        st.stop()

    # --------------------------------------------------
    # MODEL CATEGORY
    # --------------------------------------------------

    model_categories = {
        "Stacking (Change)": "Stacking Ensemble",
        "Naive Baseline": "Baseline",
        "Gradient Boosting (Change)": "Boosting",
        "XGBoost (Change)": "Boosting",
        "Random Forest (Change)": "Bagging"
    }

    evaluation_df["Technique"] = (
        evaluation_df["Model"].map(model_categories)
    )

    # --------------------------------------------------
    # MODEL PERFORMANCE TABLE
    # --------------------------------------------------

    st.subheader("Model Evaluation Results")

    st.dataframe(
        evaluation_df.round(4),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # MAE COMPARISON
    # --------------------------------------------------

    st.subheader("Mean Absolute Error (MAE)")

    fig_mae = px.bar(
        evaluation_df.sort_values("MAE"),
        x="Model",
        y="MAE",
        color="Technique",
        title="Model Comparison — MAE (Lower is Better)",
        text_auto=".2f"
    )

    fig_mae.update_layout(
        xaxis_tickangle=-25,
        height=450
    )

    st.plotly_chart(
        fig_mae,
        use_container_width=True
    )

    # --------------------------------------------------
    # RMSE COMPARISON
    # --------------------------------------------------

    st.subheader("Root Mean Squared Error (RMSE)")

    fig_rmse = px.bar(
        evaluation_df.sort_values("RMSE"),
        x="Model",
        y="RMSE",
        color="Technique",
        title="Model Comparison — RMSE (Lower is Better)",
        text_auto=".2f"
    )

    fig_rmse.update_layout(
        xaxis_tickangle=-25,
        height=450
    )

    st.plotly_chart(
        fig_rmse,
        use_container_width=True
    )

    # --------------------------------------------------
    # R2 COMPARISON
    # --------------------------------------------------

    st.subheader("R² Score Comparison")

    fig_r2 = px.bar(
        evaluation_df.sort_values("R2", ascending=False),
        x="Model",
        y="R2",
        color="Technique",
        title="Model Comparison — R² (Higher is Better)",
        text_auto=".4f"
    )

    fig_r2.update_layout(
        xaxis_tickangle=-25,
        height=450
    )

    st.plotly_chart(
        fig_r2,
        use_container_width=True
    )

    # --------------------------------------------------
    # BEST MODEL SUMMARY
    # --------------------------------------------------

    best_model = evaluation_df.loc[
        evaluation_df["MAE"].idxmin()
    ]

    st.success(
        f"Best Model by MAE: {best_model['Model']} | "
        f"MAE: {best_model['MAE']:.2f} | "
        f"RMSE: {best_model['RMSE']:.2f} | "
        f"R²: {best_model['R2']:.4f}"
    )

    st.caption(
        "Evaluation metrics are loaded from the saved "
        "final_model_results.csv file."
    )

with tab4:
    # DASHBOARD OVERVIEW
    # --------------------------------------------------

    st.subheader(" Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Records",
            f"{len(df):,}"
        )

    with col2:
        st.metric(
            "Vegetables",
            df["vegetable"].nunique()
        )

    with col3:
        st.metric(
            "Markets",
            df["market"].nunique()
        )

    with col4:
        st.metric(
            "Forecast Horizon",
            f"{forecast_horizon} Days"
        )

    st.divider()

    # --------------------------------------------------

    # DATASET INFORMATION
    # --------------------------------------------------

    st.subheader(" Dataset Information")

    st.write("Available Vegetables:")
    st.write(sorted(df["vegetable"].unique()))

    st.write("Available Markets:")
    st.write(sorted(df["market"].unique()))

    st.write("Available Price Types:")
    st.write(sorted(df["price_type"].unique()))

    st.write("Dataset Date Range:")
    st.write(
        df["date"].min().date(),
        "to",
        df["date"].max().date()
    )

    # --------------------------------------------------

    # MODEL INFORMATION
    # --------------------------------------------------

    st.divider()

    st.subheader("Machine Learning Model")

    st.success("Saved Stacking Ensemble Model Loaded Successfully!")

    st.write("Model Name:", saved_model["model_name"])

    st.write("Prediction Type:", saved_model["prediction_type"])

    st.write("Base Models:", list(base_models.keys()))

    st.write("Meta Model:", type(meta_model).__name__)

    st.write("Input Features:", len(feature_columns))


    # --------------------------------------------------


# NAVIGATION TABS END
