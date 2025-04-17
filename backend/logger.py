import json
from datetime import datetime

def guardar_log(ip, username, password, resultado="pendiente"):
    log_entry = {
        "ip": ip,
        "username": username,
        "password": password,
        "resultado": resultado,
        "timestamp": str(datetime.now())
    }

    # Guardar en formato JSON por línea
    with open("logs/inputs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
