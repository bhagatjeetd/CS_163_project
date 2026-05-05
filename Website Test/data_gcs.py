import os
import pandas as pd
from google.cloud import storage
from io import StringIO

def read_csv_from_gcs(blob_name: str) -> pd.DataFrame:
    bucket_name = os.environ.get("BUCKET_NAME", "")
    if not bucket_name:
        raise RuntimeError("BUCKET_NAME environment variable is not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    text = blob.download_as_text()
    return pd.read_csv(StringIO(text))