"""
Trust Analysis Module

Computes agreement statistics between LLM judge scores and human annotations,
runs bias probes, and produces a trust verdict per task category / dimension.
"""

import math
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

from data.mt_bench import DIMENSIONS

# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DimensionStats:
    dimension: str
    spearman_rho: float
    spearman_p: float
    cohens_kappa: float
    mean_abs_error: float
    n_samples: int

@dataclass
class CategoryReport:
    category: str
    dimension_stats: list[DimensionStats]
    consistency_variance: dict[str, float]   # dimension → variance across runs
    position_bias_rate: float                # fraction of pairs where order changed verdict
    verbosity_bias_rho: float                # Spearman ρ between response length and score
    verdict: Literal["green", "yellow", "red"]
    verdict_reason: str
    overall_rho: float                       # average Spearman ρ across dimensions

@dataclass
class TrustReport:
    category_reports: list[CategoryReport]
    overall_verdict: Literal["green", "yellow", "red"]
    summary: str


# ── Core analysis functions ───────────────────────────────────────────────────

def compute_dimension_stats(
    judge_scores: list[int],
    human_scores: list[int],
    dimension: str,
) -> DimensionStats:
    """Spearman ρ and Cohen's κ between judge and human scores for one dimension."""
    n = len(judge_scores)
    assert len(human_scores) == n, "Score lists must have the same length."

    if n < 3:
        return DimensionStats(
            dimension=dimension,
            spearman_rho=float("nan"),
            spearman_p=float("nan"),
            cohens_kappa=float("nan"),
            mean_abs_error=float("nan"),
            n_samples=n,
        )

    rho, p = stats.spearmanr(judge_scores, human_scores)
    # Cohen's κ requires matching categories; use buckets 1-5
    try:
        kappa = cohen_kappa_score(human_scores, judge_scores)
    except Exception:
        kappa = float("nan")

    mae = float(np.mean(np.abs(np.array(judge_scores) - np.array(human_scores))))

    return DimensionStats(
        dimension=dimension,
        spearman_rho=round(float(rho), 3),
        spearman_p=round(float(p), 4),
        cohens_kappa=round(float(kappa), 3),
        mean_abs_error=round(mae, 3),
        n_samples=n,
    )


def compute_consistency_variance(
    multi_run_scores: list[list[dict]],
) -> dict[str, float]:
    """
    Given scores from n_runs repeated judge calls (list of list of score dicts),
    return per-dimension variance.
    """
    dim_scores: dict[str, list[int]] = {d: [] for d in DIMENSIONS}
    for run in multi_run_scores:
        for score_dict in run:
            for dim in DIMENSIONS:
                if dim in score_dict:
                    dim_scores[dim].append(int(score_dict[dim]))

    return {
        dim: round(float(np.var(scores)) if scores else float("nan"), 4)
        for dim, scores in dim_scores.items()
    }


def compute_position_bias(
    original_preferences: list[str],
    swapped_preferences: list[str],
) -> float:
    """
    Returns the fraction of cases where flipping A↔B changed the preference verdict.
    A rate > 0.2 indicates notable position bias.
    """
    if not original_preferences:
        return float("nan")
    changed = sum(
        1 for o, s in zip(original_preferences, swapped_preferences)
        if o != s and o != "tie" and s != "tie"
    )
    return round(changed / len(original_preferences), 3)


def compute_verbosity_bias(
    judge_scores: list[int],
    responses: list[str],
    dimension: str = "helpfulness",
) -> float:
    """
    Spearman ρ between response length (in words) and judge score for a dimension.
    A high positive correlation indicates verbosity bias.
    """
    lengths = [len(r.split()) for r in responses]
    if len(set(lengths)) < 2:
        return float("nan")
    rho, _ = stats.spearmanr(lengths, judge_scores)
    return round(float(rho), 3)


def get_trust_verdict(
    category: str,
    dim_stats: list[DimensionStats],
    position_bias_rate: float,
    verbosity_bias_rho: float,
    consistency_variance: dict[str, float],
) -> tuple[Literal["green", "yellow", "red"], str, float]:
    """
    Determines the trust verdict for a category.

    Returns (verdict, reason, overall_rho).
    Thresholds (from proposal):
      green  → avg Spearman ρ > 0.70
      yellow → 0.50 < avg ρ ≤ 0.70
      red    → avg ρ ≤ 0.50
    """
    valid_rhos = [
        s.spearman_rho for s in dim_stats
        if not math.isnan(s.spearman_rho)
    ]
    overall_rho = round(float(np.mean(valid_rhos)), 3) if valid_rhos else float("nan")

    reasons = []

    if math.isnan(overall_rho):
        return "red", "Insufficient data to compute agreement statistics.", overall_rho

    if overall_rho > 0.70:
        base_verdict = "green"
        reasons.append(f"Strong human-judge agreement (avg ρ = {overall_rho:.2f}).")
    elif overall_rho > 0.50:
        base_verdict = "yellow"
        reasons.append(f"Moderate human-judge agreement (avg ρ = {overall_rho:.2f}); use with caution.")
    else:
        base_verdict = "red"
        reasons.append(f"Weak human-judge agreement (avg ρ = {overall_rho:.2f}); human review required.")

    # Escalate for high position bias
    if not math.isnan(position_bias_rate) and position_bias_rate > 0.30:
        reasons.append(f"High position bias detected ({position_bias_rate:.0%} of pairs flip).")
        if base_verdict == "green":
            base_verdict = "yellow"

    # Escalate for high verbosity bias
    if not math.isnan(verbosity_bias_rho) and abs(verbosity_bias_rho) > 0.50:
        reasons.append(f"Verbosity bias detected (length–score ρ = {verbosity_bias_rho:.2f}).")
        if base_verdict == "green":
            base_verdict = "yellow"

    # Escalate for high consistency variance
    avg_var = np.mean([v for v in consistency_variance.values() if not math.isnan(v)])
    if not math.isnan(avg_var) and avg_var > 0.5:
        reasons.append(f"Low consistency across repeated runs (avg variance = {avg_var:.2f}).")
        if base_verdict != "red":
            base_verdict = "yellow"

    return base_verdict, " ".join(reasons), overall_rho


# ── High-level analysis pipeline ─────────────────────────────────────────────

def build_category_report(
    category: str,
    cases: list[dict],
    judge_results: list[dict],          # one dict per case with dimension scores
    pairwise_original: list[str],       # judge preferences (A/B/tie) in original order
    pairwise_swapped: list[str],        # judge preferences with A/B swapped
    consistency_runs: list[list[dict]], # n_runs × n_cases score dicts
) -> CategoryReport:
    """
    Aggregate all statistics for one category into a CategoryReport.

    judge_results: list of dicts like {"helpfulness": 4, "factual_accuracy": 3, ...}
    Each case has human_scores {"helpfulness": {"a": 5, "b": 3}, ...}
    We compare judge score for response_a against human score for response_a.
    """
    dim_stats_list = []
    all_responses_a = [c["response_a"] for c in cases]

    for dim in DIMENSIONS:
        judge_dim_scores = [jr.get(dim, 3) for jr in judge_results]
        human_dim_scores = [c["human_scores"][dim]["a"] for c in cases]
        dim_stats_list.append(
            compute_dimension_stats(judge_dim_scores, human_dim_scores, dim)
        )

    # Consistency
    consistency_var = compute_consistency_variance(consistency_runs)

    # Position bias
    pos_bias = compute_position_bias(pairwise_original, pairwise_swapped)

    # Verbosity bias (helpfulness vs response_a length)
    help_scores = [jr.get("helpfulness", 3) for jr in judge_results]
    verb_bias = compute_verbosity_bias(help_scores, all_responses_a)

    verdict, reason, overall_rho = get_trust_verdict(
        category, dim_stats_list, pos_bias, verb_bias, consistency_var
    )

    return CategoryReport(
        category=category,
        dimension_stats=dim_stats_list,
        consistency_variance=consistency_var,
        position_bias_rate=pos_bias,
        verbosity_bias_rho=verb_bias,
        verdict=verdict,
        verdict_reason=reason,
        overall_rho=overall_rho,
    )


def build_trust_report(category_reports: list[CategoryReport]) -> TrustReport:
    """Roll up category reports into an overall trust verdict."""
    verdicts = [r.verdict for r in category_reports]
    if verdicts.count("red") >= 2:
        overall = "red"
        summary = "Multiple task categories show low LLM-judge reliability. Human review strongly recommended."
    elif "red" in verdicts or verdicts.count("yellow") >= 2:
        overall = "yellow"
        summary = "LLM judge is reliable for some categories. Review flagged categories before deploying."
    else:
        overall = "green"
        summary = "LLM judge shows strong agreement with human annotators across most categories."

    return TrustReport(
        category_reports=category_reports,
        overall_verdict=overall,
        summary=summary,
    )


# ── Utility: format a report as a plain-text summary ─────────────────────────

def format_report(report: TrustReport) -> str:
    lines = [f"OVERALL VERDICT: {report.overall_verdict.upper()}", report.summary, ""]
    for cr in report.category_reports:
        lines.append(f"Category: {cr.category.upper()} — {cr.verdict.upper()}")
        lines.append(f"  Reason: {cr.verdict_reason}")
        lines.append(f"  Overall ρ: {cr.overall_rho:.3f}")
        lines.append(f"  Position bias: {cr.position_bias_rate:.1%}")
        lines.append(f"  Verbosity bias ρ: {cr.verbosity_bias_rho:.3f}")
        lines.append("  Dimension stats:")
        for ds in cr.dimension_stats:
            lines.append(
                f"    {ds.dimension:<18} ρ={ds.spearman_rho:.3f}  κ={ds.cohens_kappa:.3f}  MAE={ds.mean_abs_error:.2f}"
            )
        lines.append("")
    return "\n".join(lines)
