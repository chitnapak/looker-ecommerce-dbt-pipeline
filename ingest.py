import os
import zipfile
import glob
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery

# 1. Load environment variables from .env file
load_dotenv()

# Verify environment variables
gcp_project_id = os.getenv("GCP_PROJECT_ID")
bq_dataset_id = os.getenv("BQ_DATASET_ID", "raw_thelook")

print("Checking environment variables...")
print(f"GCP Project ID: {gcp_project_id}")
print(f"BigQuery Dataset: {bq_dataset_id}")

# 2. Setup Kaggle API credentials & local dataset fallbacks
dataset_slug = os.getenv("KAGGLE_DATASET", "mustafakeser4/looker-ecommerce-bigquery-dataset")

# 3. Create folders for data storage
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 4. Search and download the dataset from Kaggle or extract existing local dataset zip
print(f"\n--- Phase 1: Obtaining dataset '{dataset_slug}' ---")

# Check if zip exists in parent directory or data directory
parent_zip = Path("../looker-ecommerce-bigquery-dataset.zip")
local_zip = data_dir / "looker-ecommerce-bigquery-dataset.zip"

if parent_zip.exists() and not (list(data_dir.glob("*.csv")) or list(data_dir.glob("*.zip"))):
    import shutil
    print(f"Found local dataset ZIP at {parent_zip}. Copying to {data_dir}...")
    shutil.copy(parent_zip, local_zip)

if not list(data_dir.glob("*.csv")) and not list(data_dir.glob("*.zip")):
    kaggle_user = os.getenv("KAGGLE_USERNAME")
    kaggle_key = os.getenv("KAGGLE_KEY")
    
    if kaggle_user and kaggle_key:
        import kaggle
        print(f"Downloading dataset '{dataset_slug}' using Kaggle API...")
        try:
            kaggle.api.dataset_download_files(dataset_slug, path=str(data_dir), unzip=False)
            print("Download completed successfully!")
        except Exception as e:
            print(f"Error downloading dataset '{dataset_slug}': {e}")
    else:
        print("KAGGLE_USERNAME or KAGGLE_KEY not found in .env, checking for local data files...")

# 5. Extract the ZIP file
zip_files = list(data_dir.glob("*.zip"))
if zip_files:
    zip_path = zip_files[0]
    print(f"\n--- Extracting {zip_path.name} to {data_dir}/ ---")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    print("Extraction completed!")
    # Remove ZIP file to save space
    zip_path.unlink()
else:
    print("\nNo ZIP file found. Proceeding with existing CSV files in data/ directory.")

# 6. Load CSV files to BigQuery
print(f"\n--- Phase 2: Uploading CSV files to Google BigQuery ({gcp_project_id}) ---")
bq_client = bigquery.Client(project=gcp_project_id)

# Create raw dataset if it doesn't exist
dataset_ref = bq_client.dataset(bq_dataset_id)
try:
    bq_client.get_dataset(dataset_ref)
    print(f"Dataset '{bq_dataset_id}' already exists.")
except Exception as get_err:
    print(f"Could not retrieve dataset '{bq_dataset_id}' details: {get_err}")
    print("Attempting to create dataset...")
    from google.api_core.exceptions import Conflict
    try:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # Modify as needed, default is US
        bq_client.create_dataset(dataset)
        print(f"Dataset '{bq_dataset_id}' created successfully.")
    except Conflict:
        print(f"Dataset '{bq_dataset_id}' already exists (Conflict 409 ignored). Proceeding...")
    except Exception as create_err:
        print(f"Could not create dataset: {create_err}. Attempting to proceed with table uploads anyway...")

# Get all CSV files in data/ folder
csv_files = list(data_dir.glob("*.csv"))

if not csv_files:
    print("No CSV files found for ingestion.")
    exit(0)

import pandas as pd

# Ingest each CSV file
for csv_file in csv_files:
    table_name = csv_file.stem
    # Clean table name to be valid for BigQuery (no dots or dashes)
    if table_name.startswith("thelook_ecommerce."):
        table_name = table_name.replace("thelook_ecommerce.", "")
    table_name = table_name.replace(".", "_").replace("-", "_")
    
    table_ref = dataset_ref.table(table_name)
    
    print(f"\nReading '{csv_file.name}' via pandas...")
    df = pd.read_csv(csv_file)
    
    print(f"Uploading '{csv_file.name}' ({len(df)} rows) to table '{bq_dataset_id}.{table_name}'...")
    
    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE # Overwrite existing table data
    )
    
    load_job = bq_client.load_table_from_dataframe(
        df,
        table_ref,
        job_config=job_config
    )
        
    # Wait for the job to complete
    try:
        load_job.result()
        print(f"Successfully uploaded {load_job.output_rows} rows into '{bq_dataset_id}.{table_name}'!")
    except Exception as e:
        print(f"Error uploading table '{table_name}': {e}")
        if hasattr(load_job, 'errors') and load_job.errors:
            for error in load_job.errors:
                print(f"  - {error}")

print("\n--- Ingestion Pipeline Completed Successfully! ---")
