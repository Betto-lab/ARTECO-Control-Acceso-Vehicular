"""Construcción y envío idempotente de eventos de acceso."""

import hashlib
import json
import os
from datetime import datetime, timezone


def build_access_event(payload):
    required = ("plate", "event_type", "gate_id")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Campos obligatorios: {', '.join(missing)}")
    occurred_at = payload.get("occurred_at") or datetime.now(timezone.utc).isoformat()
    stable = f"{payload['plate']}|{payload['event_type']}|{payload['gate_id']}|{occurred_at}"
    return {**payload, "occurred_at": occurred_at, "event_id": hashlib.sha256(stable.encode()).hexdigest()[:24]}


def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        access_event = build_access_event(payload)
    except (ValueError, json.JSONDecodeError) as error:
        return {"statusCode": 422, "body": json.dumps({"error": str(error)})}

    queue_url = os.getenv("ACCESS_QUEUE_URL")
    if queue_url:
        import boto3
        boto3.client("sqs").send_message(QueueUrl=queue_url, MessageBody=json.dumps(access_event))
    return {"statusCode": 202, "body": json.dumps(access_event)}
