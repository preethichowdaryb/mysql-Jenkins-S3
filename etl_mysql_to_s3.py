import os, io
import pandas as pd
import mysql.connector
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # reads .env when running locally

# MySQL connection (pull from env)
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "company_db"),
    connection_timeout=10
)

# Extract ALL data
df = pd.read_sql("SELECT * FROM employee_data", conn)
conn.close()

# Transform
df["bonus"] = df["salary"] * 0.10

# Date-partitioned S3 key
today = datetime.today()
s3_key = f"raw/{today.year}/{today.month:02}/{today.day:02}/employee_data.csv"

# CSV in-memory
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)

# Upload to S3 (boto3 picks creds from env or IAM role)
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
s3.put_object(Bucket=os.getenv("S3_BUCKET"), Key=s3_key, Body=csv_buffer.getvalue())

print(f"Uploaded {len(df)} records to s3://{os.getenv('S3_BUCKET')}/{s3_key}")

