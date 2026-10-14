# Pipeline Gempa BMKG — Indonesia

Pipeline ETL otomatis yang memantau gempa bumi terkini dari BMKG,
menyimpan ke PostgreSQL, dan mengirim notifikasi Telegram.

## Alur Pipeline

```text
extract → raw.json → transform → clean.csv → load → PostgreSQL → notif.json → notify → Telegram
```

| Tahap     | Script            | Input            | Output                        |
|-----------|-------------------|------------------|-------------------------------|
| Extract   | `src/extract.py`  | API BMKG         | `data/raw.json`               |
| Transform | `src/transform.py`| `data/raw.json`  | `data/clean.csv`              |
| Load      | `src/load.py`     | `data/clean.csv` | PostgreSQL + `data/notif.json`|
| Notify    | `src/notify.py`   | `data/notif.json`| Pesan Telegram                |

## Teknologi

- Python (`requests`, `pandas`, `psycopg2`, `python-dotenv`)
- PostgreSQL
- Apache Airflow (Docker) — orkestrasi tiap 1 menit
- Telegram Bot API — notifikasi

## Struktur Folder

```text
pipline_gempa/
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── notify.py
│   └── db_config.py
├── data/
│   ├── raw.json
│   ├── clean.csv
│   └── notif.json
├── dags/
│   └── gempa_dag.py   (arsip; yang aktif di airflow_docker/dags/)
├── .env
└── README.md
```

## Konfigurasi (`.env`)

```ini
DB_PASSWORD=***
TELEGRAM_TOKEN=***
TELEGRAM_CHAT_ID=***
```

> Di dalam Docker, host database dibaca dari variabel `GEMPA_DB_HOST=host.docker.internal`
> (diset di `docker-compose.yaml`). Jangan memakai nama `DB_HOST` untuk ini —
> nama tersebut dipakai internal oleh Airflow dan menyebabkan scheduler crash-loop.

## Cara Menjalankan

### Manual (Windows)

```cmd
python D:/gempa_stg/src/extract.py
python D:/gempa_stg/src/transform.py
python D:/gempa_stg/src/load.py
python D:/gempa_stg/src/notify.py
```

### Otomatis (Airflow + Docker)

1. Edit `docker-compose.yaml` di folder `airflow_docker`:
   - Tambah volume mount: `- D:/pipline_gempa:/opt/airflow/pipline_gempa`
   - Di `x-airflow-common` → `environment`:
     - `_PIP_ADDITIONAL_REQUIREMENTS: "pandas requests psycopg2-binary python-dotenv"`
     - `GEMPA_DB_HOST: host.docker.internal`
2. `wsl - docker compose up -d` (bukan `restart` — restart tidak membaca ulang yaml)
3. Copy DAG ke `C:\Users\USER\airflow_docker\dags\gempa_dag.py`
4. Buka `http://localhost:8080` (login: `airflow` / `airflow`), unpause DAG `gempa_indo`

Jadwal: `*/1 * * * *` (tiap 1 menit), `catchup=False`.

## Catatan Desain

- Tidak ada filter wilayah — semua gempa yang tercatat BMKG masuk ke database
  dan Telegram. Pada run pertama setelah filter dihapus, semua gempa dianggap
  data baru sehingga Telegram dapat menerima banyak pesan sekaligus (wajar,
  hanya terjadi sekali).
- `Coordinates` disimpan sebagai teks (tidak dipecah jadi latitude/longitude) —
  cukup untuk arsip dan notifikasi.
- Upsert memakai `ON CONFLICT (datetime) DO NOTHING` — data duplikat tidak masuk dua kali.
- `notif.json` hanya berisi data yang benar-benar baru; kalau kosong, Telegram tidak
  mengirim apa pun (tidak ada notifikasi ganda).
- Semua script memakai pola portable agar jalan di Windows maupun Docker:
  ```python
  from pathlib import Path
  BASE = Path(__file__).resolve().parent.parent
  ```
  Jangan memakai path absolut (`D:/...`) atau path relatif (`data/...`) di dalam script.


## Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| DAG tidak muncul di UI | File di folder yang salah | Copy ke `airflow_docker/dags/` |
| Task "No Status" terus | Scheduler/worker belum healthy | Tunggu `(healthy)` di `docker compose ps` |
| Scheduler restart berulang | Env `DB_HOST` bentrok dengan internal Airflow | Ganti jadi `GEMPA_DB_HOST` |
| `docker compose restart` tidak mempan | `restart` tidak baca ulang yaml | Pakai `docker compose up -d` |
| `FileNotFoundError: data/notif.json` di container | Path relatif, tergantung folder kerja | Pakai pola `BASE / "data" / ...` |
| Garis bawah merah di `airflow.operators.bash` (VS Code) | Airflow hanya ada di Docker, bukan di Windows | Abaikan — validasi lewat UI Airflow |
