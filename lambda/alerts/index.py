"""Publicación de alertas operativas mediante SNS."""

import json
import os


ALLOWED_SEVERITIES = {"INFO", "WARNING", "CRITICAL"}


def build_alert(payload):
    severity = str(payload.get("severity", "WARNING")).upper()
    if severity not in ALLOWED_SEVERITIES or not payload.get("message"):
        raise ValueError("severity inválida o message ausente")
    return {"severity": severity, "message": payload["message"], "plate": payload.get("plate")}


def lambda_handler(event, context):
    try:
        alert = build_alert(event)
    except ValueError as error:
        return {"statusCode": 422, "body": json.dumps({"error": str(error)})}
    topic_arn = os.getenv("ALERTS_TOPIC_ARN")
    if topic_arn:
        import boto3
        boto3.client("sns").publish(TopicArn=topic_arn, Subject=f"ARTECO {alert['severity']}", Message=json.dumps(alert))
    return {"statusCode": 202, "body": json.dumps(alert)}
