CREATE TABLE session_aggregation
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
ORDER BY (first_seen, session);
