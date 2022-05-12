from google.cloud import bigquery

from google.oauth2 import service_account
from dotenv import load_dotenv
load_dotenv()

def upload_to_bigquery_from_files():
    for table_name in table_names:
        filename = f"/Users/andyurquhart/Documents/Harvest-stuff/{table_name}.json"
        dataset_id = 'forecast_001'
        table_id = table_name

        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True

        with open(filename, "rb") as source_file:
            job = client.load_table_from_file(
                source_file,
                table_ref,
                location="europe-west2",  # Must match the destination dataset location.
                job_config=job_config,
            )  # API request

        job.result()  # Waits for table load to complete.

        print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))

if __name__ == "__main__":
    client = bigquery.Client()
    table_names = ['assignments_data', 'projects_data', 'clients_data']
    upload_to_bigquery_from_files()