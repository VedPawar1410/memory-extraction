"""
Run the eval cases against the real Gemini model and write reports/eval_results.json.

Usage (needs GOOGLE_API_KEY in the environment or .env):
    python -m evals.run_eval

This calls the paid/free-tier API, so it is NOT part of the pytest suite.
"""

import json
import os
import statistics
import time
from datetime import date
from pathlib import Path

from langchain_core.callbacks import get_usage_metadata_callback

import config  # also loads .env
from app import DEFAULT_CHAT
from evals.cases import EXTRACTION_CASES, REWRITE_CASES
from memory_engine import MemoryEngine, UserProfile
from personality_engine import PersonalityEngine

REPORT_PATH = Path(__file__).parent.parent / "reports" / "eval_results.json"


def matches(text: str, pattern: str) -> bool:
    return any(option in text for option in pattern.split("|"))


def check_extraction(case: dict, profile) -> list[str]:
    fields = {name: " || ".join(items).lower() for name, items in profile.model_dump().items()}
    fields["any"] = " || ".join(fields.values())
    failures = []
    for field, patterns in case.get("expect", {}).items():
        failures += [f"missing {field}: {p}" for p in patterns if not matches(fields[field], p)]
    failures += [f"hallucinated: {bad}" for bad in case.get("must_not", []) if bad in fields["any"]]
    total = sum(len(items) for items in profile.model_dump().values())
    if "max_items" in case and total > case["max_items"]:
        failures.append(f"expected at most {case['max_items']} items, got {total}")
    return failures


def check_rewrite(case: dict, output) -> list[str]:
    if not isinstance(output, str):
        return [f"returned {type(output).__name__}, not str"]
    return [f"lost meaning: {p}" for p in case["keep"] if not matches(output.lower(), p)]


def timed(fn):
    start = time.perf_counter()
    try:
        return fn(), None, round(time.perf_counter() - start, 2)
    except Exception as e:  # record the failure and keep going
        return None, f"ERROR: {e}"[:200], round(time.perf_counter() - start, 2)


def main():
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise SystemExit("Set GOOGLE_API_KEY (in your shell or .env) to run the eval.")

    extractor = MemoryEngine(api_key=api_key)
    results, sample_profile = [], None

    with get_usage_metadata_callback() as usage:
        for case in EXTRACTION_CASES:
            profile, error, seconds = timed(lambda: extractor.extract_from_chat(case["chat"] or DEFAULT_CHAT))
            failures = [error] if error else check_extraction(case, profile)
            if case["id"] == "designer_default":
                sample_profile = profile
            results.append(dict(id=case["id"], kind="extraction", passed=not failures, seconds=seconds,
                                failures=failures, output=profile.model_dump() if profile else None))

        for case in REWRITE_CASES:
            fallback = UserProfile(facts=[], preferences=[], emotional_patterns=[])
            engine = PersonalityEngine(sample_profile or fallback, api_key=api_key)
            output, error, seconds = timed(lambda: engine.rewrite_reply(case["text"], case["persona"]))
            failures = [error] if error else check_rewrite(case, output)
            results.append(dict(id=case["id"], kind="rewrite", passed=not failures, seconds=seconds,
                                failures=failures, output=output))

    latencies = sorted(r["seconds"] for r in results)
    passed = sum(r["passed"] for r in results)
    tokens = {model: {k: u[k] for k in ("input_tokens", "output_tokens", "total_tokens")}
              for model, u in usage.usage_metadata.items()}
    summary = dict(
        date=date.today().isoformat(),
        model=config.GEMINI_MODEL,
        passed=passed,
        total=len(results),
        pass_rate=round(passed / len(results), 3),
        median_seconds=statistics.median(latencies),
        max_seconds=latencies[-1],
        tokens=tokens,
    )

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(json.dumps(dict(summary=summary, cases=results), indent=2, ensure_ascii=False) + "\n")

    print(f"{config.GEMINI_MODEL}: {passed}/{len(results)} passed | "
          f"median {summary['median_seconds']}s | max {summary['max_seconds']}s | tokens {tokens}")
    for r in results:
        print(f"  {'PASS' if r['passed'] else 'FAIL'}  {r['id']:<22} {r['seconds']:>5}s  {'; '.join(r['failures'])}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
