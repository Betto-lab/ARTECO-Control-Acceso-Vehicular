import json
import os
import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):
    for record in event.get("Records", []):
        message = json.loads(record["body"])

        bucket = message["bucket"]
        key = message["key"]

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        file_content = response["Body"].read()

        filename = key.split("/")[-1]
        processed_key = f"processed/{filename}"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=processed_key,
            Body=file_content
        )

        print(f"Procesado: {key} -> {processed_key}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Procesamiento completado"
        })
    }