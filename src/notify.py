import json, os, requests
from dotenv import load_dotenv
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
load_dotenv()

def kirim_pesan(teks):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": teks, "parse_mode": "html"}, timeout=50)

with open(BASE / "data" / "notif.json") as f:
    daftar = json.load(f)

for g in daftar:
    teks = (
        f"<b>INFO GEMPA INDONESIA\n</b>"
        f"Waktu: {g['datetime']}\n"
        f"Magnitudo: {g['magnitude']}\n"
        f"Kedalaman: {g['kedalaman']}\n"
        f"Wilayah: {g['wilayah']}\n"
        f"Potensi: {g['potensi']}"
    )
    kirim_pesan(teks)

print(f"{len(daftar)} notifikasi terkirim")