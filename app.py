
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Shades of Grey | Business Analytics",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = Path("Shades_of_Grey_Synthetic_Dataset_Final_With_Sales_Pipeline.xlsx")


@st.cache_data
def load_data(file):
    sheets = pd.read_excel(file, sheet_name=None)

    # Basic cleaning and transformation
    for name, df in sheets.items():
        df.columns = [str(c).strip() for c in df.columns]
        df.drop_duplicates(inplace=True)

        # Convert date columns automatically
        for col in df.columns:
            if "Date" in col or col.endswith("_Date"):
                df[col] = pd.to_datetime(df[col], errors="coerce")

    # Useful transformations
    if "Customers" in sheets:
        customers = sheets["Customers"].copy()
        if "Age" in customers.columns:
            customers["Age_Group"] = pd.cut(
                customers["Age"],
                bins=[0, 25, 35, 45, 100],
                labels=["18–25", "26–35", "36–45", "46+"]
            )
        sheets["Customers"] = customers

    if "Transactions" in sheets:
        tx = sheets["Transactions"].copy()
        if "Transaction_Date" in tx.columns:
            tx["Month"] = tx["Transaction_Date"].dt.strftime("%b")
            tx["Year_Month"] = tx["Transaction_Date"].dt.to_period("M").astype(str)
        if {"Gross_Profit_INR", "Net_Revenue_INR"}.issubset(tx.columns):
            tx["Profit_Margin_Percent"] = (
                tx["Gross_Profit_INR"] / tx["Net_Revenue_INR"] * 100
            ).round(2)
        sheets["Transactions"] = tx

    if "Marketing" in sheets:
        marketing = sheets["Marketing"].copy()
        if {"Clicks", "Impressions"}.issubset(marketing.columns):
            marketing["CTR_Percent"] = (
                marketing["Clicks"] / marketing["Impressions"] * 100
            ).round(2)
        if {"Conversions", "Clicks"}.issubset(marketing.columns):
            marketing["Conversion_Rate_Percent"] = (
                marketing["Conversions"] / marketing["Clicks"] * 100
            ).round(2)
        if {"Attributed_Revenue_INR", "Marketing_Spend_INR"}.issubset(marketing.columns):
            marketing["Marketing_ROI_Percent"] = (
                (marketing["Attributed_Revenue_INR"] - marketing["Marketing_Spend_INR"])
                / marketing["Marketing_Spend_INR"] * 100
            ).round(2)
        sheets["Marketing"] = marketing

    return sheets


st.title("📊 Shades of Grey — Business Analytics Dashboard")
st.caption("Descriptive, diagnostic and exploratory analytics using a synthetic business dataset.")

if not DATA_FILE.exists():
    uploaded = st.file_uploader("Upload the final Excel dataset", type=["xlsx"])
    if uploaded is None:
        st.info("Please place the Excel file in the same folder as app.py, or upload it above.")
        st.stop()
    data = load_data(uploaded)
else:
    data = load_data(DATA_FILE)

customers = data.get("Customers", pd.DataFrame())
products = data.get("Products", pd.DataFrame())
transactions = data.get("Transactions", pd.DataFrame())
marketing = data.get("Marketing", pd.DataFrame())
pipeline = data.get("Sales_Pipeline", pd.DataFrame())
returns = data.get("Returns", pd.DataFrame())
inventory = data.get("Inventory", pd.DataFrame())

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Executive Overview",
        "👥 Customer Analysis",
        "🛍️ Product & Sales",
        "📢 Marketing Performance",
        "🔄 Sales Pipeline",
        "📦 Returns & Inventory",
        "📊 Correlation & Insights",
        "ℹ️ Project Methodology"
    ]
)

def money(x):
    return f"₹{x:,.0f}"

if page == "🏠 Executive Overview":
    st.header("Executive Overview")

    total_revenue = transactions["Net_Revenue_INR"].sum() if not transactions.empty else 0
    total_profit = transactions["Gross_Profit_INR"].sum() if not transactions.empty else 0
    total_transactions = len(transactions)
    total_customers = customers["Customer_ID"].nunique() if "Customer_ID" in customers else len(customers)
    total_leads = len(pipeline)
    conversion_rate = (
        (pipeline["Purchase_Status"].eq("Converted").mean() * 100)
        if "Purchase_Status" in pipeline else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", money(total_revenue))
    c2.metric("Total Gross Profit", money(total_profit))
    c3.metric("Total Transactions", f"{total_transactions:,}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Total Customers", f"{total_customers:,}")
    c5.metric("Total Leads", f"{total_leads:,}")
    c6.metric("Lead Conversion Rate", f"{conversion_rate:.1f}%")

    st.subheader("Monthly Revenue Trend")
    if not transactions.empty and "Year_Month" in transactions:
        monthly = transactions.groupby("Year_Month", as_index=False)["Net_Revenue_INR"].sum()
        fig = px.line(monthly, x="Year_Month", y="Net_Revenue_INR", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "Insight: This trend identifies periods of stronger and weaker sales performance. "
            "The business can use this information for seasonal planning, inventory allocation and campaign timing."
        )

elif page == "👥 Customer Analysis":
    st.header("Customer Analysis")

    if not customers.empty:
        col1, col2 = st.columns(2)

        with col1:
            if "Age_Group" in customers:
                age = customers["Age_Group"].value_counts().reset_index()
                age.columns = ["Age Group", "Customers"]
                st.plotly_chart(
                    px.bar(age, x="Age Group", y="Customers", title="Customers by Age Group"),
                    use_container_width=True
                )

        with col2:
            if "City" in customers:
                city = customers["City"].value_counts().head(10).reset_index()
                city.columns = ["City", "Customers"]
                st.plotly_chart(
                    px.bar(city, x="City", y="Customers", title="Top Cities by Customers"),
                    use_container_width=True
                )

        if "Preferred_Style" in customers:
            style = customers["Preferred_Style"].value_counts().reset_index()
            style.columns = ["Style", "Customers"]
            st.plotly_chart(
                px.pie(style, names="Style", values="Customers", title="Preferred Style"),
                use_container_width=True
            )

        st.info(
            "Business insight: Customer demographics and preferences help the business improve segmentation, "
            "product assortment and targeted marketing."
        )

elif page == "🛍️ Product & Sales":
    st.header("Product & Sales Analysis")

    if not transactions.empty and not products.empty:
        merged = transactions.merge(
            products[["Product_ID", "Product_Name", "Category"]],
            on="Product_ID",
            how="left"
        )

        col1, col2 = st.columns(2)

        with col1:
            category = merged.groupby("Category", as_index=False)["Net_Revenue_INR"].sum()
            category = category.sort_values("Net_Revenue_INR", ascending=False)
            st.plotly_chart(
                px.bar(category, x="Category", y="Net_Revenue_INR", title="Revenue by Category"),
                use_container_width=True
            )

        with col2:
            top_products = (
                merged.groupby("Product_Name", as_index=False)["Net_Revenue_INR"]
                .sum()
                .nlargest(10, "Net_Revenue_INR")
            )
            st.plotly_chart(
                px.bar(top_products, x="Net_Revenue_INR", y="Product_Name",
                       orientation="h", title="Top 10 Products by Revenue"),
                use_container_width=True
            )

        st.info(
            "Business insight: High-revenue categories and products should receive stronger inventory support "
            "and marketing attention. Low-performing products may need repositioning or reduced inventory."
        )

elif page == "📢 Marketing Performance":
    st.header("Marketing Performance")

    if not marketing.empty:
        channel = marketing.groupby("Channel", as_index=False).agg(
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
            Conversions=("Conversions", "sum"),
            Spend=("Marketing_Spend_INR", "sum"),
            Revenue=("Attributed_Revenue_INR", "sum")
        )

        st.plotly_chart(
            px.bar(channel, x="Channel", y="Conversions", title="Conversions by Marketing Channel"),
            use_container_width=True
        )

        st.plotly_chart(
            px.scatter(
                marketing,
                x="Marketing_Spend_INR",
                y="Attributed_Revenue_INR",
                color="Channel",
                size="Conversions",
                hover_name="Campaign_Name",
                title="Marketing Spend vs Attributed Revenue"
            ),
            use_container_width=True
        )

        st.info(
            "Diagnostic insight: Comparing spend with revenue and conversions helps identify channels that "
            "generate efficient returns and channels that may require optimisation."
        )

elif page == "🔄 Sales Pipeline":
    st.header("End-to-End Sales Pipeline")

    st.warning(
        "This pipeline is synthetic and represents simulated business validation. "
        "It should not be presented as actual proof of market demand."
    )

    if not pipeline.empty:
        converted = int((pipeline["Purchase_Status"] == "Converted").sum())
        not_converted = int((pipeline["Purchase_Status"] == "Not Converted").sum())

        a, b, c = st.columns(3)
        a.metric("Total Leads", f"{len(pipeline):,}")
        b.metric("Converted", f"{converted:,}")
        c.metric("Not Converted", f"{not_converted:,}")

        stage_order = ["Awareness", "Interest", "Consideration", "Purchase"]
        stages = pipeline["Pipeline_Stage"].value_counts().reindex(stage_order, fill_value=0).reset_index()
        stages.columns = ["Stage", "Leads"]

        fig = go.Figure(
            go.Funnel(
                y=stages["Stage"],
                x=stages["Leads"],
                textinfo="value+percent initial"
            )
        )
        fig.update_layout(title="Customer Journey Funnel")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            source = pipeline.groupby("Lead_Source", as_index=False).agg(
                Leads=("Lead_ID", "count"),
                Converted=("Purchase_Status", lambda x: (x == "Converted").sum())
            )
            source["Conversion_Rate_Percent"] = source["Converted"] / source["Leads"] * 100
            st.plotly_chart(
                px.bar(source, x="Lead_Source", y="Conversion_Rate_Percent",
                       title="Conversion Rate by Lead Source"),
                use_container_width=True
            )

        with col2:
            lost = pipeline.loc[
                pipeline["Purchase_Status"] == "Not Converted",
                "Lost_Reason"
            ].value_counts().reset_index()
            lost.columns = ["Lost Reason", "Leads"]
            st.plotly_chart(
                px.bar(lost, x="Leads", y="Lost Reason", orientation="h",
                       title="Reasons for Lost Leads"),
                use_container_width=True
            )

        st.info(
            "Business insight: The funnel shows where potential customers drop out. "
            "The business can improve follow-ups, pricing, product availability and communication "
            "at the stages with the largest drop-off."
        )

elif page == "📦 Returns & Inventory":
    st.header("Returns & Inventory Analysis")

    if not returns.empty:
        st.subheader("Returns")
        st.dataframe(returns.head(10), use_container_width=True)

        # Try to identify a reason column automatically
        reason_cols = [c for c in returns.columns if "Reason" in c]
        if reason_cols:
            reason_col = reason_cols[0]
            reasons = returns[reason_col].value_counts().reset_index()
            reasons.columns = ["Reason", "Count"]
            st.plotly_chart(
                px.bar(reasons, x="Reason", y="Count", title="Return Reasons"),
                use_container_width=True
            )

    if not inventory.empty:
        st.subheader("Inventory")
        st.dataframe(inventory.head(10), use_container_width=True)

    st.info(
        "Business insight: Return patterns can reveal product-quality or expectation problems, "
        "while inventory analysis supports better stock planning and waste reduction."
    )

elif page == "📊 Correlation & Insights":
    st.header("Correlation Analysis & Insights")

    st.subheader("Marketing Correlation")
    if not marketing.empty:
        numeric = marketing.select_dtypes(include="number")
        if numeric.shape[1] >= 2:
            corr = numeric.corr().round(2)
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix — Marketing Metrics"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales Correlation")
    if not transactions.empty:
        numeric = transactions.select_dtypes(include="number")
        if numeric.shape[1] >= 2:
            corr = numeric.corr().round(2)
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix — Sales Metrics"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "Interpretation note: Correlation shows statistical association, not causation. "
        "A strong relationship does not automatically mean that one variable causes the other."
    )

elif page == "ℹ️ Project Methodology":
    st.header("Project Methodology")

    st.markdown("""
### End-to-End Project Flow

1. **Business Strategy & Validation Framework**
   - Define the business problem, target customer and value proposition.
   - Map the journey from lead generation to purchase.

2. **Synthetic Dataset Preparation**
   - Customers, products, transactions, marketing, returns, inventory and finance data.
   - Sales pipeline added for simulated lead-to-purchase validation.

3. **Data Cleaning & Transformation**
   - Duplicate removal.
   - Date conversion.
   - Derived metrics such as age groups, conversion rate, CTR and ROI.

4. **Descriptive & Diagnostic Analytics**
   - Analyse customers, sales, products, marketing and pipeline performance.

5. **EDA & Correlation Analysis**
   - Identify trends, relationships and potential business issues.

6. **Business Insights & Recommendations**
   - Explain what each analysis means and recommend possible actions.

### Important Limitation
The dataset is synthetic. Therefore, the sales-pipeline analysis demonstrates a
**simulated validation framework**, rather than actual proof of market demand.
""")
