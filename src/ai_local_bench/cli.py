from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ai_local_bench.collectors import collect_system_info
from ai_local_bench.config import get_project_paths
from ai_local_bench.reporting import (
    write_results_csv,
    write_results_jsonl,
    write_summary_markdown,
)
from ai_local_bench.runners import (
    run_comfyui_suite,
    run_llamacpp_server_suite,
    run_llamacpp_suite,
    run_ollama_suite,
)
from ai_local_bench.suite_validation import normalize_suite_paths, validate_suite_definition


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-local-bench",
        description=(
            "Reproducible cross-platform benchmarks for local AI inference "
            "on consumer hardware."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    detect_parser = subparsers.add_parser(
        "detect",
        help="Inspect the local system and print environment metadata.",
    )
    detect_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    detect_parser.set_defaults(handler=handle_detect)

    run_parser = subparsers.add_parser(
        "run",
        help="Run a benchmark suite.",
    )
    run_parser.add_argument(
        "--suite",
        help="Benchmark suite identifier, for example text-basic or image-comfyui-basic.",
    )
    run_parser.add_argument(
        "--runner",
        required=True,
        help="Runner identifier, for example llamacpp or comfyui.",
    )
    run_parser.add_argument(
        "--suite-file",
        help="Optional explicit path to a suite JSON file.",
    )
    run_parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for logs, reports, and artifacts.",
    )
    run_parser.set_defaults(handler=handle_run)

    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Summarize benchmark outputs into Markdown.",
    )
    summarize_parser.add_argument(
        "--input",
        required=True,
        help="Input JSONL file or directory containing raw result files.",
    )
    summarize_parser.add_argument(
        "--output",
        required=True,
        help="Output Markdown report path.",
    )
    summarize_parser.set_defaults(handler=handle_summarize)

    return parser


def handle_detect(args: argparse.Namespace) -> int:
    system_info = collect_system_info()
    if args.format == "json":
        print(json.dumps(system_info, indent=2, sort_keys=True))
        return 0

    for key, value in system_info.items():
        if key == "gpus":
            print("gpus:")
            for index, gpu in enumerate(value, start=1):
                print(f"  [{index}]")
                for gpu_key, gpu_value in gpu.items():
                    print(f"    {gpu_key}: {gpu_value}")
        else:
            print(f"{key}: {value}")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    if not args.suite and not args.suite_file:
        raise SystemExit("Either --suite or --suite-file is required")

    suite = load_suite_definition(args.suite, args.suite_file)
    runner_name = args.runner.lower()
    validate_suite_definition(suite, runner_name)

    base_output_dir = Path(args.output_dir)
    run_dir = make_run_directory(base_output_dir, suite["suite_name"], runner_name)
    system_info = collect_system_info()

    if runner_name == "llamacpp":
        results = run_llamacpp_suite(suite, system_info, run_dir)
    elif runner_name == "llamacpp_server":
        results = run_llamacpp_server_suite(suite, system_info, run_dir)
    elif runner_name == "comfyui":
        results = run_comfyui_suite(suite, system_info, run_dir)
    elif runner_name == "ollama":
        results = run_ollama_suite(suite, system_info, run_dir)
    else:
        raise SystemExit(f"Unsupported runner: {args.runner}")

    raw_dir = run_dir / "raw"
    reports_dir = run_dir / "reports"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = raw_dir / f"{suite['suite_name']}.jsonl"
    csv_path = base_output_dir / "ai-local-bench-results.csv"
    summary_path = reports_dir / f"{suite['suite_name']}.md"
    snapshot_path = run_dir / "environment.json"

    write_results_jsonl(jsonl_path, results)
    append_results_csv(csv_path, results)
    write_summary_markdown(summary_path, results)
    snapshot_path.write_text(json.dumps(system_info, indent=2, sort_keys=True), encoding="utf-8")

    print(f"results={len(results)}")
    print(f"run_dir={run_dir}")
    print(f"jsonl={jsonl_path}")
    print(f"csv={csv_path}")
    print(f"summary={summary_path}")
    return 0


def handle_summarize(args: argparse.Namespace) -> int:
    from ai_local_bench.reporting.jsonl_writer import load_results_jsonl

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        results = []
        for jsonl_file in sorted(input_path.glob("*.jsonl")):
            results.extend(load_results_jsonl(jsonl_file))
    else:
        results = load_results_jsonl(input_path)

    write_summary_markdown(output_path, results)
    print(f"results={len(results)}")
    print(f"output={output_path}")
    return 0


def load_suite_definition(suite_name: str | None, suite_file: str | None) -> dict:
    if suite_file:
        suite_path = Path(suite_file)
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        return normalize_suite_paths(suite, suite_path)

    if not suite_name:
        raise SystemExit("Suite name is required when --suite-file is not provided")

    paths = get_project_paths()
    candidates = [
        paths.benchmarks_dir / "text" / f"{suite_name}.json",
        paths.benchmarks_dir / "image" / f"{suite_name}.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            suite = json.loads(candidate.read_text(encoding="utf-8"))
            return normalize_suite_paths(suite, candidate)
    raise SystemExit(f"Could not find suite definition for {suite_name}")


def make_run_directory(base_output_dir: Path, suite_name: str, runner_name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = base_output_dir / f"{stamp}-{suite_name}-{runner_name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def append_results_csv(path: Path, results) -> None:
    from csv import DictWriter

    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.exists()
    from ai_local_bench.schemas import RESULT_FIELD_NAMES

    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = DictWriter(handle, fieldnames=RESULT_FIELD_NAMES)
        if not existing:
            writer.writeheader()
        for result in results:
            writer.writerow(result.to_dict())


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
