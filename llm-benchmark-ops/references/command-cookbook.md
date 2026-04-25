# Command Cookbook

## Smoke run (all models x all benchmarks)
```bash
python experiments/run_all_benchmarks.py \
  --models qwen2.5-14b-instruct qwen2.5-32b-instruct \
  --benchmark_root /home/ubuntu/codes/datasets \
  --sample_size 8 \
  --disable_optimization \
  --run_id smoke-<timestamp>
```

## Full run in tmux
```bash
RUN_ID=full-$(date +%Y%m%d-%H%M%S)
tmux new-session -d -s "$RUN_ID" \
  "cd /path/to/repo && python experiments/run_all_benchmarks.py --run_id $RUN_ID"
```

## Monitor
```bash
tail -f result/logs/<run_id>/launcher.log
tail -f result/logs/<run_id>/<model>/<benchmark>.log
```

## Aggregate summary table
```bash
python /home/ubuntu/.codex/skills/experiment-governance/scripts/collect_summaries.py --run-id <run_id>
```
