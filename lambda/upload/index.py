import json
import os
import base64
import uuid
import boto3

s3 = boto3.client("s3")
sqs = boto3.client("sqs")

BUCKET_NAME = os.environ["BUCKET_NAME"]
QUEUE_URL = os.environ["QUEUE_URL"]


def lambda_handler(event, context):
    try:
        body = event.get("body", "")

        if event.get("isBase64Encoded", False):
            file_content = base64.b64decode(body)
        else:
            file_content = body.encode("utf-8")

        file_id = str(uuid.uuid4())
        object_key = f"uploads/{file_id}.bin"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=file_content
        )

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                "bucket": BUCKET_NAME,
                "key": object_key
            })
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Archivo recibido correctamente",
                "key": object_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }