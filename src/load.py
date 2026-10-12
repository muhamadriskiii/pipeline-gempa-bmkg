import pandas as pd, json
from db_config import get_conn
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent

df = pd.read_csv(BASE / "data" / "clean.csv")
df["datetime"] = pd.to_datetime(df["datetime"])

conn = get_conn()
cur = conn.cursor()
sql = """
INSERT INTO gempa_bmkg(
datetime, tanggal, jam, coordinates, magnitude, kedalaman, wilayah, potensi
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (datetime) DO NOTHING
RETURNING datetime;
"""
baru_masuk = []
for _, row in df.iterrows():
    cur.execute(sql, (
        row["datetime"], row["tanggal"], row["jam"], row["coordinates"],
        row["magnitude"], row["kedalaman"], row["wilayah"], row["potensi"]
    ))
    hasil = cur.fetchone()
    if hasil:
        baru_masuk.append({
            "datetime": str(row["datetime"]),
            "magnitude": float(row["magnitude"]),
            "kedalaman": row["kedalaman"],
            "wilayah": row["wilayah"],
            "potensi": row["potensi"],
        })
conn.commit()
cur.close()
conn.close()

with open(BASE / "data" / "notif.json", "w") as f:
    json.dump(baru_masuk, f)
print(f"{len(baru_masuk)} data baru masuk database")
