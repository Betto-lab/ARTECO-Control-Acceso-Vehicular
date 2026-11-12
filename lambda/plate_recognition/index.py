"""Adaptador de reconocimiento de placas mediante Amazon Rekognition."""

import json
import os
import re


PLATE_PATTERN = re.compile(r"^[A-Z0-9]{5,8}$")


def normalize_plate(text):
    candidate = re.sub(r"[^A-Z0-9]", "", text.upper())
    return candidate if PLATE_PATTERN.fullmatch(candidate) else None


def select_plate(text_detections):
    """Selecciona la primera placa válida entre detecciones de Rekognition."""
    for detection in text_detections:
        if detection.get("Type") != "LINE" or detection.get("Confidence", 0) < 80:
            continue
        plate = normalize_plate(detection.get("DetectedText", ""))
        if plate:
            return {"plate": plate, "confidence": detection["Confidence"]}
    return None


def lambda_handler(event, context):
    bucket = event.get("bucket") or os.getenv("EVIDENCE_BUCKET")
    key = event.get("key")
    if not bucket or not key:
        return {"statusCode": 400, "body": json.dumps({"error": "bucket y key son obligatorios"})}

    import boto3

    result = boto3.client("rekognition").detect_text(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    match = select_plate(result.get("TextDetections", []))
    status = 200 if match else 422
    return {"statusCode": status, "body": json.dumps(match or {"error": "No se detectó una placa válida"})}
