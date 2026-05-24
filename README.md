# Looker E-Commerce Data Analytics Pipeline 🚀

An end-to-end, production-grade **Modern Data Stack** pipeline designed for retail transaction analytics, leveraging the Looker Synthetic E-Commerce dataset (TheLook).

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tools / Technologies](#tools--technologies)
- [Development Environment](#development-environment)
- [How Things Work](#how-things-work)
- [How to Setup](#how-to-setup)
- [References / Useful Resources](#references--useful-resources)
- [My Notes](#my-notes)

---

## Overview

This project implements a complete, enterprise-grade data platform using a modern ELT (Extract-Load-Transform) design. It automates the process of extracting raw e-commerce transaction data, loading it onto a secure cloud data warehouse, transforming it into high-performance analytical datasets using standard dimensional modeling, and presenting key business health metrics on an interactive executive dashboard.

### Pipeline Architecture Workflow:

![Alt text](https://github.com/chitnapak/looker-ecommerce-dbt-pipeline/blob/8ebef38d34a9b2f28372d357339c27f856e1dcb2/Presentation.png)

👉 **[Click here to view dashboard on Data Studio](https://datastudio.google.com/reporting/f004d3e7-693e-47e5-b0d7-037142b7f1df)**

---

## Key Features

- **Automated Data Ingestion (Python ETL):** Seamless extraction of transaction, product catalog, user demographics, inventory, and event data using Kaggle API, writing cleaned datasets into BigQuery.
- **Dimensional Data Modeling (Star Schema):** Designed specialized dimension (`dim_users`, `dim_products`) and fact (`fct_order_items`) models in the dbt Marts layer for comprehensive business intelligence.
- **Cost & Query Performance Optimization:** Implemented `fct_daily_sales` as a lightweight, pre-aggregated table summarizing daily transactions, category, and brand performance. This minimizes BigQuery query scanning costs and boosts Looker Studio load times.
- **Item-Level Cost Accuracy:** Configured `fct_order_items` and `fct_daily_sales` to join `stg_inventory_items` directly. This enables tracking unit costs at the individual item level rather than generic catalog costs, maximizing profitability accuracy.
- **Automated Data Quality Safeguards:** Integrated automated tests checking for primary key uniqueness and non-null values (`unique`, `not_null`) ensuring 100% data integrity before BI delivery.
- **Continuous Integration (CI/CD):** Equipped with a GitHub Actions workflow (`dbt_ci.yml`) to automatically compile the codebase and run tests on every Pull Request or push, protecting production models.

---

## Tools / Technologies

- **Python (3.10):** Core engine for data ingestion scripts, utilizing the `google-cloud-bigquery` SDK, `pandas` for basic schema sanitization, and the `kaggle` API wrapper.
- **Google BigQuery:** Enterprise serverless cloud data warehouse acting as our primary storage and processing engine, divided into a raw zone (`raw_thelook`) and analytics zone (`dbt_dev`).
- **dbt Core (Data Build Tool):** SQL-based command-line tool managing data transformations, model versioning, testing, and generating data lineage documentation.
- **Looker Studio:** Cloud-native business intelligence tool serving as our visualization layer, connecting to our optimized analytics tables.
- **Git & GitHub:** Version control system storing the codebase securely, paired with **GitHub Actions** for DevOps test automation.

---

## Development Environment

- **Code IDE:** Visual Studio Code (VS Code)
- **Environment Isolation:** Python Virtual Environment (`.venv`)
- **Key VS Code Extensions:**
  - *dbt Power User* (for SQL autocompletes, compilation, and interactive dbt Lineage Graphs)
  - *Python* (for code formatting, syntax highlighting, and virtual environment integration)

---

## How Things Work

1. **Extraction (E):** The Python ingestion pipeline fetches the Looker E-commerce dataset using Kaggle credentials.
2. **Loading (L):** The raw files are automatically mapped and loaded as physical tables in the `raw_thelook` BigQuery dataset.
3. **Staging Transformation (T - Staging):** dbt views (`stg_distribution_centers`, `stg_events`, `stg_inventory_items`, `stg_order_items`, `stg_orders`, `stg_products`, `stg_users`) sanitize columns, convert timestamps to valid BigQuery formats, and uniform field naming conventions.
4. **Marts Transformation (T - Marts):** Staging models are joined into optimized analytical physical tables:
   - `dim_users`: Demographics, user states, countries, and user registration months.
   - `dim_products`: Merges catalog specs with their respective distribution centers.
   - `fct_order_items`: Maps detailed order details, logistics durations (days to ship, days in transit), and profits based on item costs.
   - `fct_daily_sales`: Lightweight pre-aggregated daily summaries.
5. **Testing & QA:** We execute data validation rules. Once all constraints pass, the data is served to the BI dashboard.
6. **BI & Reporting:** Looker Studio runs queries against `fct_daily_sales` to display the premium dark-themed executive dashboard instantly.

---

## How to Setup

### Step 1: Clone and Set Up Python Virtual Environment
Clone your repository and initialize your isolated environment inside the root directory:
```bash
# Activate environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install dbt-bigquery
```

### Step 2: Establish Credentials
1. **Kaggle API:** Retrieve `kaggle.json` from your Kaggle profile page. Save it in the project root folder.
2. **GCP Service Account:** Create a GCP Service Account key with the **BigQuery Admin** role. Download the JSON key file and save it locally in the project root (e.g., `looker-ecommerce-analytics-5aafe0ab0b11.json`).
3. **Environment Setup:** Configure the `.env` file to refer to your JSON key path and project name:
   ```env
   GCP_PROJECT_ID=looker-ecommerce-analytics
   GCP_KEYFILE_PATH=C:\Users\ACER\OneDrive\Desktop\Profile\Pojectlooker\looker-ecommerce-analytics-5aafe0ab0b11.json
   ```

### Step 3: Run Ingestion
Execute the ingestion script to populate BigQuery with raw datasets:
```bash
.venv\Scripts\python ingest.py
```

### Step 4: Run & Test dbt Models
Move into the dbt folder and run dbt commands locally:
```bash
cd looker_ecommerce_dbt

# Run transformations and construct tables
..\.venv\Scripts\dbt run --profiles-dir .

# Run data quality tests
..\.venv\Scripts\dbt test --profiles-dir .

# Generate interactive documentation
..\.venv\Scripts\dbt docs generate --profiles-dir .
```

### Step 5: Connect Looker Studio
- Go to [Looker Studio](https://lookerstudio.google.com/).
- Click **Create > Report** and search for the **BigQuery** connector.
- Select your GCP Project `looker-ecommerce-analytics`, Dataset `dbt_dev`, and import the **`fct_daily_sales`** table to begin designing your KPI dashboard.

### Step 6: Configure GitHub CI/CD Secrets
- Go to your GitHub Repository Settings ➡️ **Secrets and variables ➡️ Actions**.
- Create a new secret named **`GCP_SA_KEY`**.
- Copy and paste the entire JSON string from your local GCP keyfile into this secret and save.

---

## References / Useful Resources

- **Data Source:** [Looker Synthetic E-Commerce Kaggle Dataset](https://www.kaggle.com/datasets/daichiuchigashima/thelook-ecommerce)
- **Transformation Tool:** [dbt Core Official Documentation](https://docs.getdbt.com/)
- **Data Warehouse:** [Google BigQuery SQL Syntax Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- **Data Visualization:** [Looker Studio Quick-Start Guide](https://support.google.com/looker-studio/answer/6292570)

---

## My Notes

*(You can use this section to write custom analysis notes, logistics study summaries, future pipeline upgrade drafts, cohort evaluations, or any other notes related to your data analysis journey!)*

- **Logistics Insight:** Distribution Center performance can be monitored by grouping `fct_order_items` shipping times to isolate transit bottleneck regions.
- **Product Strategy:** Daily profitability trends in `fct_daily_sales` help identify which high-cost brands are yielding lower profit margins due to high returns.
- **Future Upgrades:** 
  - Add an intermediate model tracking customer churn and cohort months.
  - Implement incremental materialization on `fct_order_items` for streaming updates.
