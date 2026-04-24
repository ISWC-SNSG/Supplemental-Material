.PHONY: build-private adapters-private maven-ere chronoqa reports optional-smoke-private optional-batch-private

build-private:
	python scripts/03_build_tasks.py --config configs/private_benchmark.yaml

adapters-private:
	python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method rog_reimpl --split test --output outputs/private_rog_reimpl_test.jsonl
	python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method kg2rag_reimpl --split test --output outputs/private_kg2rag_reimpl_test.jsonl
	python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method eventrag_reimpl --split test --output outputs/private_eventrag_reimpl_test.jsonl
	python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method e2rag_reimpl --split test --output outputs/private_e2rag_reimpl_test.jsonl

maven-ere:
	python evaluation/scripts/17_write_maven_ere_reported_summary.py --manifest data/public_eval_subsets/maven_ere_ct_90/manifest.json --summary-out artifacts/paper_results/maven_ere_90doc_final_summary.csv

chronoqa:
	python evaluation/scripts/18_evaluate_chronoqa_90_final.py --manifest data/public_eval_subsets/chronoqa_temporal_balanced_90_final/manifest.json --summary-out artifacts/paper_results/chronoqa_90_final_summary_overall.csv --group-out artifacts/paper_results/chronoqa_90_final_summary_by_group.csv

reports:
	python scripts/11_make_tables.py --reports-dir outputs/reports

optional-smoke-private:
	python optional_online_runner/04_run_responses_online.py --config configs/private_benchmark.yaml --method plain_llm --split dev --limit 2
	python optional_online_runner/04_run_responses_online.py --config configs/private_benchmark.yaml --method standard_rag --split dev --limit 2
	python optional_online_runner/04_run_responses_online.py --config configs/private_benchmark.yaml --method ours --split dev --limit 2

optional-batch-private:
	python optional_online_runner/05_make_batch_requests.py --config configs/private_benchmark.yaml --method plain_llm --split test
	python optional_online_runner/05_make_batch_requests.py --config configs/private_benchmark.yaml --method standard_rag --split test
	python optional_online_runner/05_make_batch_requests.py --config configs/private_benchmark.yaml --method ours --split test
