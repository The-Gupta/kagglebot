"""
End-to-End Test — Validates the full KaggleBot pipeline without LLM calls.

Tests all modules in sequence:
  Web Scraper → Data Server → Strategy Ranker → Code Templates → Security → Memory → Observability → Evaluation

This test runs without an API key — it tests the tool/skill layer only.
"""

import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_competition(slug: str, train_path: str, target_col: str):
    """Run a full pipeline test for a single competition."""
    print(f"\n{'='*60}")
    print(f"  Testing: {slug}")
    print(f"{'='*60}")

    # 1. Web Scraper
    from mcp_servers.web_scraper_server import get_known_competition
    cached = get_known_competition(slug)
    assert cached is not None, f"No cached data for {slug}"
    print(f"  ✅ Scraper: {cached['title']} ({cached['competition_type']})")

    # 2. Data Server
    from mcp_servers.data_server import (
        load_dataset, compute_profile, analyze_target, detect_issues
    )
    if os.path.exists(train_path):
        load_result = load_dataset(train_path)
        assert load_result["shape"]["rows"] > 0
        print(f"  ✅ Data Load: {load_result['shape']}")

        profile = compute_profile(train_path)
        assert len(profile["columns"]) > 0
        print(f"  ✅ Profile: {len(profile['columns'])} columns profiled")

        target = analyze_target(train_path, target_col)
        assert "task_type" in target
        print(f"  ✅ Target: {target['task_type']}")

        issues = detect_issues(train_path)
        print(f"  ✅ Issues: quality_score={issues['overall_quality_score']}/100")
    else:
        print(f"  ⏭️  Data: skipped (no file at {train_path})")

    # 3. Strategy Ranker
    from skills.strategy_ranker import get_strategies_for_type, rank_strategies
    strategies = get_strategies_for_type(cached["competition_type"])
    ranked = rank_strategies(strategies, dataset_size=100, num_features=10)
    assert len(ranked) >= 1
    print(f"  ✅ Strategies: {len(ranked)} ranked (top: {ranked[0]['name']})")

    # 4. Code Templates
    from skills.code_templates import generate_full_baseline
    code = generate_full_baseline(
        train_path=train_path,
        target_column=target_col,
        task_type=cached["competition_type"],
        model_family=ranked[0]["model_family"],
        metric="accuracy",
    )
    assert len(code) > 100
    print(f"  ✅ Code: {len(code.splitlines())} lines generated")

    # 5. Security
    from security.safe_code_gen import check_code_safety
    from security.secret_scanner import is_safe
    safety = check_code_safety(code)
    secrets_ok = is_safe(code)
    assert safety["is_safe"], f"Code safety failed: {safety['issues']}"
    assert secrets_ok, "Secret scanner found issues"
    print(f"  ✅ Security: safe={safety['is_safe']}, no_secrets={secrets_ok}")

    # 6. Input Validation
    from security.input_validator import validate_kaggle_url, ValidationError
    url = f"https://www.kaggle.com/competitions/{slug}"
    validated = validate_kaggle_url(url)
    assert validated == url
    print(f"  ✅ Validation: URL accepted")

    print(f"  🎉 {slug} — ALL TESTS PASSED")
    return True


def test_memory():
    """Test the memory system."""
    print(f"\n{'='*60}")
    print(f"  Testing: Memory System")
    print(f"{'='*60}")

    from context.memory_manager import MemoryManager
    mm = MemoryManager(filepath="output/test_e2e_memory.json")
    mm.clear()

    # Store
    mm.store("test_key", "Test insight", "strategy", "binary_classification", "test")
    assert mm.get_stats()["total_memories"] == 1
    print("  ✅ Store: 1 memory saved")

    # Retrieve
    results = mm.retrieve(competition_type="binary_classification")
    assert len(results) >= 1
    print(f"  ✅ Retrieve: {len(results)} memories found")

    # Cleanup
    mm.clear()
    os.remove("output/test_e2e_memory.json")
    print("  ✅ Cleanup: done")
    print("  🎉 Memory — ALL TESTS PASSED")


def test_observability():
    """Test the tracing system."""
    print(f"\n{'='*60}")
    print(f"  Testing: Observability")
    print(f"{'='*60}")

    from observability.tracing import Tracer
    from observability.trace_viewer import render_trace_tree, render_trace_summary

    tracer = Tracer("e2e-test")
    with tracer.span("test_root", "agent") as root:
        with tracer.span("test_tool", "tool") as tool:
            tool.set_attribute("key", "value")
            time.sleep(0.01)

    tree = render_trace_tree(tracer)
    assert "test_root" in tree
    assert "test_tool" in tree
    print("  ✅ Trace tree rendered")

    summary = render_trace_summary(tracer)
    assert "Agents: 1" in summary
    print("  ✅ Trace summary rendered")

    path = tracer.export_json("output/test_e2e_trace.json")
    assert os.path.exists(path)
    os.remove(path)
    print("  ✅ JSON export works")
    print("  🎉 Observability — ALL TESTS PASSED")


def test_evaluation():
    """Test the evaluation system."""
    print(f"\n{'='*60}")
    print(f"  Testing: Evaluation")
    print(f"{'='*60}")

    from evaluation.eval_criteria import (
        get_rubric_text, compute_weighted_score, get_eval_prompt
    )

    rubric = get_rubric_text()
    assert len(rubric) > 100
    print(f"  ✅ Rubric: {len(rubric.splitlines())} lines")

    scores = {"relevance": 4, "feasibility": 5, "ranking_quality": 4,
              "completeness": 4, "novelty": 3}
    weighted = compute_weighted_score(scores)
    assert 3.0 <= weighted <= 5.0
    print(f"  ✅ Scoring: weighted={weighted}/5.0")

    prompt = get_eval_prompt("test strategies", "test context")
    assert "Score EACH criterion" in prompt
    print(f"  ✅ Prompt: {len(prompt)} chars")
    print("  🎉 Evaluation — ALL TESTS PASSED")


def test_imports():
    """Test that all agent imports work."""
    print(f"\n{'='*60}")
    print(f"  Testing: Agent Imports")
    print(f"{'='*60}")

    from agents.orchestrator import orchestrator_agent
    assert orchestrator_agent.name == "kagglebot_orchestrator"
    assert len(orchestrator_agent.sub_agents) == 4
    names = [a.name for a in orchestrator_agent.sub_agents]
    assert "scraper_agent" in names
    assert "data_agent" in names
    assert "strategy_agent" in names
    assert "code_agent" in names
    print(f"  ✅ Orchestrator: {orchestrator_agent.name}")
    print(f"  ✅ Sub-agents: {names}")
    print(f"  ✅ Tools: {len(orchestrator_agent.tools)} memory tools")
    print("  🎉 Imports — ALL TESTS PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("  🤖 KaggleBot End-to-End Test Suite")
    print("=" * 60)

    start = time.time()
    passed = 0
    failed = 0

    tests = [
        ("Titanic", lambda: test_competition(
            "titanic", "data/titanic_train.csv", "Survived")),
        ("House Prices", lambda: test_competition(
            "house-prices-advanced-regression-techniques",
            "data/house_prices_train.csv", "SalePrice")),
        ("Spaceship Titanic", lambda: test_competition(
            "spaceship-titanic", "data/spaceship_train.csv", "Transported")),
        ("Memory", test_memory),
        ("Observability", test_observability),
        ("Evaluation", test_evaluation),
        ("Agent Imports", test_imports),
    ]

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ {name} FAILED: {e}")
            failed += 1

    elapsed = round(time.time() - start, 2)
    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed} passed, {failed} failed ({elapsed}s)")
    print(f"{'='*60}")

    sys.exit(0 if failed == 0 else 1)
