import requests
import json
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent

r = requests.get(
    "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json",
    timeout=20
)
data = r.json()["Infogempa"]["gempa"]
with open(BASE / "data" / "raw.json", "w") as f:
    json.dump(data, f)