#!/usr/bin/env python3
"""④ Eval harness (stub). Runs gold questions through the agent, grades, emits a TELEMETRY row
per run (skill version, git SHA, model, per-assertion pass/fail, tokens, latency), and gates on
the per-domain threshold. Wire into CI so a PR touching a dependency re-runs the affected evals.

Two senior practices baked in:
  - GRADE THE QUERY, not the number (anchors against staleness): for grade_on=metric_resolution
    we check the resolved metric/dimensions/filters, not a live value.
  - TELEMETRY, not test logs: every run lands in a warehouse table so "did that change help?"
    becomes a query, and ablations (hold evals fixed, change one component) are trivial.
"""
import json, subprocess, sys, yaml  # PyYAML

def git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip() or "unknown"

def run_agent(question: str) -> dict:
    """TODO: call your agent (Claude Code / API with the skills loaded). Return its structured trace:
       {metrics:[...], dimensions:[...], filters:[...], hits_semantic_layer:bool,
        asked_clarification:bool, value:..., tokens:int, latency_ms:int}."""
    raise NotImplementedError(f"wire to your agent runtime; question was: {question!r}")

def grade(ev: dict, trace: dict) -> tuple[bool, list[str]]:
    fails, exp = [], ev.get("expect", {})
    mode = ev.get("grade_on")
    if mode in ("metric_resolution", "query_snapshot"):
        for m in exp.get("metrics", []):
            if m not in trace.get("metrics", []): fails.append(f"missing metric {m}")
        for d in exp.get("dimensions", []):
            if d not in trace.get("dimensions", []): fails.append(f"missing dim {d}")
        for f in exp.get("filters_include", []):
            if not any(f.split("=")[0].strip() in x for x in trace.get("filters", [])):
                fails.append(f"missing filter {f}")
        if exp.get("hits_semantic_layer") and not trace.get("hits_semantic_layer"):
            fails.append("did not resolve through the semantic layer")
    if mode == "behavior" and exp.get("asks_clarification") and not trace.get("asked_clarification"):
        fails.append("should have asked a clarifying question")
    return (len(fails) == 0, fails)

def main(path: str):
    spec = yaml.safe_load(open(path))
    sha, results = git_sha(), []
    for ev in spec["evals"]:
        trace = run_agent(ev["question"])
        ok, fails = grade(ev, trace)
        row = {  # one telemetry row per assertion/run → write to your warehouse, not just stdout
            "domain": spec["domain"], "eval_id": ev["id"], "git_sha": sha,
            "skill_version": trace.get("skill_version"), "model": trace.get("model"),
            "passed": ok, "failures": fails,
            "tokens": trace.get("tokens"), "latency_ms": trace.get("latency_ms"),
        }
        print(json.dumps(row)); results.append(ok)
    rate = sum(results) / len(results) if results else 0.0
    gate = spec.get("gate_threshold", 0.9)
    print(f"\nPASS RATE: {rate:.1%}  (gate {gate:.0%})  domain={spec['domain']}")
    sys.exit(0 if rate >= gate else 1)   # CI fails the PR / blocks the domain launch below the gate

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evals/gold_questions.yml")
