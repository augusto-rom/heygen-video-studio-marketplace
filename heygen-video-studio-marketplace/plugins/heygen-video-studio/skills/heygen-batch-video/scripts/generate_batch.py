#!/usr/bin/env python3
"""
HeyGen Batch Video — genera videos de HeyGen en serie a partir de un Google Sheet.

Lee filas con estado="pendiente" y aprobado="si", genera el video en HeyGen
usando una plantilla (template), espera a que termine y escribe la URL de vuelta
en la hoja.

Uso:
    python generate_batch.py --sheet-id <ID> --worksheet "Hoja 1" --max 10
    python generate_batch.py --sheet-id <ID> --dry-run

Variables de entorno requeridas:
    HEYGEN_API_KEY                  API key de HeyGen (plan con API).
    GOOGLE_APPLICATION_CREDENTIALS  Ruta al JSON de la cuenta de servicio de Google.

Opcional:
    HEYGEN_TEMPLATE_MAP  JSON que mapea nombre de avatar -> template_id.
                         Ej: {"Winston":"abc123","Wina":"def456"}
                         Se usa cuando la fila trae 'avatar' en vez de 'template_id'.

Dependencias:
    pip install gspread google-auth requests
"""

import argparse
import json
import os
import sys
import time

import requests

HEYGEN_BASE = "https://api.heygen.com"
GENERATE_URL = HEYGEN_BASE + "/v2/template/{template_id}/generate"
STATUS_URL = HEYGEN_BASE + "/v1/video_status.get"

REQUIRED_COLUMNS = ["id", "titulo", "guion", "aprobado", "estado"]


# --------------------------------------------------------------------------- #
# Utilidades de configuracion
# --------------------------------------------------------------------------- #
def get_api_key():
    key = os.environ.get("HEYGEN_API_KEY")
    if not key:
        sys.exit("ERROR: falta la variable de entorno HEYGEN_API_KEY.")
    return key


def get_template_map():
    raw = os.environ.get("HEYGEN_TEMPLATE_MAP", "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("ERROR: HEYGEN_TEMPLATE_MAP no es un JSON valido.")


def resolve_template_id(row, template_map):
    """Devuelve el template_id de la fila: primero la columna, luego el mapa por avatar."""
    tid = (row.get("template_id") or "").strip()
    if tid:
        return tid
    avatar = (row.get("avatar") or "").strip()
    if avatar and avatar in template_map:
        return template_map[avatar]
    return None


# --------------------------------------------------------------------------- #
# Google Sheets
# --------------------------------------------------------------------------- #
def open_worksheet(sheet_id, worksheet_name):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        sys.exit("ERROR: instala dependencias con: pip install gspread google-auth requests")

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        sys.exit("ERROR: GOOGLE_APPLICATION_CREDENTIALS no apunta a un archivo valido.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    return sh.worksheet(worksheet_name) if worksheet_name else sh.sheet1


def load_rows(ws):
    """Devuelve (registros, mapa_columna->indice_1based). Valida columnas obligatorias."""
    values = ws.get_all_values()
    if not values:
        sys.exit("ERROR: la hoja esta vacia.")
    header = [h.strip() for h in values[0]]
    col_index = {name: i + 1 for i, name in enumerate(header)}  # 1-based para gspread
    missing = [c for c in REQUIRED_COLUMNS if c not in col_index]
    if missing:
        sys.exit(f"ERROR: faltan columnas obligatorias en la hoja: {missing}")

    records = []
    for r, raw in enumerate(values[1:], start=2):  # fila 2 en adelante (1-based)
        row = {header[i]: (raw[i] if i < len(raw) else "") for i in range(len(header))}
        row["_rownum"] = r
        records.append(row)
    return records, col_index


def update_cell(ws, rownum, col_index, column, value):
    if column in col_index:
        ws.update_cell(rownum, col_index[column], value)


# --------------------------------------------------------------------------- #
# HeyGen
# --------------------------------------------------------------------------- #
def heygen_generate(api_key, template_id, title, guion):
    payload = {
        "title": title[:100] if title else "video",
        "variables": {
            "guion": {"name": "guion", "type": "text", "properties": {"content": guion}}
        },
    }
    resp = requests.post(
        GENERATE_URL.format(template_id=template_id),
        headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})
    video_id = data.get("video_id")
    if not video_id:
        raise RuntimeError(f"HeyGen no devolvio video_id: {resp.text[:300]}")
    return video_id


def heygen_wait(api_key, video_id, poll_seconds=15, timeout_minutes=20):
    """Consulta el estado hasta 'completed'. Devuelve la URL del video."""
    deadline = time.time() + timeout_minutes * 60
    while time.time() < deadline:
        resp = requests.get(
            STATUS_URL,
            headers={"X-Api-Key": api_key},
            params={"video_id": video_id},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        status = data.get("status")
        if status == "completed":
            return data.get("video_url") or data.get("url")
        if status in ("failed", "error"):
            raise RuntimeError(f"HeyGen fallo el render: {data.get('error') or status}")
        time.sleep(poll_seconds)
    raise TimeoutError(f"Timeout esperando el video {video_id}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Genera videos de HeyGen en lote desde un Google Sheet.")
    ap.add_argument("--sheet-id", required=True, help="ID del Google Sheet (de la URL).")
    ap.add_argument("--worksheet", default="", help="Nombre de la pestana. Vacio = primera.")
    ap.add_argument("--max", type=int, default=5, help="Freno de costos: maximo de videos por corrida.")
    ap.add_argument("--poll", type=int, default=15, help="Segundos entre consultas de estado.")
    ap.add_argument("--dry-run", action="store_true", help="Muestra que se generaria sin llamar a HeyGen.")
    args = ap.parse_args()

    api_key = None if args.dry_run else get_api_key()
    template_map = get_template_map()

    ws = open_worksheet(args.sheet_id, args.worksheet)
    records, col_index = load_rows(ws)

    pendientes = [
        r for r in records
        if (r.get("estado") or "").strip().lower() == "pendiente"
        and (r.get("aprobado") or "").strip().lower() in ("si", "sí", "yes", "true")
    ]

    if not pendientes:
        print("No hay filas pendientes y aprobadas. Nada que hacer.")
        return

    lote = pendientes[: args.max]
    print(f"Filas pendientes y aprobadas: {len(pendientes)}. Se procesaran {len(lote)} (limite --max={args.max}).")

    for row in lote:
        rid = row.get("id", "?")
        template_id = resolve_template_id(row, template_map)
        if not template_id:
            print(f"[{rid}] SIN template_id (ni columna ni mapa de avatar). Marcando error.")
            if not args.dry_run:
                update_cell(ws, row["_rownum"], col_index, "estado", "error")
            continue

        guion = (row.get("guion") or "").strip()
        if not guion:
            print(f"[{rid}] guion vacio. Marcando error.")
            if not args.dry_run:
                update_cell(ws, row["_rownum"], col_index, "estado", "error")
            continue

        if args.dry_run:
            print(f"[{rid}] DRY-RUN -> template={template_id} | guion='{guion[:60]}...'")
            continue

        try:
            print(f"[{rid}] generando en HeyGen (template {template_id})...")
            video_id = heygen_generate(api_key, template_id, row.get("titulo", ""), guion)
            update_cell(ws, row["_rownum"], col_index, "video_id", video_id)
            update_cell(ws, row["_rownum"], col_index, "estado", "en_proceso")

            url = heygen_wait(api_key, video_id, poll_seconds=args.poll)
            update_cell(ws, row["_rownum"], col_index, "video_url", url or "")
            update_cell(ws, row["_rownum"], col_index, "estado", "listo")
            print(f"[{rid}] LISTO -> {url}")
        except Exception as e:  # noqa: BLE001 (queremos seguir con el resto del lote)
            print(f"[{rid}] ERROR: {e}")
            try:
                update_cell(ws, row["_rownum"], col_index, "estado", "error")
            except Exception:
                pass

    print("Corrida terminada.")


if __name__ == "__main__":
    main()
