#!/usr/bin/env python3
"""
Agrega guiones a la hoja de produccion (Google Sheet) para el skill
heygen-batch-video. Cada guion se inserta como una fila con estado="pendiente"
y aprobado="no" (control humano antes de generar).

Uso:
    python add_guiones.py --sheet-id <ID> --worksheet "Hoja 1" --input guiones.json

Entrada (JSON): lista de objetos con al menos:
    id, titulo, guion   (opcionales: avatar, template_id)

Variables de entorno:
    GOOGLE_APPLICATION_CREDENTIALS  Ruta al JSON de la cuenta de servicio de Google.

Dependencias:
    pip install gspread google-auth
"""

import argparse
import json
import os
import sys

# Encabezados esperados por heygen-batch-video. Si la hoja esta vacia, se crean.
HEADERS = [
    "id", "titulo", "guion", "template_id", "avatar",
    "aprobado", "estado", "video_url", "video_id",
]


def open_worksheet(sheet_id, worksheet_name):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        sys.exit("ERROR: instala dependencias con: pip install gspread google-auth")

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        sys.exit("ERROR: GOOGLE_APPLICATION_CREDENTIALS no apunta a un archivo valido.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    return sh.worksheet(worksheet_name) if worksheet_name else sh.sheet1


def ensure_headers(ws):
    """Si la hoja esta vacia, escribe la fila de encabezados."""
    values = ws.get_all_values()
    if not values or not any(values[0]):
        ws.update("A1", [HEADERS])
        return HEADERS
    return [h.strip() for h in values[0]]


def main():
    ap = argparse.ArgumentParser(description="Carga guiones a la hoja de produccion de HeyGen.")
    ap.add_argument("--sheet-id", required=True)
    ap.add_argument("--worksheet", default="")
    ap.add_argument("--input", required=True, help="Archivo JSON con la lista de guiones.")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        guiones = json.load(f)
    if not isinstance(guiones, list) or not guiones:
        sys.exit("ERROR: el JSON debe ser una lista con al menos un guion.")

    ws = open_worksheet(args.sheet_id, args.worksheet)
    headers = ensure_headers(ws)

    rows = []
    for g in guiones:
        if not g.get("guion") or not g.get("id"):
            print(f"Saltando guion sin 'id' o 'guion': {g}")
            continue
        record = {
            "id": g.get("id", ""),
            "titulo": g.get("titulo", ""),
            "guion": g.get("guion", ""),
            "template_id": g.get("template_id", ""),
            "avatar": g.get("avatar", ""),
            "aprobado": "no",         # requiere aprobacion humana
            "estado": "pendiente",
            "video_url": "",
            "video_id": "",
        }
        rows.append([record.get(h, "") for h in headers])

    if not rows:
        sys.exit("ERROR: no habia guiones validos que agregar.")

    ws.append_rows(rows, value_input_option="RAW")
    print(f"Agregados {len(rows)} guiones a la hoja (aprobado=no, estado=pendiente).")
    print("Siguiente paso: revisa, cambia 'aprobado' a 'si' en los aprobados, y corre heygen-batch-video.")


if __name__ == "__main__":
    main()
