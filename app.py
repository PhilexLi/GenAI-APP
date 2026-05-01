"""
LLM-as-a-Judge Enterprise Trust Calibration
Streamlit application — BU.330.760 Generative AI, Spring 2026
"""

import math
import os
from io import StringIO

import pandas as pd
import plotly.express as px
import streamlit as st

from data.mt_bench import CATEGORIES, DIMENSIONS, get_cases_by_category, get_flat_eval_cases
from modules.analysis import (
    build_category_report,
    build_trust_report,
    compute_position_bias,
    compute_verbosity_bias,
    format_report,
)
from modules.judge import JudgeModule

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LLM Evaluation Trust Calibration",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .verdict-green  { background:#d4edda; color:#155724; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    .verdict-yellow { background:#fff3cd; color:#856404; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    .verdict-red    { background:#f8d7da; color:#721c24; border-radius:8px;
                      padding:12px 18px; font-weight:600; font-size:1.1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

VERDICT_EMOJI = {"green": "✅", "yellow": "⚠️", "red": "🔴"}

# ── Session state ─────────────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "judge_results": {},       # eval_id → score dict
        "pairwise_orig": {},       # case_id → preference
        "pairwise_swap": {},       # case_id → preference (swapped)
        "consistency_runs": {},    # eval_id → list[score_dict]
        "eval_complete": False,
        "selected_cases": [],
        "flat_eval_cases": [],
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


# ── Custom CSV loader ─────────────────────────────────────────────────────────

def _load_custom_csv(file) -> list[dict]:
    try:
        df = pd.read_csv(file)
        required = {"id", "category", "question", "response_a", "response_b"}
        missing = required - set(df.columns)
        if missing:
            st.error(f"CSV missing required columns: {', '.join(sorted(missing))}")
            return []

        # Detect whether per-dimension columns exist
        per_dim_cols = [f"score_a_{d}" for d in DIMENSIONS] + [f"score_b_{d}" for d in DIMENSIONS]
        has_per_dim = all(c in df.columns for c in per_dim_cols)
        has_overall = "score_a" in df.columns and "score_b" in df.columns
        if not has_per_dim and not has_overall:
            st.warning(
                "No score columns found. "
                "Provide either per-dimension columns "
                "(score_a_helpfulness, score_a_factual_accuracy, score_a_coherence, score_a_safety "
                "and the matching score_b_* columns) "
                "or a single score_a / score_b column as a fallback. "
                "Defaulting to score_a=5, score_b=2 for all dimensions."
            )

        cases = []
        for _, row in df.iterrows():
            if has_per_dim:
                human_scores = {
                    dim: {
                        "a": max(1, min(5, int(row[f"score_a_{dim}"]))),
                        "b": max(1, min(5, int(row[f"score_b_{dim}"]))),
                    }
                    for dim in DIMENSIONS
                }
            else:
                score_a = max(1, min(5, int(row.get("score_a", 5))))
                score_b = max(1, min(5, int(row.get("score_b", 2))))
                human_scores = {dim: {"a": score_a, "b": score_b} for dim in DIMENSIONS}

            cases.append({
                "id": str(row["id"]),
                "category": str(row["category"]).strip().lower(),
                "question": str(row["question"]),
                "response_a": str(row["response_a"]),
                "response_b": str(row["response_b"]),
                "human_scores": human_scores,
                "human_preference": "a",
            })
        return cases
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return []


_SAMPLE_CSV = (
    "id,category,question,response_a,response_b,"
    "score_a_helpfulness,score_a_factual_accuracy,score_a_coherence,score_a_safety,"
    "score_b_helpfulness,score_b_factual_accuracy,score_b_coherence,score_b_safety\n"
    "CUSTOM1,hr_screening,Does this candidate have Python experience?,"
    "\"Yes — 5 years with Django FastAPI and ML pipelines.\","
    "\"Maybe, the resume mentions some coding.\","
    "5,5,5,5,2,3,2,5\n"
    "CUSTOM2,hr_screening,Is the candidate suitable for a senior role?,"
    "\"Strong fit: led a team of 8 and shipped 3 major products.\","
    "\"Hard to say without more context.\","
    "5,5,5,5,2,2,2,5\n"
)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚖️ LLM Judge Trust")
    st.caption("BU.330.760 · Spring 2026")
    st.caption("*When can enterprises trust LLM evaluation to replace human review?*")
    st.divider()

    provider = st.selectbox("API Provider", ["qwen", "openai"], index=0)

    if provider == "openai":
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=1)
        st.caption("gpt-4o-mini is cheapest (~$0.01 for this project).")
    else:
        api_key = st.text_input(
            "DashScope API Key (Qwen)", type="password",
            value=os.getenv("DASHSCOPE_API_KEY", ""),
            help="Get it at: console.aliyun.com → Model Services → DashScope",
        )
        model = st.selectbox("Model", ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"], index=0)
        st.caption("qwen-plus / qwen-long have a free tier — enough to run this project at no cost.")

    st.divider()
    st.subheader("Custom Categories")
    uploaded_file = st.file_uploader(
        "Upload cases (CSV)",
        type="csv",
        help=(
            "Required columns: id, category, question, response_a, response_b. "
            "Human scores (1–5): provide per-dimension columns "
            "score_a_helpfulness, score_a_factual_accuracy, score_a_coherence, score_a_safety "
            "and the matching score_b_* columns (recommended), "
            "or a single score_a / score_b as a fallback (duplicated across all dimensions)."
        ),
    )
    custom_cases = _load_custom_csv(uploaded_file) if uploaded_file else []
    if custom_cases:
        custom_cat_names = sorted(set(c["category"] for c in custom_cases))
        st.success(f"Loaded {len(custom_cases)} cases — categories: {', '.join(custom_cat_names)}")
    st.download_button(
        "⬇ Download CSV template",
        data=_SAMPLE_CSV,
        file_name="custom_cases_template.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Evaluation settings")

    _custom_cats = sorted(set(c["category"] for c in custom_cases))
    _all_cats = CATEGORIES + [c for c in _custom_cats if c not in CATEGORIES]
    selected_categories = st.multiselect("Categories to evaluate", _all_cats, default=_all_cats)

    n_cases_per_cat = st.slider(
        "Cases per category", min_value=2, max_value=9, value=5, step=1,
        help="Each case produces 2 evaluations (high + low quality response).",
    )
    run_pairwise = st.checkbox("Run pairwise + position-bias check", value=True)

    st.divider()
    demo_mode = st.checkbox("Demo mode (no API calls)", value=False,
        help="Load pre-computed simulated results for demonstration.")


# ── Mock helpers ──────────────────────────────────────────────────────────────

def _mock_flat_score(eval_case: dict, jitter: float = 0.3) -> dict:
    import random
    rng = random.Random(hash(eval_case["eval_id"]))
    result = {}
    rationale = {}
    for dim in DIMENSIONS:
        human = eval_case["human_scores"][dim]
        delta = rng.choice([-1, 0, 0, 1]) + rng.uniform(-jitter, jitter)
        result[dim] = max(1, min(5, round(human + delta)))
        rationale[dim] = f"Mock rationale for {dim} on {eval_case['eval_id']}."
    result["rationale"] = rationale
    return result


def _mock_pairwise(case: dict) -> str:
    return case["human_preference"].upper()


def _load_demo_results(flat_cases: list[dict], orig_cases: list[dict]):
    import random
    for ec in flat_cases:
        eid = ec["eval_id"]
        jitter = 0.4 if ec["variant"] == "a" else 0.8
        st.session_state.judge_results[eid] = _mock_flat_score(ec, jitter)

    for case in orig_cases:
        cid = case["id"]
        st.session_state.pairwise_orig[cid] = _mock_pairwise(case)
        rng = random.Random(hash(cid + "swap"))
        flipped = {"A": "B", "B": "A", "tie": "tie"}
        if rng.random() < 0.30:
            st.session_state.pairwise_swap[cid] = flipped.get(_mock_pairwise(case), "tie")
        else:
            st.session_state.pairwise_swap[cid] = _mock_pairwise(case)

    st.session_state.eval_complete = True


# ── Tab layout ────────────────────────────────────────────────────────────────

tab_eval, tab_trust, tab_bias = st.tabs([
    "📋 Evaluate Responses",
    "📊 Trust & Deployment",
    "🔬 Bias Analysis",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EVALUATE RESPONSES
# ══════════════════════════════════════════════════════════════════════════════

with tab_eval:
    st.header("Evaluate a Batch of Responses")
    st.markdown(
        "Evaluates **both high-quality (A) and low-quality (B) responses** for each case, "
        "producing the score variance needed for meaningful agreement statistics."
    )

    all_selected_cases = []
    for cat in selected_categories:
        if cat in CATEGORIES:
            all_selected_cases.extend(get_cases_by_category(cat)[:n_cases_per_cat])
        else:
            all_selected_cases.extend([c for c in custom_cases if c["category"] == cat])
    st.session_state.selected_cases = all_selected_cases

    flat_eval_cases = get_flat_eval_cases(all_selected_cases)
    st.session_state.flat_eval_cases = flat_eval_cases

    cat_counts = ", ".join(
        f"{cat}: {sum(1 for c in all_selected_cases if c['category'] == cat)}"
        for cat in selected_categories
    )
    st.info(
        f"**{len(flat_eval_cases)} response evaluations** from {len(all_selected_cases)} cases "
        f"({cat_counts}) — each case contributes one high-quality and one low-quality response."
    )

    with st.expander("Preview selected cases"):
        for case in all_selected_cases:
            st.markdown(f"**[{case['id']}] {case['category'].capitalize()}**")
            st.markdown(f"> {case['question'][:180]}{'...' if len(case['question']) > 180 else ''}")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Response A — high quality")
                st.text(case["response_a"][:300] + ("..." if len(case["response_a"]) > 300 else ""))
            with col2:
                st.caption("Response B — low quality")
                st.text(case["response_b"][:300] + ("..." if len(case["response_b"]) > 300 else ""))
            st.divider()

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        run_btn = st.button(
            "▶ Run Evaluation" if not demo_mode else "▶ Load Demo Results",
            type="primary", use_container_width=True,
        )
    with col_btn2:
        if st.session_state.eval_complete:
            st.success(f"Evaluation complete — {len(flat_eval_cases)} responses scored.")

    if run_btn:
        if demo_mode:
            with st.spinner("Loading demo results..."):
                _load_demo_results(flat_eval_cases, all_selected_cases)
            st.success("Demo results loaded.")
        elif not api_key:
            provider_name = "DashScope" if provider == "qwen" else "OpenAI"
            st.error(f"Please enter your {provider_name} API key in the sidebar.")
        else:
            judge = JudgeModule(api_key=api_key, model=model, provider=provider)

            total_steps = len(flat_eval_cases) + (len(all_selected_cases) if run_pairwise else 0)
            progress = st.progress(0, text="Starting evaluation...")
            errors = []
            step = 0

            for eval_case in flat_eval_cases:
                eid = eval_case["eval_id"]
                try:
                    result = judge.score_response(eval_case["question"], eval_case["response"])
                    st.session_state.judge_results[eid] = result
                except Exception as e:
                    errors.append(f"{eid}: {e}")

                step += 1
                progress.progress(step / total_steps, text=f"Scoring {eid} ({step}/{total_steps})")

            if run_pairwise:
                for case in all_selected_cases:
                    cid = case["id"]
                    try:
                        orig = judge.compare_responses(case["question"], case["response_a"], case["response_b"])
                        st.session_state.pairwise_orig[cid] = orig.get("preference", "tie")
                        swap = judge.compare_responses_swapped(case["question"], case["response_a"], case["response_b"])
                        st.session_state.pairwise_swap[cid] = swap.get("preference", "tie")
                    except Exception as e:
                        errors.append(f"Pairwise {cid}: {e}")
                    step += 1
                    progress.progress(step / total_steps, text=f"Pairwise {cid} ({step}/{total_steps})")

            st.session_state.eval_complete = True
            progress.empty()

            if errors:
                st.warning("Some cases had errors:\n" + "\n".join(errors))
            else:
                st.success(f"All {len(flat_eval_cases)} responses evaluated successfully.")

    if st.session_state.eval_complete and st.session_state.judge_results:
        st.subheader("Judge Scores vs. Human Annotations")

        rows = []
        for ec in flat_eval_cases:
            eid = ec["eval_id"]
            if eid not in st.session_state.judge_results:
                continue
            jr = st.session_state.judge_results[eid]
            for dim in DIMENSIONS:
                rows.append({
                    "Case ID": ec["case_id"],
                    "Quality": "High (A)" if ec["variant"] == "a" else "Low (B)",
                    "Category": ec["category"],
                    "Dimension": dim,
                    "Judge Score": jr.get(dim, "-"),
                    "Human Score": ec["human_scores"][dim],
                    "Difference": jr.get(dim, 0) - ec["human_scores"][dim],
                })

        df = pd.DataFrame(rows)
        st.dataframe(
            df.style.map(
                lambda v: "background-color: #d4edda" if v == 0
                else ("background-color: #fff3cd" if abs(v) == 1 else "background-color: #f8d7da"),
                subset=["Difference"],
            ),
            use_container_width=True, height=420,
        )

        st.subheader("Judge Reasoning")
        eval_options = {
            ec["eval_id"]: f"[{ec['eval_id']}] {'High' if ec['variant']=='a' else 'Low'} quality — {ec['question'][:50]}..."
            for ec in flat_eval_cases if ec["eval_id"] in st.session_state.judge_results
        }
        if eval_options:
            selected_eid = st.selectbox("Select a response to inspect", list(eval_options.keys()), format_func=lambda x: eval_options[x])
            selected_ec = next(ec for ec in flat_eval_cases if ec["eval_id"] == selected_eid)
            jr = st.session_state.judge_results[selected_eid]

            col_q, col_r = st.columns([1, 2])
            with col_q:
                st.markdown("**Question**")
                st.write(selected_ec["question"])
                quality_label = "High quality (A)" if selected_ec["variant"] == "a" else "Low quality (B)"
                st.markdown(f"**Response ({quality_label})**")
                st.write(selected_ec["response"])
            with col_r:
                st.markdown("**Judge Scores & Rationale**")
                for dim in DIMENSIONS:
                    score = jr.get(dim, "N/A")
                    human = selected_ec["human_scores"][dim]
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

        csv_buf = StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button("⬇ Download results as CSV", data=csv_buf.getvalue(),
                           file_name="judge_results.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRUST & DEPLOYMENT
# ══════════════════════════════════════════════════════════════════════════════

def _build_category_reports(flat_eval_cases, selected_cases, judge_results, selected_categories):
    reports = []
    for cat in selected_categories:
        cat_flat = [ec for ec in flat_eval_cases if ec["category"] == cat and ec["eval_id"] in judge_results]
        if not cat_flat:
            continue
        cat_judge = [judge_results[ec["eval_id"]] for ec in cat_flat]
        cat_orig = [c for c in selected_cases if c["category"] == cat]
        pairwise_orig = [st.session_state.pairwise_orig.get(c["id"], "tie") for c in cat_orig]
        pairwise_swap = [st.session_state.pairwise_swap.get(c["id"], "tie") for c in cat_orig]
        consistency = [st.session_state.consistency_runs.get(ec["eval_id"], []) for ec in cat_flat]
        reports.append(build_category_report(
            category=cat,
            flat_cases=cat_flat,
            judge_results=cat_judge,
            pairwise_original=pairwise_orig,
            pairwise_swapped=pairwise_swap,
            consistency_runs=consistency,
        ))
    return reports


with tab_trust:
    st.header("Trust Analysis & Deployment Decision")
    st.markdown(
        "Agreement statistics between the LLM judge and human annotators, "
        "with a **per-category deployment recommendation** for enterprise automation."
    )

    if not st.session_state.eval_complete:
        st.info("Run the evaluation first (Tab 1) to see results here.")
    else:
        flat_eval_cases = st.session_state.flat_eval_cases
        selected_cases = st.session_state.selected_cases
        judge_results = st.session_state.judge_results

        category_reports = _build_category_reports(flat_eval_cases, selected_cases, judge_results, selected_categories)

        if not category_reports:
            st.warning("No category results available.")
        else:
            trust_report = build_trust_report(category_reports)

            st.subheader("Overall Trust Verdict")
            _verdict_box(trust_report.overall_verdict,
                         f"{trust_report.overall_verdict.upper()} — {trust_report.summary}")
            st.write("")

            st.subheader("Deployment Recommendations")
            st.caption("Based on LLM-human agreement, bias detection, and consistency analysis.")

            rec_rows = []
            for rec in trust_report.deployment_recommendations:
                cr = next(r for r in category_reports if r.category == rec.category)
                rec_rows.append({
                    "Category": rec.category.capitalize(),
                    "Trust Level": cr.verdict.upper(),
                    "Recommendation": rec.action_label,
                    "Avg ρ": f"{cr.overall_rho:.3f}",
                    "Position Bias": f"{cr.position_bias_rate:.1%}" if not math.isnan(cr.position_bias_rate) else "N/A",
                    "Rationale": rec.rationale,
                })

            def _color_rec(val):
                if "Automate" in str(val):
                    return "background-color: #d4edda"
                elif "Hybrid" in str(val):
                    return "background-color: #fff3cd"
                elif "Human" in str(val):
                    return "background-color: #f8d7da"
                return ""

            st.dataframe(
                pd.DataFrame(rec_rows).style.map(_color_rec, subset=["Recommendation"]),
                use_container_width=True,
            )
            st.write("")

            st.subheader("Per-Category Trust Verdicts")
            cols = st.columns(len(category_reports))
            for col, cr in zip(cols, category_reports):
                with col:
                    _verdict_box(cr.verdict, f"{cr.category.capitalize()}")
                    st.caption(f"Avg ρ = {cr.overall_rho:.3f}")
                    st.caption(cr.verdict_reason[:120])
            st.write("")

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
                zmin=-1, zmax=1, text_auto=".2f",
                labels=dict(color="Spearman ρ"),
                title="Human–Judge Agreement (Spearman ρ)",
            )
            fig_heat.update_layout(height=300)
            st.plotly_chart(fig_heat, use_container_width=True)

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

            st.subheader("Cases Flagged for Human Review")
            flagged = []
            for ec in flat_eval_cases:
                eid = ec["eval_id"]
                if eid not in judge_results:
                    continue
                jr = judge_results[eid]
                for dim in DIMENSIONS:
                    delta = abs(jr.get(dim, 3) - ec["human_scores"][dim])
                    if delta >= 2:
                        flagged.append({
                            "Eval ID": eid,
                            "Category": ec["category"],
                            "Quality": "High (A)" if ec["variant"] == "a" else "Low (B)",
                            "Dimension": dim,
                            "Judge Score": jr.get(dim),
                            "Human Score": ec["human_scores"][dim],
                            "Delta": delta,
                            "Question": ec["question"][:80],
                        })
            if flagged:
                st.dataframe(pd.DataFrame(flagged), use_container_width=True)
            else:
                st.success("No cases flagged — all judge-human deltas are within acceptable range.")

            with st.expander("Export plain-text report"):
                report_text = format_report(trust_report)
                st.code(report_text)
                st.download_button("⬇ Download report", data=report_text,
                                   file_name="trust_report.txt", mime="text/plain")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BIAS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

with tab_bias:
    st.header("Bias Analysis")
    st.markdown(
        "Quantify **position bias** (does swapping A/B change the verdict?) "
        "and **verbosity bias** (does response length inflate scores?)."
    )

    if not st.session_state.eval_complete:
        st.info("Run the evaluation first (Tab 1) to see results here.")
    else:
        flat_eval_cases = st.session_state.flat_eval_cases
        selected_cases = st.session_state.selected_cases
        judge_results = st.session_state.judge_results

        # Position bias
        st.subheader("Position Bias")
        evaluated_cases = [c for c in selected_cases if c["id"] in st.session_state.pairwise_orig]
        orig_prefs = [st.session_state.pairwise_orig.get(c["id"], "tie") for c in evaluated_cases]
        swap_prefs = [st.session_state.pairwise_swap.get(c["id"], "tie") for c in evaluated_cases]

        if orig_prefs:
            pos_bias_rate = compute_position_bias(orig_prefs, swap_prefs)
            pos_col1, pos_col2 = st.columns([1, 2])
            with pos_col1:
                bias_pct = pos_bias_rate * 100 if not math.isnan(pos_bias_rate) else 0
                st.metric("Position bias rate", f"{bias_pct:.1f}%",
                          help="Fraction of pairwise comparisons where flipping A↔B changed the verdict.")
                if bias_pct > 30:
                    _verdict_box("red", f"High position bias ({bias_pct:.1f}%). Verdicts are order-dependent.")
                elif bias_pct > 15:
                    _verdict_box("yellow", f"Moderate position bias ({bias_pct:.1f}%). Consider averaging both orderings.")
                else:
                    _verdict_box("green", f"Low position bias ({bias_pct:.1f}%). Judge is order-insensitive.")
            with pos_col2:
                pref_df = pd.DataFrame({
                    "Order": ["Original (A first)", "Swapped (B first)"],
                    "Prefer A": [orig_prefs.count("A"), swap_prefs.count("A")],
                    "Prefer B": [orig_prefs.count("B"), swap_prefs.count("B")],
                    "Tie":      [orig_prefs.count("tie"), swap_prefs.count("tie")],
                })
                fig_pref = px.bar(
                    pref_df.melt(id_vars="Order", var_name="Preference", value_name="Count"),
                    x="Order", y="Count", color="Preference", barmode="group",
                    title="Preference Distribution: Original vs. Swapped Order",
                    color_discrete_map={"Prefer A": "#4CAF50", "Prefer B": "#F44336", "Tie": "#9E9E9E"},
                )
                st.plotly_chart(fig_pref, use_container_width=True)
        else:
            st.info("Enable 'Run pairwise + position-bias check' in the sidebar.")

        st.divider()

        # Verbosity bias
        st.subheader("Verbosity Bias")
        st.markdown("A high correlation between response length and judge score suggests the judge rewards verbosity rather than quality.")

        bias_rows = []
        for ec in flat_eval_cases:
            eid = ec["eval_id"]
            if eid not in judge_results:
                continue
            jr = judge_results[eid]
            bias_rows.append({
                "Eval ID": eid,
                "Category": ec["category"],
                "Quality": "High (A)" if ec["variant"] == "a" else "Low (B)",
                "Response length (words)": len(ec["response"].split()),
                "Helpfulness score": jr.get("helpfulness", 3),
            })

        if bias_rows:
            bias_df = pd.DataFrame(bias_rows)
            verb_col1, verb_col2 = st.columns(2)
            with verb_col1:
                all_help = bias_df["Helpfulness score"].tolist()
                all_resp = [ec["response"] for ec in flat_eval_cases if ec["eval_id"] in judge_results]
                verb_rho = compute_verbosity_bias(all_help, all_resp)
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
                    bias_df, x="Response length (words)", y="Helpfulness score",
                    color="Category", symbol="Quality", trendline="ols",
                    title="Response Length vs. Helpfulness Score",
                )
                st.plotly_chart(fig_scatter, use_container_width=True)



# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "BU.330.760 Generative AI · Spring 2026 · Kang Li · "
    "Data: MT-Bench (Zheng et al. 2023) · Judge: Qwen"
)
