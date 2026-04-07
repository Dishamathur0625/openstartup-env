# 🚀 OpenStartupEnv

## AI Startup Pivot Decision Simulator

---

## 🧠 Overview

**OpenStartupEnv** is a real-world **startup strategy simulation environment** designed to evaluate AI agents on business decision-making.

In this environment, the agent acts like a **startup founder** and makes sequential decisions such as:

* improving product
* increasing marketing
* reducing costs
* pivoting the business model
* raising funding
* shutting down

The goal is to **maximize startup success under realistic constraints** like burn rate, competition, and product-market fit.

---

## 🎯 Objective

The environment evaluates how effectively an AI agent can:

* grow users and revenue
* maintain healthy cash flow
* improve product-market fit (PMF)
* adapt to market conditions
* make strategic decisions (including pivoting)

---

## 💡 Why This Project?

Most AI environments focus on games or static tasks.

**OpenStartupEnv introduces:**

* real-world business dynamics
* delayed consequences of decisions
* trade-offs between growth and survival
* adaptive strategy across difficulty levels

---

## 📊 Environment Design

### 🔍 Observation Space

At each step, the agent receives:

* `month`
* `startup_type`
* `users`
* `revenue`
* `burn_rate`
* `cash_left`
* `market_trend`
* `competition_level`
* `product_quality`
* `marketing_strength`
* `pmf_score`
* `last_action`
* `goal`

---

### 🎮 Action Space

The agent must choose one action:

* `improve_product`
* `increase_marketing`
* `reduce_costs`
* `pivot_business_model`
* `raise_funding`
* `shutdown`

---

### 🏆 Reward Design

Rewards are shaped across the full trajectory.

**Positive signals:**

* user growth
* revenue growth
* PMF improvement
* reduced burn rate
* staying financially alive

**Negative signals:**

* poor strategic decisions
* declining metrics
* bankruptcy

---

## 🧪 Tasks

### 1. `easy_stable_growth`

* Goal: Grow sustainably
* Market: stable
* Competition: medium

---

### 2. `medium_competition_pressure`

* Goal: Survive high competition
* Requires careful burn management

---

### 3. `hard_pivot_or_die`

* Goal: Identify poor PMF and pivot early
* Market: declining
* Competition: high

---

## 📈 Scoring

Each task is scored:

```text
0.0 → worst performance
1.0 → best performance
```

Evaluation considers:

* survival
* revenue growth
* user growth
* PMF improvement
* strategic decisions (e.g., pivoting)

---

## 🏗️ Project Structure

```text
openstartup-env/
├── server/
│   ├── __init__.py
│   └── app.py
├── envs/
│   ├── __init__.py
│   ├── models.py
│   ├── simulator.py
│   ├── startup_env.py
│   └── tasks.py
├── graders/
│   ├── __init__.py
│   └── startup_graders.py
├── inference.py
├── openenv.yaml
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── README.md
├── uv.lock
```

---

## ⚙️ Installation

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the API

```bash
python -m uvicorn server.app:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

* `POST /reset` → Reset environment
* `POST /step` → Apply action
* `GET /state` → Current internal state
* `GET /tasks` → Available tasks

---

## 📌 Example API Usage

### Reset environment

```bash
POST /reset?task_name=easy_stable_growth
```

### Take a step

```json
POST /step
{
  "action": "improve_product"
}
```

---

## 🤖 Running Inference

Start server first:

```bash
python -m uvicorn server.app:app --reload
```

Then run:

```bash
python inference.py
```

Expected logs:

```
[START]
[STEP]
[END]
```

---

## 🐳 Docker

### Build image

```bash
docker build -t openstartup-env .
```

### Run container

```bash
docker run -p 7860:7860 openstartup-env
```

If port 7860 is busy:

```bash
docker run -p 7861:7860 openstartup-env
```

Open:

```
http://127.0.0.1:7861/docs
```

---

## ✅ OpenEnv Validation

Run:

```bash
openenv validate
```

Expected output:

```
[OK] openstartup-env: Ready for multi-mode deployment
```

---

## 🚀 Deployment

Deploy to **Hugging Face Spaces (Docker)** or any cloud platform.

After deployment:

* open `/docs`
* test `/tasks`
* test `/reset`
* test `/step`

---

## ⚠️ Disclaimer

This is a **simulation environment** for evaluating AI agents.
It does not provide real financial or startup advice.

---

## 🏁 Final Note

OpenStartupEnv is a **reinforcement-learning style environment** where AI learns to make startup decisions under uncertainty and real-world constraints.

---

