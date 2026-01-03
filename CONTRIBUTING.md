# Contributing

Thanks for contributing to TrustBench-Platform.

## Ways to contribute
- Add new datasets (ensure licensing allows redistribution).
- Add new tasks and evaluation scripts.
- Improve offline metrics (while keeping minimal dependencies).
- Add documentation, examples, and plots.

## Ground rules
- Keep changes reproducible and well-documented.
- Avoid adding heavyweight dependencies unless strongly justified.
- Do not add any code that performs network calls by default.

## Submissions
If you add a new `submissions/*.json` file:
1. Ensure it validates with:
   ```bash
   python scripts/validate_submission.py submissions/<your_file>.json
   ```
2. Include `run_meta` describing settings and environment.

## Code style
- Python 3.11
- Prefer small, readable functions with comments.
- Add tests if you introduce complex logic (optional for starter repo).

## Reporting issues
Please include:
- OS + Python version
- Command used
- Expected vs actual behavior
- Minimal repro input files if applicable
