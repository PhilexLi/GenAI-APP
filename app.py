"""
LLM-as-a-Judge Trust Framework
Streamlit application — BU.330.760 Generative AI, Spring 2026
"""

import json
import math
import os
import time
from io import StringIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.mt_bench import CATEGORIES, DIMENSIONS, MT_BENCH_CASES, get_cases_by_category
from modules.analysis import (
    build_category_report,
    build_trust_report,
    compute_dimension_stats,
    compute_position_bias,
    compute_verbosity_bias,
    format_report,
)
from modules.judge import JudgeModule

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LLM-as-a-Judge Trust Framework",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS for verdict colours ───────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .verdict-green  { background:#d4edda; color:#155724; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    .verdict-yellow { background:#fff3cd; color:#856404; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    .verdict-red    { background:#f8d7da; color:#721c24; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    .section-header { border-bottom:2px solid #e0e0e0; padding-bottom:6px;
                      margin-bottom:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

VERDICT_EMOJI = {"green": "✅", "yellow": "⚠️", "red": "🔴"}

# ── Session-state helpers ─────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "judge_results": {},       # case_id → score dict (structured)
        "baseline_results": {},    # case_id → score dict (baseline)
        "pairwise_orig": {},       # case_id → preference
        "pairwise_swap": {},       # case_id → preference (swapped)
        "consistency_runs": {},    # case_id → list[score_dict]
        "eval_complete": False,
        "selected_cases": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


def _verdict_box(verdict: str, text: str):
    st.markdown(
        f'<div class="verdict-{verdict}">{VERDICT_EMOJI[verdict]}  {text}</div>',
        unsafe_allow_html=True,
    )


def _safe_float(v) -> float:
    try:
        f = float(v)
        return f if not math.isnan(f) else 0.0
    except Exception:
        return 0.0


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚖️ LLM Judge Trust")
    st.caption("BU.330.760 · Spring 2026")
    st.divider()

    provider = st.selectbox(
        "API Provider",
        ["qwen", "openai"],
        index=0,
        help="Qwen (DashScope) has a free tier; OpenAI requires billing.",
    )

    if provider == "openai":
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
        )
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=1)
        st.caption("gpt-4o-mini is cheapest (~$0.01 for this project).")
    else:
        api_key = st.text_input(
            "DashScope API Key (千问)",
            type="password",
            value=os.getenv("DASHSCOPE_API_KEY", ""),
            help="Get it at: console.aliyun.com → 模型服务 → DashScope",
        )
        model = st.selectbox(
            "Model",
            ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
            index=0,
        )
        st.caption("qwen-plus / qwen-long 有免费额度，这个项目基本免费跑完。")

    st.divider()
    st.subheader("Evaluation settings")

    selected_categories = st.multiselect(
        "Categories to evaluate",
        CATEGORIES,
        default=CATEGORIES,
    )

    n_cases_per_cat = st.slider(
        "Cases per category",
        min_value=2,
        max_value=9,
        value=5,
        step=1,
        help="Number of cases to send to the judge per category.",
    )

    consistency_runs = st.slider(
        "Consistency runs",
        min_value=1,
        max_value=3,
        value=2,
        help="How many times to re-run the judge on the same response (variance check).",
    )

    run_baseline = st.checkbox(
        "Run baseline comparison",
        value=True,
        help="Also run a minimal prompt (no rubric) for comparison.",
    )

    run_pairwise = st.checkbox(
        "Run pairwise + position-bias check",
        value=True,
        help="Compare response A vs B and detect position bias.",
    )

    st.divider()
    demo_mode = st.checkbox(
        "Demo mode (no API calls)",
        value=False,
        help="Load pre-computed simulated results for demonstration.",
    )


# ── Helpers for demo / mock results ──────────────────────────────────────────

def _mock_judge_score(case: dict, jitter: float = 0.0) -> dict:
    """Generate a realistic mock score slightly below the human score."""
    import random
    rng = random.Random(hash(case["id"]))
    result = {}
    rationale = {}
    for dim in DIMENSIONS:
        human_a = case["human_scores"][dim]["a"]
        delta = rng.choice([-1, 0, 0, 1]) + (rng.uniform(-jitter, jitter))
        result[dim] = max(1, min(5, round(human_a + delta)))
        rationale[dim] = f"Mock rationale for {dim} on case {case['id']}."
    result["rationale"] = rationale
    return result


def _mock_pairwise(case: dict) -> str:
    return case["human_preference"].upper()


def _load_demo_results(cases: list[dict]):
    for case in cases:
        cid = case["id"]
        st.session_state.judge_results[cid] = _mock_judge_score(case)
        st.session_state.baseline_results[cid] = _mock_judge_score(case, jitter=1.2)
        st.session_state.pairwise_orig[cid] = _mock_pairwise(case)
        # Swap: introduce 30% position bias
        import random
        rng = random.Random(hash(cid + "swap"))
        if rng.random() < 0.30:
            flipped = {"A": "B", "B": "A", "tie": "tie"}
            st.session_state.pairwise_swap[cid] = flipped.get(_mock_pairwise(case), "tie")
        else:
            st.session_state.pairwise_swap[cid] = _mock_pairwise(case)
        # Consistency: small variance
        st.session_state.consistency_runs[cid] = [
            _mock_judge_score(case, jitter=0.3) for _ in range(consistency_runs)
        ]
    st.session_state.eval_complete = True


# ── Tab layout ────────────────────────────────────────────────────────────────

tab_eval, tab_trust, tab_bias, tab_compare = st.tabs([
    "📋 Evaluate Batch",
    "📊 Trust Analysis",
    "🔬 Bias Probing",
    "📈 Baseline Comparison",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EVALUATE BATCH
# ══════════════════════════════════════════════════════════════════════════════

with tab_eval:
    st.header("Evaluate a Batch of LLM Responses")
    st.markdown(
        "Select MT-Bench cases and run the GPT-4o judge to score each response "
        "on **helpfulness**, **factual accuracy**, **coherence**, and **safety**."
    )

    # Collect selected cases
    all_selected_cases = []
    for cat in selected_categories:
        cat_cases = get_cases_by_category(cat)[:n_cases_per_cat]
        all_selected_cases.extend(cat_cases)
    st.session_state.selected_cases = all_selected_cases

    cat_counts = ", ".join(
        f"{cat}: {sum(1 for c in all_selected_cases if c['category'] == cat)}"
        for cat in selected_categories
    )
    st.info(f"**{len(all_selected_cases)} cases** selected ({cat_counts})")

    # Preview expandable case list
    with st.expander("Preview selected cases"):
        for case in all_selected_cases:
            st.markdown(f"**[{case['id']}] {case['category'].capitalize()}**")
            st.markdown(f"> {case['question'][:180]}{'...' if len(case['question'])>180 else ''}")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Response A (higher quality)")
                st.text(case["response_a"][:300] + ("..." if len(case["response_a"]) > 300 else ""))
            with col2:
                st.caption("Response B (lower quality)")
                st.text(case["response_b"][:300] + ("..." if len(case["response_b"]) > 300 else ""))
            st.divider()

    # Run button
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        run_btn = st.button(
            "▶ Run Evaluation" if not demo_mode else "▶ Load Demo Results",
            type="primary",
            use_container_width=True,
        )
    with col_btn2:
        if st.session_state.eval_complete:
            st.success(f"Evaluation complete — {len(all_selected_cases)} cases scored.")

    if run_btn:
        if demo_mode:
            with st.spinner("Loading demo results..."):
                _load_demo_results(all_selected_cases)
            st.success("Demo results loaded.")
        elif not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        else:
            judge = JudgeModule(api_key=api_key, model=model, baseline=False, provider=provider)
            baseline_judge = JudgeModule(api_key=api_key, model=model, baseline=True, provider=provider) if run_baseline else None

            progress = st.progress(0, text="Starting evaluation...")
            total_steps = len(all_selected_cases)
            errors = []

            for idx, case in enumerate(all_selected_cases):
                cid = case["id"]
                try:
                    # Structured judge — score response A
                    result = judge.score_response(case["question"], case["response_a"])
                    st.session_state.judge_results[cid] = result

                    # Baseline judge
                    if run_baseline and baseline_judge:
                        b_result = baseline_judge.score_response(case["question"], case["response_a"])
                        st.session_state.baseline_results[cid] = b_result

                    # Pairwise comparison + swap
                    if run_pairwise:
                        orig = judge.compare_responses(
                            case["question"], case["response_a"], case["response_b"]
                        )
                        st.session_state.pairwise_orig[cid] = orig.get("preference", "tie")

                        swap = judge.compare_responses_swapped(
                            case["question"], case["response_a"], case["response_b"]
                        )
                        st.session_state.pairwise_swap[cid] = swap.get("preference", "tie")

                    # Consistency runs (on response A)
                    if consistency_runs > 1:
                        runs = judge.score_with_consistency(
                            case["question"], case["response_a"], n_runs=consistency_runs
                        )
                        st.session_state.consistency_runs[cid] = runs

                except Exception as e:
                    errors.append(f"Case {cid}: {e}")

                progress.progress((idx + 1) / total_steps, text=f"Scored {cid} ({idx+1}/{total_steps})")

            st.session_state.eval_complete = True
            progress.empty()

            if errors:
                st.warning("Some cases had errors:\n" + "\n".join(errors))
            else:
                st.success(f"All {total_steps} cases evaluated successfully.")

    # Show results table if available
    if st.session_state.eval_complete and st.session_state.judge_results:
        st.subheader("Judge Scores vs. Human Annotations")

        rows = []
        for case in all_selected_cases:
            cid = case["id"]
            if cid not in st.session_state.judge_results:
                continue
            jr = st.session_state.judge_results[cid]
            for dim in DIMENSIONS:
                rows.append({
                    "Case ID": cid,
                    "Category": case["category"],
                    "Dimension": dim,
                    "Judge Score": jr.get(dim, "-"),
                    "Human Score": case["human_scores"][dim]["a"],
                    "Difference": jr.get(dim, 0) - case["human_scores"][dim]["a"],
                })

        df = pd.DataFrame(rows)
        st.dataframe(
            df.style.map(
                lambda v: "background-color: #d4edda" if v == 0
                else ("background-color: #fff3cd" if abs(v) == 1 else "background-color: #f8d7da"),
                subset=["Difference"],
            ),
            use_container_width=True,
            height=420,
        )

        # Per-case reasoning panel
        st.subheader("Judge Reasoning")
        case_options = {c["id"]: f"[{c['id']}] {c['question'][:60]}..." for c in all_selected_cases if c["id"] in st.session_state.judge_results}
        if case_options:
            selected_id = st.selectbox("Select a case to inspect", list(case_options.keys()), format_func=lambda x: case_options[x])
            selected_case = next(c for c in all_selected_cases if c["id"] == selected_id)
            jr = st.session_state.judge_results[selected_id]

            col_q, col_r = st.columns([1, 2])
            with col_q:
                st.markdown("**Question**")
                st.write(selected_case["question"])
                st.markdown("**Response A (evaluated)**")
                st.write(selected_case["response_a"])

            with col_r:
                st.markdown("**Judge Scores & Rationale**")
                for dim in DIMENSIONS:
                    score = jr.get(dim, "N/A")
                    human = selected_case["human_scores"][dim]["a"]
                    delta = score - human if isinstance(score, int) else 0
                    color = "#d4edda" if delta == 0 else ("#fff3cd" if abs(delta) == 1 else "#f8d7da")
                    st.markdown(
                        f'<span style="background:{color};padding:2px 8px;border-radius:4px">'
                        f'<b>{dim}</b>: Judge={score} | Human={human}</span>',
                        unsafe_allow_html=True,
                    )
                    rationale = jr.get("rationale", {})
                    if isinstance(rationale, dict):
                        st.caption(rationale.get(dim, ""))
                    st.write("")

        # Download button
        csv_buf = StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇ Download results as CSV",
            data=csv_buf.getvalue(),
            file_name="judge_results.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRUST ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

with tab_trust:
    st.header("Trust Analysis")
    st.markdown(
        "Agreement statistics between the LLM judge and human annotators, "
        "with a per-category trust verdict."
    )

    if not st.session_state.eval_complete:
        st.info("Run the evaluation first (Tab 1) to see results here.")
    else:
        selected_cases = st.session_state.selected_cases
        judge_results = st.session_state.judge_results

        category_reports = []
        for cat in selected_categories:
            cat_cases = [c for c in selected_cases if c["category"] == cat]
            if not cat_cases:
                continue

            cat_judge = [judge_results[c["id"]] for c in cat_cases if c["id"] in judge_results]
            if not cat_judge:
                continue

            pairwise_orig = [
                st.session_state.pairwise_orig.get(c["id"], "tie") for c in cat_cases
            ]
            pairwise_swap = [
                st.session_state.pairwise_swap.get(c["id"], "tie") for c in cat_cases
            ]
            consistency = [
                st.session_state.consistency_runs.get(c["id"], []) for c in cat_cases
            ]

            report = build_category_report(
                category=cat,
                cases=cat_cases,
                judge_results=cat_judge,
                pairwise_original=pairwise_orig,
                pairwise_swapped=pairwise_swap,
                consistency_runs=consistency,
            )
            category_reports.append(report)

        if not category_reports:
            st.warning("No category results available.")
        else:
            trust_report = build_trust_report(category_reports)

            # ── Overall verdict ──
            st.subheader("Overall Trust Verdict")
            _verdict_box(
                trust_report.overall_verdict,
                f"{trust_report.overall_verdict.upper()} — {trust_report.summary}",
            )
            st.write("")

            # ── Per-category verdicts ──
            st.subheader("Per-Category Verdicts")
            cols = st.columns(len(category_reports))
            for col, cr in zip(cols, category_reports):
                with col:
                    _verdict_box(cr.verdict, f"{cr.category.capitalize()}")
                    st.caption(f"Avg ρ = {cr.overall_rho:.3f}")
                    st.caption(cr.verdict_reason[:120])

            st.write("")

            # ── Spearman ρ heatmap ──
            st.subheader("Spearman ρ by Category × Dimension")
            rho_data = []
            for cr in category_reports:
                row = {"Category": cr.category}
                for ds in cr.dimension_stats:
                    row[ds.dimension] = _safe_float(ds.spearman_rho)
                rho_data.append(row)

            rho_df = pd.DataFrame(rho_data).set_index("Category")
            fig_heat = px.imshow(
                rho_df,
                color_continuous_scale=[[0, "#f8d7da"], [0.5, "#fff3cd"], [1, "#d4edda"]],
                zmin=-1, zmax=1,
                text_auto=".2f",
                labels=dict(color="Spearman ρ"),
                title="Human–Judge Agreement (Spearman ρ)",
            )
            fig_heat.update_layout(height=300)
            st.plotly_chart(fig_heat, use_container_width=True)

            # ── Detailed dimension stats table ──
            st.subheader("Detailed Agreement Statistics")
            stat_rows = []
            for cr in category_reports:
                for ds in cr.dimension_stats:
                    stat_rows.append({
                        "Category": cr.category,
                        "Dimension": ds.dimension,
                        "Spearman ρ": f"{_safe_float(ds.spearman_rho):.3f}",
                        "p-value": f"{_safe_float(ds.spearman_p):.4f}",
                        "Cohen's κ": f"{_safe_float(ds.cohens_kappa):.3f}",
                        "Mean Abs Error": f"{_safe_float(ds.mean_abs_error):.2f}",
                        "n": ds.n_samples,
                    })
            st.dataframe(pd.DataFrame(stat_rows), use_container_width=True)

            # ── Items flagged for human review ──
            st.subheader("Cases Flagged for Human Review")
            flagged = []
            for case in selected_cases:
                cid = case["id"]
                if cid not in judge_results:
                    continue
                jr = judge_results[cid]
                for dim in DIMENSIONS:
                    delta = abs(jr.get(dim, 3) - case["human_scores"][dim]["a"])
                    if delta >= 2:
                        flagged.append({
                            "Case ID": cid,
                            "Category": case["category"],
                            "Dimension": dim,
                            "Judge Score": jr.get(dim),
                            "Human Score": case["human_scores"][dim]["a"],
                            "Delta": delta,
                            "Question": case["question"][:80],
                        })

            if flagged:
                flag_df = pd.DataFrame(flagged)
                st.dataframe(flag_df, use_container_width=True)
            else:
                st.success("No cases flagged — all judge-human deltas are within acceptable range.")

            # ── Text export ──
            with st.expander("Export plain-text report"):
                report_text = format_report(trust_report)
                st.code(report_text)
                st.download_button(
                    "⬇ Download report",
                    data=report_text,
                    file_name="trust_report.txt",
                    mime="text/plain",
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BIAS PROBING
# ══════════════════════════════════════════════════════════════════════════════

with tab_bias:
    st.header("Bias Probing")
    st.markdown(
        "Quantify **position bias** (does swapping A/B change the verdict?) "
        "and **verbosity bias** (does response length inflate scores?)."
    )

    if not st.session_state.eval_complete:
        st.info("Run the evaluation first (Tab 1) to see results here.")
    else:
        selected_cases = st.session_state.selected_cases
        judge_results = st.session_state.judge_results

        # ── Position bias ──
        st.subheader("Position Bias")
        orig_prefs = [st.session_state.pairwise_orig.get(c["id"], "tie") for c in selected_cases if c["id"] in judge_results]
        swap_prefs = [st.session_state.pairwise_swap.get(c["id"], "tie") for c in selected_cases if c["id"] in judge_results]

        if orig_prefs:
            pos_bias_rate = compute_position_bias(orig_prefs, swap_prefs)
            pos_col1, pos_col2 = st.columns([1, 2])
            with pos_col1:
                bias_pct = pos_bias_rate * 100 if not math.isnan(pos_bias_rate) else 0
                st.metric("Position bias rate", f"{bias_pct:.1f}%", help="Fraction of pairwise comparisons where flipping A↔B changed the verdict.")
                if bias_pct > 30:
                    _verdict_box("red", f"High position bias ({bias_pct:.1f}%). Judge verdicts are order-dependent.")
                elif bias_pct > 15:
                    _verdict_box("yellow", f"Moderate position bias ({bias_pct:.1f}%). Consider averaging over both orderings.")
                else:
                    _verdict_box("green", f"Low position bias ({bias_pct:.1f}%). Judge appears order-insensitive.")

            with pos_col2:
                # Preference distribution
                pref_df = pd.DataFrame({
                    "Order": ["Original (A first)", "Swapped (B first)"],
                    "Prefer A": [orig_prefs.count("A"), swap_prefs.count("A")],
                    "Prefer B": [orig_prefs.count("B"), swap_prefs.count("B")],
                    "Tie":      [orig_prefs.count("tie"), swap_prefs.count("tie")],
                })
                fig_pref = px.bar(
                    pref_df.melt(id_vars="Order", var_name="Preference", value_name="Count"),
                    x="Order", y="Count", color="Preference",
                    barmode="group",
                    title="Preference Distribution: Original vs. Swapped Order",
                    color_discrete_map={"Prefer A": "#4CAF50", "Prefer B": "#F44336", "Tie": "#9E9E9E"},
                )
                st.plotly_chart(fig_pref, use_container_width=True)

        st.divider()

        # ── Verbosity bias ──
        st.subheader("Verbosity Bias")
        st.markdown(
            "A high correlation between response length and judge score suggests the judge "
            "rewards verbosity rather than quality."
        )

        bias_rows = []
        for case in selected_cases:
            cid = case["id"]
            if cid not in judge_results:
                continue
            jr = judge_results[cid]
            help_score = jr.get("helpfulness", 3)
            length_a = len(case["response_a"].split())
            bias_rows.append({
                "Case ID": cid,
                "Category": case["category"],
                "Response A length (words)": length_a,
                "Helpfulness score": help_score,
                "Coherence score": jr.get("coherence", 3),
            })

        if bias_rows:
            bias_df = pd.DataFrame(bias_rows)

            verb_col1, verb_col2 = st.columns(2)
            with verb_col1:
                lengths = bias_df["Response A length (words)"].tolist()
                help_scores = bias_df["Helpfulness score"].tolist()
                verb_rho = compute_verbosity_bias(help_scores, [c["response_a"] for c in selected_cases if c["id"] in judge_results])
                st.metric("Verbosity bias ρ (helpfulness)", f"{verb_rho:.3f}" if not math.isnan(verb_rho) else "N/A")
                if not math.isnan(verb_rho):
                    if abs(verb_rho) > 0.5:
                        _verdict_box("red", f"Strong verbosity bias (ρ={verb_rho:.2f}). Length predicts score.")
                    elif abs(verb_rho) > 0.3:
                        _verdict_box("yellow", f"Moderate verbosity bias (ρ={verb_rho:.2f}).")
                    else:
                        _verdict_box("green", f"Minimal verbosity bias (ρ={verb_rho:.2f}).")

            with verb_col2:
                fig_scatter = px.scatter(
                    bias_df,
                    x="Response A length (words)",
                    y="Helpfulness score",
                    color="Category",
                    trendline="ols",
                    title="Response Length vs. Helpfulness Score",
                    labels={"Response A length (words)": "Words in response", "Helpfulness score": "Judge helpfulness score"},
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        # ── Consistency analysis ──
        st.subheader("Consistency (Score Variance Across Repeated Runs)")
        var_rows = []
        for case in selected_cases:
            cid = case["id"]
            runs = st.session_state.consistency_runs.get(cid)
            if not runs or len(runs) < 2:
                continue
            for dim in DIMENSIONS:
                dim_vals = [r.get(dim, 3) for r in runs]
                var_rows.append({
                    "Case ID": cid,
                    "Category": case["category"],
                    "Dimension": dim,
                    "Scores": str(dim_vals),
                    "Variance": round(pd.Series(dim_vals).var(), 4),
                })

        if var_rows:
            var_df = pd.DataFrame(var_rows)
            avg_var = var_df["Variance"].mean()
            st.metric("Average score variance across runs", f"{avg_var:.4f}")
            if avg_var > 0.5:
                _verdict_box("yellow", "Notable inconsistency across repeated runs — judge outputs are not fully deterministic.")
            else:
                _verdict_box("green", f"Scores are consistent across repeated runs (avg variance = {avg_var:.4f}).")
            st.dataframe(var_df, use_container_width=True)
        else:
            st.info("Run at least 2 consistency runs to see variance data (adjust in sidebar).")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BASELINE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

with tab_compare:
    st.header("Structured Judge vs. Minimal Prompt Baseline")
    st.markdown(
        "Side-by-side comparison of the **structured rubric judge** against a "
        "**minimal one-line prompt** baseline (no rubric, no output constraints)."
    )

    if not st.session_state.eval_complete:
        st.info("Run the evaluation first (Tab 1) to see results here.")
    elif not st.session_state.baseline_results:
        st.info("Enable 'Run baseline comparison' in the sidebar, then re-run evaluation.")
    else:
        selected_cases = st.session_state.selected_cases
        judge_results = st.session_state.judge_results
        baseline_results = st.session_state.baseline_results

        # Build agreement stats for both
        comparison_rows = []
        for cat in selected_categories:
            cat_cases = [c for c in selected_cases if c["category"] == cat and c["id"] in judge_results]
            if not cat_cases:
                continue
            for dim in DIMENSIONS:
                j_scores = [judge_results[c["id"]].get(dim, 3) for c in cat_cases]
                b_scores = [baseline_results.get(c["id"], {}).get(dim, 3) for c in cat_cases]
                h_scores = [c["human_scores"][dim]["a"] for c in cat_cases]

                j_rho, _ = __import__("scipy").stats.spearmanr(j_scores, h_scores) if len(j_scores) >= 3 else (float("nan"), float("nan"))
                b_rho, _ = __import__("scipy").stats.spearmanr(b_scores, h_scores) if len(b_scores) >= 3 else (float("nan"), float("nan"))

                comparison_rows.append({
                    "Category": cat,
                    "Dimension": dim,
                    "Structured ρ": round(_safe_float(j_rho), 3),
                    "Baseline ρ": round(_safe_float(b_rho), 3),
                    "Δ (Structured − Baseline)": round(_safe_float(j_rho) - _safe_float(b_rho), 3),
                })

        if comparison_rows:
            comp_df = pd.DataFrame(comparison_rows)

            # Summary: wins for structured vs baseline
            structured_wins = (comp_df["Δ (Structured − Baseline)"] > 0).sum()
            total_comparisons = len(comp_df)
            st.metric(
                "Structured judge wins (higher ρ)",
                f"{structured_wins}/{total_comparisons}",
                delta=f"+{structured_wins - (total_comparisons - structured_wins)} vs baseline",
            )

            st.subheader("Agreement Statistics: Structured vs. Baseline")
            st.dataframe(
                comp_df.style.map(
                    lambda v: "background-color: #d4edda" if isinstance(v, float) and v > 0
                    else ("background-color: #f8d7da" if isinstance(v, float) and v < -0.05 else ""),
                    subset=["Δ (Structured − Baseline)"],
                ),
                use_container_width=True,
            )

            # Bar chart
            fig_comp = px.bar(
                comp_df.melt(
                    id_vars=["Category", "Dimension"],
                    value_vars=["Structured ρ", "Baseline ρ"],
                    var_name="Judge Type",
                    value_name="Spearman ρ",
                ),
                x="Dimension",
                y="Spearman ρ",
                color="Judge Type",
                facet_col="Category",
                barmode="group",
                title="Spearman ρ: Structured Judge vs. Minimal Prompt Baseline",
                color_discrete_map={"Structured ρ": "#4CAF50", "Baseline ρ": "#FF9800"},
            )
            fig_comp.add_hline(y=0.7, line_dash="dash", line_color="green", annotation_text="Trust threshold (ρ=0.70)")
            fig_comp.add_hline(y=0.5, line_dash="dash", line_color="orange", annotation_text="Min acceptable (ρ=0.50)")
            fig_comp.update_layout(height=450)
            st.plotly_chart(fig_comp, use_container_width=True)

            # Per-case score comparison
            st.subheader("Per-Case Score Comparison")
            case_rows = []
            for case in selected_cases:
                cid = case["id"]
                if cid not in judge_results or cid not in baseline_results:
                    continue
                jr = judge_results[cid]
                br = baseline_results[cid]
                row = {"Case ID": cid, "Category": case["category"]}
                for dim in DIMENSIONS:
                    row[f"Structured ({dim[:4]})"] = jr.get(dim, "-")
                    row[f"Baseline ({dim[:4]})"] = br.get(dim, "-")
                    row[f"Human ({dim[:4]})"] = case["human_scores"][dim]["a"]
                case_rows.append(row)

            if case_rows:
                st.dataframe(pd.DataFrame(case_rows), use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "BU.330.760 Generative AI · Spring 2026 · Kang Li · "
    "Data: MT-Bench (Zheng et al. 2023) · Judge: GPT-4o"
)
