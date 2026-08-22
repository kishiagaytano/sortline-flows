import json
import os
import uuid
from datetime import datetime, timezone
import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

REQUIRED_FIELDS = ("description", "stepsToReproduce", "environment")

def lambda_handler(event, _):
    print("EVENT:", json.dumps(event, indent=2, default=str))

    # Normalise a JSON string payload before any shape detection, so that the
    # membership and .get() tests below always run against a dict.
    if isinstance(event, str):
        event = json.loads(event)
    if not isinstance(event, dict):
        return {"error": "unsupported"}

    if "node" in event:
        raw = event["node"]["inputs"][0]["value"]
        body = json.loads(raw) if isinstance(raw, str) else raw
    elif event.get("messageVersion") == "1.0":
        params = event.get("parameters") or []
        body = {p.get("name"): p.get("value") for p in params
                if isinstance(p, dict) and p.get("name") is not None}
    else:
        body = event

    if isinstance(body, str):
        body = json.loads(body)
    if not isinstance(body, dict):
        return _resp(event, {"error": "unsupported"})

    description, steps, environment = (
        (body.get(field) or "").strip() for field in REQUIRED_FIELDS
    )

    if not description:
        return _resp(event, {"error": "missing", "field": "description"})

    ticket_id = str(uuid.uuid4())
    item = {
        "ticketId": ticket_id,
        "description": description,
        "stepsToReproduce": steps,
        "environment": environment,
        "status": "OPEN",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    table.put_item(Item=item)

    return _resp(event, {"ticketId": ticket_id, "status": "OPEN"})


def _resp(event, obj):
    if "node" in event or event.get("messageVersion") != "1.0":
        return obj
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function": event.get("function"),
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": json.dumps(obj)
                    }
                }
            },
        },
    }