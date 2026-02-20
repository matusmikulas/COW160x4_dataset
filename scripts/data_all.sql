CREATE TABLE data_table
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
ORDER BY (ts);
