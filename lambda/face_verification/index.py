"""Comparación facial contra una imagen de referencia almacenada en S3."""

import json
import os


def is_verified(face_matches, threshold=90.0):
    return any(match.get("Similarity", 0) >= threshold for match in face_matches)


def lambda_handler(event, context):
    required = ("source_key", "reference_key")
    if any(not event.get(field) for field in required):
        return {"statusCode": 400, "body": json.dumps({"error": "source_key y reference_key son obligatorios"})}

    bucket = event.get("bucket") or os.getenv("EVIDENCE_BUCKET")
    if not bucket:
        return {"statusCode": 400, "body": json.dumps({"error": "bucket es obligatorio"})}

    import boto3

    response = boto3.client("rekognition").compare_faces(
        SourceImage={"S3Object": {"Bucket": bucket, "Name": event["source_key"]}},
        TargetImage={"S3Object": {"Bucket": bucket, "Name": event["reference_key"]}},
        SimilarityThreshold=90,
    )
    verified = is_verified(response.get("FaceMatches", []))
    return {"statusCode": 200, "body": json.dumps({"verified": verified})}
