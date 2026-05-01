"""
Trust Analysis Module — Enterprise Deployment Edition

Computes agreement statistics between LLM judge scores and human annotations,
runs bias probes, produces a trust verdict per category, and generates
deployment recommendations for enterprise automation decisions.
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
    consistency_variance: dict[str, float]
    position_bias_rate: float
    verbosity_bias_rho: float
    verdict: Literal["green", "yellow", "red"]
    verdict_reason: str
    overall_rho: float

@dataclass
class DeploymentRecommendation:
    category: str
    action: str        # "automate" | "hybrid" | "human_required"
    action_label: str
    rationale: str

@dataclass
class CostModelResult:
    full_human_monthly: float
    full_llm_monthly: float
    hybrid_monthly: float
    hybrid_savings_pct: float
    automatable_fraction: float
    avg_accuracy_loss: float

@dataclass
class TrustReport:
    category_reports: list[CategoryReport]
    overall_verdict: Literal["green", "yellow", "red"]
    summary: str
    deployment_recommendations: list[DeploymentRecommendation] = field(default_factory=list)


# ── Core analysis functions ───────────────────────────────────────────────────

def compute_dimension_stats(
    judge_scores: list[int],
    human_scores: list[int],
    dimension: str,
) -> DimensionStats:
    n = len(judge_scores)
    assert len(human_scores) == n

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
    valid_rhos = [s.spearman_rho for s in dim_stats if not math.isnan(s.spearman_rho)]
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

    if not math.isnan(position_bias_rate) and position_bias_rate > 0.30:
        reasons.append(f"High position bias ({position_bias_rate:.0%} of pairs flip).")
        if base_verdict == "green":
            base_verdict = "yellow"

    if not math.isnan(verbosity_bias_rho):
        reasons.append(f"Verbosity bias ρ = {verbosity_bias_rho:.2f} (reported; not used for verdict).")

    return base_verdict, " ".join(reasons), overall_rho


def get_deployment_recommendation(
    verdict: Literal["green", "yellow", "red"],
    overall_rho: float,
    position_bias_rate: float,
    category: str,
) -> DeploymentRecommendation:
    rho_str = f"ρ={overall_rho:.2f}" if not math.isnan(overall_rho) else "ρ=N/A"
    if verdict == "green":
        return DeploymentRecommendation(
            category=category,
            action="automate",
            action_label="✅ Automate",
            rationale=f"Strong agreement ({rho_str}). LLM evaluation can reliably replace human review.",
        )
    elif verdict == "yellow":
        return DeploymentRecommendation(
            category=category,
            action="hybrid",
            action_label="⚠️ Hybrid",
            rationale=f"Moderate agreement ({rho_str}). Use LLM for pre-screening; route ~30% of edge cases to human review.",
        )
    else:
        return DeploymentRecommendation(
            category=category,
            action="human_required",
            action_label="🔴 Human Required",
            rationale=f"Low agreement ({rho_str}). LLM evaluation is not reliable enough to replace human review.",
        )


def compute_cost_model(
    category_reports: list[CategoryReport],
    human_cost_per_case: float,
    llm_cost_per_case: float,
    monthly_volume: int,
) -> CostModelResult:
    if not category_reports:
        return CostModelResult(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    n_cats = len(category_reports)
    green = [cr for cr in category_reports if cr.verdict == "green"]
    yellow = [cr for cr in category_reports if cr.verdict == "yellow"]
    red = [cr for cr in category_reports if cr.verdict == "red"]

    green_frac = len(green) / n_cats
    yellow_frac = len(yellow) / n_cats
    red_frac = len(red) / n_cats

    full_human = monthly_volume * human_cost_per_case
    full_llm = monthly_volume * llm_cost_per_case

    # Hybrid: green→LLM only, yellow→LLM + 30% human spot-check, red→full human
    hybrid = monthly_volume * (
        green_frac * llm_cost_per_case
        + yellow_frac * (llm_cost_per_case + 0.30 * human_cost_per_case)
        + red_frac * human_cost_per_case
    )

    automatable_frac = green_frac + 0.70 * yellow_frac

    auto_maes = []
    for cr in green + yellow:
        valid = [ds.mean_abs_error for ds in cr.dimension_stats if not math.isnan(ds.mean_abs_error)]
        if valid:
            auto_maes.append(float(np.mean(valid)))
    avg_acc_loss = round(float(np.mean(auto_maes)), 3) if auto_maes else 0.0

    savings_pct = (full_human - hybrid) / full_human if full_human > 0 else 0.0

    return CostModelResult(
        full_human_monthly=round(full_human, 2),
        full_llm_monthly=round(full_llm, 2),
        hybrid_monthly=round(hybrid, 2),
        hybrid_savings_pct=round(savings_pct, 3),
        automatable_fraction=round(automatable_frac, 3),
        avg_accuracy_loss=avg_acc_loss,
    )


# ── High-level pipeline ───────────────────────────────────────────────────────

def build_category_report(
    category: str,
    flat_cases: list[dict],
    judge_results: list[dict],
    pairwise_original: list[str],
    pairwise_swapped: list[str],
    consistency_runs: list[list[dict]],
) -> CategoryReport:
    """
    flat_cases: list of flat eval dicts (from get_flat_eval_cases) for this category.
    judge_results: one score dict per flat_case, in the same order.
    """
    dim_stats_list = []
    all_responses = [ec["response"] for ec in flat_cases]

    for dim in DIMENSIONS:
        judge_dim_scores = [jr.get(dim, 3) for jr in judge_results]
        human_dim_scores = [ec["human_scores"][dim] for ec in flat_cases]
        dim_stats_list.append(compute_dimension_stats(judge_dim_scores, human_dim_scores, dim))

    consistency_var = compute_consistency_variance(consistency_runs)
    pos_bias = compute_position_bias(pairwise_original, pairwise_swapped)
    help_scores = [jr.get("helpfulness", 3) for jr in judge_results]
    verb_bias = compute_verbosity_bias(help_scores, all_responses)
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
    verdicts = [r.verdict for r in category_reports]
    if verdicts.count("red") >= 2:
        overall = "red"
        summary = "Multiple task categories show low LLM-judge reliability. Human review strongly recommended."
    elif "red" in verdicts or verdicts.count("yellow") >= 2:
        overall = "yellow"
        summary = "LLM judge is reliable for some categories. Use a hybrid approach before full deployment."
    else:
        overall = "green"
        summary = "LLM judge shows strong agreement with human annotators. Automation is viable."

    recs = [
        get_deployment_recommendation(cr.verdict, cr.overall_rho, cr.position_bias_rate, cr.category)
        for cr in category_reports
    ]

    return TrustReport(
        category_reports=category_reports,
        overall_verdict=overall,
        summary=summary,
        deployment_recommendations=recs,
    )


# ── Report formatter ──────────────────────────────────────────────────────────

def format_report(report: TrustReport) -> str:
    lines = [
        f"OVERALL VERDICT: {report.overall_verdict.upper()}",
        report.summary,
        "",
        "DEPLOYMENT RECOMMENDATIONS",
        "-" * 40,
    ]
    for rec in report.deployment_recommendations:
        lines.append(f"  {rec.category.upper()}: {rec.action_label}")
        lines.append(f"    {rec.rationale}")
    lines += ["", "DETAILED STATISTICS", "-" * 40]
    for cr in report.category_reports:
        lines.append(f"Category: {cr.category.upper()} — {cr.verdict.upper()}")
        lines.append(f"  {cr.verdict_reason}")
        lines.append(f"  Overall ρ: {cr.overall_rho:.3f}")
        lines.append(f"  Position bias: {cr.position_bias_rate:.1%}")
        lines.append(f"  Verbosity bias ρ: {cr.verbosity_bias_rho:.3f}")
        for ds in cr.dimension_stats:
            lines.append(
                f"    {ds.dimension:<18} ρ={ds.spearman_rho:.3f}  κ={ds.cohens_kappa:.3f}  MAE={ds.mean_abs_error:.2f}"
            )
        lines.append("")
    return "\n".join(lines)
