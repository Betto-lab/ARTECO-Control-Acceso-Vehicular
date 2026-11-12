"""Prototipo de validación para eventos de acceso vehicular de ARTECO.

Este módulo todavía no está conectado a API Gateway ni a una base de datos.
La función valida el contrato de entrada y devuelve una decisión determinista
que permite integrar y probar el flujo sin afirmar un despliegue completo.
"""

import json
import re
from datetime import datetime, timezone


PLATE_PATTERN = re.compile(r"^[A-Z0-9]{5,8}$")
ALLOWED_EVENT_TYPES = {"ENTRY", "EXIT"}


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def _parse_body(event):
    body = event.get("body", event)
    if isinstance(body, str):
        return json.loads(body)
    if isinstance(body, dict):
        return body
    raise ValueError("El cuerpo debe ser un objeto JSON")


def lambda_handler(event, context):
    """Valida un evento de ingreso o salida y devuelve el resultado prototipo."""
    try:
        payload = _parse_body(event)
    except (TypeError, ValueError, json.JSONDecodeError):
        return _response(400, {"error": "JSON inválido"})

    plate = str(payload.get("plate", "")).upper().replace("-", "").strip()
    event_type = str(payload.get("event_type", "")).upper().strip()
    gate_id = str(payload.get("gate_id", "")).strip()

    errors = []
    if not PLATE_PATTERN.fullmatch(plate):
        errors.append("plate debe contener entre 5 y 8 caracteres alfanuméricos")
    if event_type not in ALLOWED_EVENT_TYPES:
        errors.append("event_type debe ser ENTRY o EXIT")
    if not gate_id:
        errors.append("gate_id es obligatorio")

    if errors:
        return _response(422, {"errors": errors})

    # PROTOTIPO/PENDIENTE: consultar la lista autorizada y persistir el evento.
    result = {
        "status": "accepted_for_prototype",
        "plate": plate,
        "event_type": event_type,
        "gate_id": gate_id,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "authorization_checked": False,
        "persistence_completed": False,
    }
    return _response(202, result)
