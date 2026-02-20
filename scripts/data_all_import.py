#!/usr/bin/env python3
import os
import sys
import glob
import zipfile
import gzip
import requests

# --------- HARD-CODED SETTINGS ----------
ZIP_PATH = "data_all.zip"           # set "" to skip unzip step
EXTRACT_DIR = "./unzipped"          # where to unzip (if ZIP_PATH exists)
GLOB_PATTERN = "*.json.gz"          # after unzip, files are expected here (or in EXTRACT_DIR)
CLICKHOUSE_URL = "http://localhost:8123/"
USER = "ch_user"
PASSWORD = "ch_pass_change_me"
DATABASE = "default"
TABLE = "data_table"
# ---------------------------------------

QUERY = f"INSERT INTO {DATABASE}.{TABLE} FORMAT JSONEachRow"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {DATABASE}.{TABLE}
(
  ts DateTime64(6),

  src_port Nullable(UInt16),
  dst_ip   Nullable(String),
  dst_port Nullable(UInt16),

  type     Nullable(String),
  eventid  Nullable(String),
  session  Nullable(String),
  sensor   Nullable(String),
  `group`  Nullable(UInt32),

  username Nullable(String),
  password Nullable(String),
  input    Nullable(String),
  message  Nullable(String),

  data     Nullable(String),
  url      Nullable(String),
  realm    Nullable(String),
  protocol Nullable(String),

  arch Nullable(String),
  compCS Nullable(String),
  encCS Nullable(String),
  langCS Nullable(String),
  macCS Nullable(String),

  hassh Nullable(String),
  hasshAlgorithms Nullable(String),
  kexAlgs Nullable(String),
  keyAlgs Nullable(String),
  `key` Nullable(String),
  fingerprint Nullable(String),

  filename Nullable(String),
  destfile Nullable(String),
  outfile Nullable(String),
  shasum Nullable(String),

  size Nullable(UInt64),
  duration Nullable(Float64),
  width Nullable(UInt32),
  height Nullable(UInt32),

  id Nullable(String),
  name Nullable(String),
  value Nullable(String),
  version Nullable(String),

  ts_indexed Nullable(DateTime64(3)),

  src_ip_geoip_region_name Nullable(String),
  src_ip_geoip_location Nullable(String),
  src_ip_geoip_country_name Nullable(String),
  src_ip_geoip_country_iso_code Nullable(String),
  src_ip_geoip_city_name Nullable(String),
  src_ip_geoip_asn_org Nullable(String),
  src_ip_geoip_asn_number Nullable(UInt32),

  honeypot_ip_geoip_region_name Nullable(String),
  honeypot_ip_geoip_location Nullable(String),
  honeypot_ip_geoip_country_name Nullable(String),
  honeypot_ip_geoip_country_iso_code Nullable(String),
  honeypot_ip_geoip_city_name Nullable(String),
  honeypot_ip_geoip_asn_org Nullable(String),
  honeypot_ip_geoip_asn_number Nullable(UInt32),

  src_ip String,
  honeypot_ip String
)
ENGINE = MergeTree
ORDER BY (ts)
"""

def unzip_if_needed():
    if not ZIP_PATH:
        return
    if not os.path.exists(ZIP_PATH):
        return
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(EXTRACT_DIR)

def iter_gz_bytes(path: str, chunk_size: int = 1024 * 1024):
    with gzip.open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def main():
    unzip_if_needed()

    # decide where to look for files
    search_dir = EXTRACT_DIR if (ZIP_PATH and os.path.exists(ZIP_PATH)) else "."
    paths = sorted(glob.glob(os.path.join(search_dir, GLOB_PATTERN)))

    if not paths:
        print(f"No files found matching: {os.path.join(search_dir, GLOB_PATTERN)}", file=sys.stderr)
        sys.exit(2)

    #connectivity check
    r = requests.get(CLICKHOUSE_URL, params={"query": "SELECT version()"}, auth=(USER, PASSWORD))
    if r.status_code != 200:
        print("Cannot reach ClickHouse HTTP:", r.status_code, r.text[:300], file=sys.stderr)
        sys.exit(3)
    print("ClickHouse HTTP OK, version:", r.text.strip(), flush=True)

    r = requests.post(CLICKHOUSE_URL, params={"query": CREATE_TABLE_SQL}, auth=(USER, PASSWORD))
    if r.status_code != 200:
        print("Failed to create table:", r.status_code, r.text[:2000], file=sys.stderr)
        sys.exit(5)

    for i, path in enumerate(paths, 1):
        print(f"[{i}/{len(paths)}] Loading {path}", flush=True)
        r = requests.post(
            CLICKHOUSE_URL,
            params={"query": QUERY},
            data=iter_gz_bytes(path),          # streamed
            auth=(USER, PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=None,
        )
        if r.status_code != 200:
            print(f"FAILED {path} -> HTTP {r.status_code}", file=sys.stderr)
            print(r.text[:2000], file=sys.stderr)
            sys.exit(4)

    print("DONE", flush=True)

if __name__ == "__main__":
    main()
