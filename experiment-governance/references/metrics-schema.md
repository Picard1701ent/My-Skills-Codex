# Metrics Schema (Per Benchmark Summary)

Required keys:
- benchmark: string
- model: string
- elapsed_seconds: number
- prompt_tokens: number
- completion_tokens: number
- api_calls: number
- cost: number

Metric key:
- either `accuracy` (number) OR `score` (number)

Optional keys:
- samples
- evaluated_questions
- result_file
- mode
- num_rounds
- batch_size
