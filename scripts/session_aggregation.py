#!/usr/bin/env python3
import gzip
import os
import sys
import requests

# --------- HARD-CODED SETTINGS ----------
INPUT_GZ = "session_aggregation.jsonl.gz"
CLICKHOUSE_URL = "http://localhost:8123/"
USER = "ch_user"
PASSWORD = "ch_pass_change_me"
DATABASE = "default"
TABLE = "session_aggregation"
# ---------------------------------------

QUERY_CREATE_TABLE = r"""
CREATE TABLE IF NOT EXISTS session_aggregation
(
  session String,
  src_ip FixedString(8),
  honeypot_ip FixedString(8),
  first_seen DateTime64(6, 'UTC'),
  last_seen  DateTime64(6, 'UTC'),

  total_events UInt64,

  cnt_session_connect        UInt64,
  cnt_session_closed         UInt64,
  cnt_client_version         UInt64,
  cnt_client_kex             UInt64,
  cnt_login_failed           UInt64,
  cnt_command_input          UInt64,
  cnt_session_params         UInt64,
  cnt_log_closed             UInt64,
  cnt_login_success          UInt64,
  cnt_command_failed         UInt64,
  cnt_file_download          UInt64,
  cnt_direct_tcpip_request   UInt64,
  cnt_direct_tcpip_data      UInt64,
  cnt_file_download_failed   UInt64,
  cnt_client_fingerprint     UInt64,
  cnt_file_upload            UInt64,
  cnt_client_size            UInt64,
  cnt_client_var             UInt64,
  cnt_command_success        UInt64
)
ENGINE = MergeTree
ORDER BY (first_seen, session)
"""

QUERY_INSERT = f"INSERT INTO {DATABASE}.{TABLE} FORMAT JSONEachRow"

def iter_gz_bytes(path: str, chunk_size: int = 1024 * 1024):
    with gzip.open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def ch_get(sql: str) -> str:
    r = requests.get(CLICKHOUSE_URL, params={"query": sql}, auth=(USER, PASSWORD), timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:2000]}")
    return r.text.strip()

def ch_post(sql: str, data_iter=None) -> None:
    r = requests.post(
        CLICKHOUSE_URL,
        params={"query": sql},
        auth=(USER, PASSWORD),
        data=data_iter,
        headers={"Content-Type": "application/json"},
        timeout=None,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:2000]}")

def main():
    if not os.path.exists(INPUT_GZ):
        print(f"ERROR: file not found: {INPUT_GZ}", file=sys.stderr)
        sys.exit(2)

    # connectivity
    print("ClickHouse version:", ch_get("SELECT version()"), flush=True)

    # create table
    print("Creating table (if not exists)...", flush=True)
    ch_post(QUERY_CREATE_TABLE)

    print(f"Loading {INPUT_GZ} into {DATABASE}.{TABLE} ...", flush=True)
    ch_post(QUERY_INSERT, data_iter=iter_gz_bytes(INPUT_GZ))

    cnt = ch_get(f"SELECT count() FROM {DATABASE}.{TABLE}")
    print("DONE. Rows in table:", cnt, flush=True)

if __name__ == "__main__":
    main()
