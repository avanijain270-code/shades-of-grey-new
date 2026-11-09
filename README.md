# Shades of Grey — Business Analytics Dashboard

## Project Overview
This individual business analytics project analyses the performance of the fictional brand **Shades of Grey** using a synthetic dataset.

The project covers:
- Business strategy and simulated end-to-end sales pipeline validation
- Data cleaning and transformation
- Descriptive analytics
- Diagnostic analytics
- Exploratory Data Analysis (EDA)
- Correlation analysis
- Interactive Streamlit dashboard
- Business insights and recommendations

## Dataset
The Excel workbook contains:
- Customers
- Products
- Transactions
- Marketing
- Sales Pipeline
- Returns
- Inventory
- Monthly Finance
- Data Dictionary
- Data Quality Log
- Read Me

## Sales Pipeline
The Sales Pipeline models the customer journey:

Marketing → Lead Generation → Awareness → Interest → Consideration → Purchase

The pipeline includes lead sources, customer references, product interest, follow-up status, conversion status, linked transactions and lost reasons.

### Important Limitation
This dataset is synthetic. Therefore, the sales pipeline represents **simulated business validation** and should not be presented as actual proof of market demand. Real demand validation would require customer surveys, interviews, experiments or actual sales evidence.

## Dashboard Sections
1. Executive Overview
2. Customer Analysis
3. Product & Sales Analysis
4. Marketing Performance
5. Sales Pipeline
6. Returns & Inventory
7. Correlation & Insights
8. Project Methodology

## Installation

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

```bash
streamlit run app.py
```

## Technologies Used
- Python
- Streamlit
- Pandas
- OpenPyXL
- Plotly

## Project Structure

```text
Shades_of_Grey_Business_Analytics/
│
├── Shades_of_Grey_Synthetic_Dataset_Final_With_Sales_Pipeline.xlsx
├── app.py
├── requirements.txt
└── README.md
```
