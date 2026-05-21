import os
import zipfile
import glob
from pathlib import Path
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# Verify environment variables
gcp_project_id = os.getenv("GCP_PROJECT_ID")
bq_dataset_id = os.getenv("BQ_DATASET_ID", "raw_thelook")

print("Checking environment variables...")
print(f"GCP Project ID: {gcp_project_id}")
print(f"BigQuery Dataset: {bq_dataset_id}")

# 2. Setup Kaggle API credentials
# The Kaggle API client reads credentials from environment variables: KAGGLE_USERNAME and KAGGLE_KEY
if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
    raise ValueError(
        "KAGGLE_USERNAME or KAGGLE_KEY is not set in environment variables. Please check your .env file."
    )

# Now import kaggle after setting up credentials in env
import kaggle
from google.cloud import bigquery

# Initialize Google BigQuery Client
# It will automatically pick up GOOGLE_APPLICATION_CREDENTIALS from .env via os.environ
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    raise ValueError(
        "GOOGLE_APPLICATION_CREDENTIALS is not set in environment variables. Please check your .env file."
    )

# 3. Create folders for data storage
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 4. Search and download the dataset from Kaggle
# The dataset could be under different slugs. We will try 'thelook-ecommerce/thelook-ecommerce' or search dynamically.
dataset_slug = "thelook-ecommerce/thelook-ecommerce"

print(f"\n--- Phase 1: Downloading dataset '{dataset_slug}' from Kaggle ---")
try:
    # Download files to 'data/' folder
    kaggle.api.dataset_download_files(dataset_slug, path=str(data_dir), unzip=False)
    print("Download completed successfully!")
except Exception as e:
    print(f"Error downloading direct slug '{dataset_slug}': {e}")
    print("Attempting to search for the dataset dynamically...")
    try:
        datasets = kaggle.api.dataset_list(search="thelook ecommerce")
        if datasets:
            # Pick the first matching dataset
            dataset_slug = datasets[0].ref
            print(f"Found matching dataset slug: '{dataset_slug}'")
            kaggle.api.dataset_download_files(dataset_slug, path=str(data_dir), unzip=False)
            print("Download completed successfully!")
        else:
            raise FileNotFoundError("Could not find any Looker eCommerce dataset on Kaggle.")
    except Exception as search_err:
        print(f"Failed to find or download dataset: {search_err}")
        exit(1)

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
    print("\nNo ZIP file found. Files might have been downloaded unzipped.")

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

# Ingest each CSV file
for csv_file in csv_files:
    table_name = csv_file.stem
    # Clean table name to be valid for BigQuery (no dots or dashes)
    if table_name.startswith("thelook_ecommerce."):
        table_name = table_name.replace("thelook_ecommerce.", "")
    table_name = table_name.replace(".", "_").replace("-", "_")
    
    table_ref = dataset_ref.table(table_name)
    
    print(f"\nUploading '{csv_file.name}' to table '{bq_dataset_id}.{table_name}'...")
    
    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,      # Skip header row
        autodetect=True,          # Let BigQuery detect types (schema) automatically
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE # Overwrite existing table data
    )
    
    with open(csv_file, "rb") as source_file:
        load_job = bq_client.load_table_from_file(
            source_file,
            table_ref,
            job_config=job_config
        )
        
    # Wait for the job to complete
    try:
        load_job.result()
        print(f"Successfully uploaded {load_job.output_rows} rows into '{bq_dataset_id}.{table_name}'!")
    except Exception as e:
        print(f"Error uploading table '{table_name}': {e}")
        # Print load errors if any
        if load_job.errors:
            for error in load_job.errors:
                print(f"  - {error}")

print("\n--- Ingestion Pipeline Completed Successfully! ---")
