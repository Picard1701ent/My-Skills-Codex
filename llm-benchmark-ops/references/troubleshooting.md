# Troubleshooting

## Job exits immediately
- Check environment activation and Python path.
- Validate API key/base URL in `.env`.

## Log exists but no progress
- Check process list and CPU usage.
- Verify network/API connectivity.

## Missing summary files
- Inspect per-benchmark log tail for exceptions.
- Re-run failed benchmark only.

## Token/API counters missing
- Ensure summary writer includes `prompt_tokens`, `completion_tokens`, `api_calls`.
