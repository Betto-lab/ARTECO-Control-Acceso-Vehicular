"""Registro y consulta persistente de accesos vehiculares en Aurora."""

import hashlib
import json
import os
import re
from datetime import datetime, timezone

PLATE_PATTERN = re.compile(r"^[A-Z0-9]{5,8}$")
ALLOWED_EVENT_TYPES = {"ENTRY", "EXIT"}
_schema_ready = False


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(payload, default=str),
    }


def _parse_body(event):
    body = event.get("body", event)
    if isinstance(body, str):
        return json.loads(body)
    if isinstance(body, dict):
        return body
    raise ValueError("El cuerpo debe ser un objeto JSON")


def _database(client=None):
    cluster_arn = os.getenv("DB_CLUSTER_ARN", "")
    secret_arn = os.getenv("DB_SECRET_ARN", "")
    if not cluster_arn or not secret_arn:
        raise RuntimeError("La base de datos no esta configurada")
    if client is None:
        import boto3
        client = boto3.client("rds-data")
    return client, {
        "resourceArn": cluster_arn,
        "secretArn": secret_arn,
        "database": os.getenv("DB_NAME", "arteco"),
    }


def _execute(client, connection, sql, parameters=None):
    return client.execute_statement(
        **connection,
        sql=sql,
        parameters=parameters or [],
        includeResultMetadata=True,
    )


def _ensure_schema(client, connection):
    global _schema_ready
    if _schema_ready:
        return
    statements = [
        """CREATE TABLE IF NOT EXISTS vehicles (
            id BIGSERIAL PRIMARY KEY, plate VARCHAR(8) NOT NULL UNIQUE,
            owner_name VARCHAR(120) NOT NULL, active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE IF NOT EXISTS access_events (
            event_id VARCHAR(24) PRIMARY KEY, vehicle_id BIGINT REFERENCES vehicles(id),
            plate VARCHAR(8) NOT NULL, event_type VARCHAR(5) NOT NULL,
            gate_id VARCHAR(64) NOT NULL, authorized BOOLEAN NOT NULL DEFAULT FALSE,
            occurred_at TIMESTAMPTZ NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)""",
        "CREATE INDEX IF NOT EXISTS access_events_plate_occurred_idx ON access_events (plate, occurred_at DESC)",
    ]
    for statement in statements:
        _execute(client, connection, statement)
    _schema_ready = True


def _value(field):
    if not field:
        return None
    return next(iter(field.values()))


def _records(result):
    columns = [item["name"] for item in result.get("columnMetadata", [])]
    return [dict(zip(columns, (_value(field) for field in row))) for row in result.get("records", [])]


def register_vehicle(payload, client=None):
    plate = str(payload.get("plate", "")).upper().replace("-", "").strip()
    owner_name = payload.get("owner_name")
    if not isinstance(owner_name, str):
        raise ValueError("owner_name debe ser texto")
    owner_name = owner_name.strip()
    if not 1 <= len(owner_name) <= 120:
        raise ValueError("owner_name debe contener entre 1 y 120 caracteres")
    if not PLATE_PATTERN.fullmatch(plate):
        raise ValueError("plate debe contener entre 5 y 8 caracteres alfanumericos")
    db, connection = _database(client)
    _ensure_schema(db, connection)
    _execute(db, connection, """INSERT INTO vehicles (plate, owner_name, active)
        VALUES (:plate, :owner, TRUE)
        ON CONFLICT (plate) DO UPDATE SET owner_name = EXCLUDED.owner_name, active = TRUE""", [
        {"name": "plate", "value": {"stringValue": plate}},
        {"name": "owner", "value": {"stringValue": owner_name}},
    ])
    return {"plate": plate, "owner_name": owner_name, "active": True}


def record_access(payload, client=None):
    plate = str(payload.get("plate", "")).upper().replace("-", "").strip()
    event_type = str(payload.get("event_type", "")).upper().strip()
    gate_id = str(payload.get("gate_id", "")).strip()
    errors = []
    if not PLATE_PATTERN.fullmatch(plate):
        errors.append("plate debe contener entre 5 y 8 caracteres alfanumericos")
    if event_type not in ALLOWED_EVENT_TYPES:
        errors.append("event_type debe ser ENTRY o EXIT")
    if not gate_id:
        errors.append("gate_id es obligatorio")
    if errors:
        raise ValueError("; ".join(errors))

    # RDS Data API's TIMESTAMP type hint expects a SQL timestamp without a
    # timezone suffix. PostgreSQL interprets it as UTC for this connection.
    occurred_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    event_id = hashlib.sha256(f"{plate}|{event_type}|{gate_id}|{occurred_at}".encode()).hexdigest()[:24]
    db, connection = _database(client)
    _ensure_schema(db, connection)
    vehicle = _execute(db, connection,
        "SELECT id, owner_name FROM vehicles WHERE plate = :plate AND active = TRUE", [
            {"name": "plate", "value": {"stringValue": plate}}
        ])
    rows = _records(vehicle)
    authorized = bool(rows)
    vehicle_id = rows[0]["id"] if rows else None
    _execute(db, connection, """INSERT INTO access_events
        (event_id, vehicle_id, plate, event_type, gate_id, authorized, occurred_at)
        VALUES (:event_id, :vehicle_id, :plate, :event_type, :gate_id, :authorized, :occurred_at)""", [
        {"name": "event_id", "value": {"stringValue": event_id}},
        {"name": "vehicle_id", "value": {"longValue": vehicle_id} if vehicle_id else {"isNull": True}},
        {"name": "plate", "value": {"stringValue": plate}},
        {"name": "event_type", "value": {"stringValue": event_type}},
        {"name": "gate_id", "value": {"stringValue": gate_id}},
        {"name": "authorized", "value": {"booleanValue": authorized}},
        {"name": "occurred_at", "value": {"stringValue": occurred_at}, "typeHint": "TIMESTAMP"},
    ])
    return {
        "event_id": event_id, "plate": plate, "event_type": event_type,
        "gate_id": gate_id, "authorized": authorized,
        "decision": "ALLOW" if authorized else "DENY",
        "owner_name": rows[0]["owner_name"] if rows else None,
        "occurred_at": occurred_at, "persistence_completed": True,
    }


def list_events(client=None):
    db, connection = _database(client)
    _ensure_schema(db, connection)
    result = _execute(db, connection, """SELECT event_id, plate, event_type, gate_id,
        authorized, occurred_at FROM access_events ORDER BY occurred_at DESC LIMIT 25""")
    return _records(result)


def lambda_handler(event, context):
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
        if method == "GET":
            return _response(200, {"events": list_events()})
        payload = _parse_body(event)
        if payload.get("action") == "register_vehicle":
            return _response(201, register_vehicle(payload))
        return _response(200, record_access(payload))
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        return _response(422, {"error": str(error)})
    except Exception as error:
        print(f"database_error: {error}")
        return _response(503, {"error": "No fue posible acceder a la base de datos"})
