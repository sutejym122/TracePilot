"""Generate believable ApiMetric rows for the latency dashboard (MVP).

TODO(phase7): produce realistic distributions:
  - p95 always > avg
  - error rates clustered low with occasional spikes
  - latency varies by endpoint type (POST /payments slower than GET /users)
"""
