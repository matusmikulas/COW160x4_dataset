# COW160x4_dataset
Supporting repository for COW160x4 dataset consisting of 50 days logs collection from 160 Cowrie honeypot instances in 4 different configurations. 

## ClickHouse Setup and Data Import

The dataset was initially collected and indexed using the ELK stack for live monitoring and basic inspection. For large-scale aggregation and efficient downstream analysis, we recommend using **ClickHouse**, which provides significantly better performance for session-level queries over hundreds of millions of events.

### 1. Install Docker

ClickHouse can be started easily using the provided Docker Compose configuration.

First, install Docker on your system by following the official installation guide:

https://docs.docker.com/get-docker/

### 2. Start ClickHouse with Docker Compose

Once Docker is installed, launch the database by running:

```bash
docker-compose up -d
```

To verify that the container is running:

```bash
docker ps
```

### 3. Import the Dataset

Download the main dataset files:

data_all.zip

session_aggregation.jsonl.gz

Place them into the same directory as the provided import scripts.

Then populate the ClickHouse database by running:

```bash
python3 data_all_import.py
python3 session_aggregation_import.py
```
Scripts will automatically create two tables in default database and fill it with data. 

### 4. Querying the Data
After import, the dataset can be explored using custom SQL queries, Python analysis scripts, or the ClickHouse HTTP interface.

ClickHouse provides a web-accessible API on port **8123**, which can be used directly from Python or other tools. Queries can also be executed through the built-in web UI by opening:

http://localhost:8123

Example queries include:

```sql
SHOW TABLES FROM default;

DESCRIBE TABLE session_aggregation;

SELECT
    sum(cnt_session_connect)        AS total_session_connect,
    sum(cnt_session_closed)         AS total_session_closed,

    sum(cnt_client_version)         AS total_client_version,
    sum(cnt_client_kex)             AS total_client_kex,
    sum(cnt_client_fingerprint)     AS total_client_fingerprint,
    sum(cnt_client_size)            AS total_client_size,
    sum(cnt_client_var)             AS total_client_var,

    sum(cnt_login_failed)           AS total_login_failed,
    sum(cnt_login_success)          AS total_login_success,

    sum(cnt_command_input)          AS total_command_input,
    sum(cnt_command_success)        AS total_command_success,
    sum(cnt_command_failed)         AS total_command_failed,

    sum(cnt_file_download)          AS total_file_download,
    sum(cnt_file_download_failed)   AS total_file_download_failed,
    sum(cnt_file_upload)            AS total_file_upload,

    sum(cnt_direct_tcpip_request)   AS total_direct_tcpip_request,
    sum(cnt_direct_tcpip_data)      AS total_direct_tcpip_data,

    sum(cnt_session_params)         AS total_session_params,
    sum(cnt_log_closed)             AS total_log_closed
FROM session_aggregation;
```

Query for session completeness verification: 
```sql
SELECT
    count() AS total_sessions
FROM session_aggregation_shifted
WHERE
    last_seen <= toDateTime64('2025-08-17 16:05:24.407581', 6, 'UTC')
    AND cnt_session_connect > 0
    AND cnt_session_closed > 0;


SELECT
    count() AS total_sessions,

    countIf(cnt_session_connect > 0 AND cnt_session_closed = 0) AS connect_only,
    countIf(cnt_session_connect = 0 AND cnt_session_closed > 0) AS closed_only,
    countIf(cnt_session_connect > 0 AND cnt_session_closed > 0) AS connect_and_closed,
    countIf(cnt_session_connect = 0 AND cnt_session_closed = 0) AS neither_connect_nor_closed
FROM session_aggregation_shifted
WHERE
    last_seen <= toDateTime64('2025-08-17 16:05:24.407581', 6, 'UTC')
    AND (cnt_direct_tcpip_request > 0 OR cnt_direct_tcpip_data > 0;
```



