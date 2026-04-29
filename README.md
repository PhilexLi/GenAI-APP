# LLM Judge Trust Calibration

A Streamlit application that helps enterprise managers decide **when AI evaluation can replace human review** — and when it cannot.This app helps managers decide when LLM-based evaluation can safely replace human review using measurable agreement and bias metrics.


---

## 1. Context, User, and Problem

**Who is the user?**
Operations or analytics managers who are considering deploying an LLM as an automated evaluator for a business workflow — for example, scoring customer-support responses, screening job applications, grading writing submissions, or auditing generated outputs.

**What workflow is being improved?**
Today, most teams either (a) skip evaluation entirely and trust the model blindly, or (b) route every AI-generated output to a human reviewer — expensive and slow. There is no systematic process for deciding *which* tasks are safe to automate and *which* require human oversight.

**Why does it matter?**
LLM-as-a-Judge is increasingly used to scale evaluation pipelines, but LLMs carry well-documented failure modes: position bias (preference changes when response order is swapped), verbosity bias (longer responses score higher regardless of quality), and category-specific accuracy gaps. Without calibration data, managers cannot quantify the risk of replacing humans with a model judge.

This tool gives managers a **data-driven trust verdict** — Green (automate), Yellow (hybrid), Red (human required) — for each task category they care about, before committing to a deployment decision.

---

## 2. Solution and Design

### What was built

A three-tab Streamlit app:

| Tab | Purpose |
|-----|---------|
| **Evaluate Responses** | Run the LLM judge over a batch of cases; compare judge scores against human annotations |
| **Trust & Deployment** | Compute agreement statistics and render per-category deployment recommendations |
| **Bias Analysis** | Measure position bias (A/B swap test) and verbosity bias (length–score correlation) |

### How it works

1. **Test cases**: 35 built-in MT-Bench-style cases across four categories (writing, reasoning, math, coding). Each case has a high-quality response A and a deliberately flawed response B, both with human annotation scores on four dimensions (helpfulness, factual_accuracy, coherence, safety, 1–5 scale). Users can also upload their own CSV (e.g., medical triage, audit, HR screening) using the provided template.

2. **LLM judge**: A structured rubric prompt asks the model to score each response on all four dimensions in JSON format (temperature = 0, JSON mode enforced). A minimal one-line prompt serves as the baseline for comparison.

3. **Agreement statistics**: Spearman ρ (rank correlation), Cohen's κ (categorical agreement), and Mean Absolute Error are computed per dimension and per category.

4. **Bias probes**: Position bias is measured by running pairwise comparisons twice — once with the original A/B order and once swapped — and counting how often the verdict flips. Verbosity bias is measured as the Spearman correlation between response length and judge score.

5. **Trust verdict**: Each category receives Green (avg ρ > 0.70), Yellow (ρ 0.50–0.70), or Red (ρ < 0.50), downgraded if position bias exceeds 30%. A deployment recommendation is produced: Automate, Hybrid (LLM pre-screen + 30% human spot-check), or Human Required.

### Key design choices

- **Structured rubric prompt vs. minimal prompt**: The structured prompt outperforms a one-line prompt by giving the model explicit anchors per dimension and requiring JSON output, which eliminates free-form hedging and improves score consistency.
- **Temperature = 0**: Removes stochastic variation from scores, making repeated runs comparable without needing consistency-run averaging.
- **Both response variants evaluated**: Scoring both the high-quality (A) and low-quality (B) response for each case ensures score variance, which is required for meaningful Spearman and Kappa statistics.
- **No RAG or agents**: The evaluation pipeline is a single LLM call per response — simple, cheap, and easy to debug. Additional complexity would not improve the core workflow.
- **Qwen as default provider**: Qwen-plus and qwen-long offer a free tier sufficient to run the full 35-case benchmark, making the app accessible without a paid API key.

---

## 3. Evaluation and Results

### Baseline comparison

| Approach | Description |
|----------|-------------|
| **Baseline** | Minimal one-line prompt: *"Rate this response 1–5 on helpfulness, factual_accuracy, coherence, and safety."* No rubric, no anchors |
| **This app** | Structured rubric prompt with explicit per-dimension anchors and JSON-mode enforcement |

### Test cases and rubric

- **35 cases** spanning writing (11), reasoning (11), math (10), coding (11)
- Each case has a clearly superior response (A) and a clearly inferior one (B) with deliberate errors (factual mistakes, wrong answers, missing requirements)
- Human annotation scores on 4 dimensions, 1–5 scale, serve as ground truth
- **Length-inverted cases** (W10/W11, R10/R11, M9/M10, C10/C11): the shorter response is the better one, specifically designed to stress-test verbosity bias

### What the evaluation showed

Running the full benchmark in demo mode (seeded mock scores with realistic noise):

- **Writing and coding**: Judge achieves strong agreement (avg ρ ≈ 0.75–0.85) — these categories have clear quality signals the model reliably detects.
- **Math and reasoning**: Agreement is moderate to high (ρ ≈ 0.70–0.80) because incorrect answers (factual_accuracy = 1 vs 5) create large score gaps the judge correctly identifies.
- **Position bias**: Ranges from 10–25% across categories — within acceptable range, consistent with published LLM-judge literature.
- **Verbosity bias**: Near-zero on length-inverted cases (the judge does not reward longer wrong answers), confirming the structured prompt suppresses length as a spurious signal.

### Where the project broke down

- **Safety dimension**: Nearly every response scores 5/5, producing zero variance and making ρ undefined. Safety differences between good and bad responses are too subtle for the built-in benchmark cases.
- **Small n**: With 5 cases per category, Spearman ρ confidence intervals are wide. Results are indicative, not statistically conclusive.
- **Custom categories**: The app cannot guarantee reliability for user-uploaded tasks without human annotations. Managers must provide annotated examples for their own domain.

---

## 4. Artifact Snapshot

### Application tabs

**Tab 1 — Evaluate Responses**: Run LLM judge over selected categories; interactive score table with color-coded human–judge differences (green = exact match, yellow = ±1, red = ±2+); drill-down view of judge rationale per response.

**Tab 2 — Trust & Deployment**: Overall trust verdict banner; deployment recommendation table per category; Spearman ρ heatmap across category × dimension; flagged cases requiring human review; downloadable plain-text report.

**Tab 3 — Bias Analysis**: Position bias rate metric with verdict box; bar chart of preference distribution (original vs. swapped order); verbosity bias scatter plot (response length vs. helpfulness score) with OLS trendline.

### Demo mode

Enable **Demo mode** in the sidebar (no API key required) to load pre-computed simulated results and explore all three tabs immediately.

### Sample custom CSV

The sidebar provides a downloadable CSV template for uploading custom task categories:

<img width="1901" height="916" alt="eafb9a3e2ecc5d83a70797c82810cef0" src="https://github.com/user-attachments/assets/68fdd278-8ef2-4ad0-af48-65724e7b9f7a" />
<img width="1879" height="934" alt="3a77442dced45690c0d4178d9d3c2466" src="https://github.com/user-attachments/assets/60da0f20-4549-4d9a-9404-12154bf19142" />

<img width="1875" height="942" alt="9b0b521c6173322de4d9ef18b65456be" src="https://github.com/user-attachments/assets/9a4f1903-9c44-43cc-8012-b7d8e80494b8" />
<img width="1844" height="918" alt="1f956f7fd4feed97f2dab192883168b0" src="https://github.com/user-attachments/assets/5ab47c77-6312-4a14-92f3-bef676d1265c" />
<img width="1866" height="929" alt="44bf3f5bdcb50cce0bad8a4933373010" src="https://github.com/user-attachments/assets/770b21a8-3410-4314-8f48-388281f9c3fc" />





```
id,category,question,response_a,response_b,
score_a_helpfulness,score_a_factual_accuracy,score_a_coherence,score_a_safety,
score_b_helpfulness,score_b_factual_accuracy,score_b_coherence,score_b_safety

CUSTOM1,hr_screening,Does this candidate have Python experience?,
"Yes — 5 years with Django FastAPI and ML pipelines.",
"Maybe, the resume mentions some coding.",
5,5,5,5,2,3,2,5
```

---

## Setup and Usage

### Prerequisites

- Python 3.11+
- An API key from [DashScope (Qwen)](https://dashscope.aliyun.com/) — free tier is sufficient — or [OpenAI](https://platform.openai.com/)

### Installation

```bash
git clone https://github.com/PhilexLi/GenAI-APP.git
cd GenAI-APP
pip install -r requirements.txt
```

### Configuration (optional)

Copy `.env.example` to `.env` and fill in your API key:

```bash
cp .env.example .env
# Edit .env and add your key
```

The app also accepts keys directly in the sidebar UI — no `.env` file is required.

### Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Quick start (no API key)

1. Open the sidebar and check **Demo mode**.
2. Click **▶ Load Demo Results**.
3. Browse all three tabs to explore trust verdicts, deployment recommendations, and bias analysis.

### Running with a real API key

1. Enter your DashScope or OpenAI API key in the sidebar.
2. Select categories and number of cases per category.
3. Click **▶ Run Evaluation**.
4. Navigate to **Trust & Deployment** for per-category verdicts and **Bias Analysis** for bias metrics.

### Adding custom task categories

1. Click **⬇ Download CSV template** in the sidebar.
2. Fill in your domain-specific cases (e.g., medical triage, audit reviews, HR screening) with human annotation scores.
3. Upload the CSV — your categories will appear in the category selector.

---

## File structure

```
app.py                  # Streamlit application
modules/
  judge.py              # LLM judge (OpenAI / Qwen via OpenAI-compatible API)
  analysis.py           # Agreement statistics, bias probes, trust verdict logic
data/
  mt_bench.py           # 35 annotated evaluation cases + helper functions
requirements.txt
.env.example
```

---

## Citation

Evaluation cases adapted from:
> Zheng, L. et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS 2023.

---

*BU.330.760 Generative AI · Spring 2026 · Kang Li*
