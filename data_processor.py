import boto3
import csv
import io
import json
import os
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Event received:", json.dumps(event))
    
    # Get bucket and file details from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        # Get the uploaded object
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        # Process data - basic stats
        row_count = 0
        for row in reader:
            row_count += 1

        # Prepare summary
        summary = {
            "file_processed": key,
            "rows_counted": row_count,
            "processed_at": datetime.utcnow().isoformat()
        }

        # Save summary to a new S3 file
        summary_key = f"summaries/{key.split('/')[-1].replace('.csv','')}_summary.json"
        s3.put_object(
            Bucket=bucket,
            Key=summary_key,
            Body=json.dumps(summary),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': f'Summary stored at {summary_key}'
        }

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
