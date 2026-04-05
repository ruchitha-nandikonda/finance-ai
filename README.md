# FinanceAI - AI-Powered Personal Finance Agent

A full-stack personal finance application that uses AI to help you track spending, manage budgets, and get intelligent insights about your financial habits.

**Live Demo:** [https://financeai-app.streamlit.app/](https://financeai-app.streamlit.app/)

---

## Tech Stack

### Backend
- **FastAPI** — RESTful API framework
- **OpenAI GPT** — Conversational AI agent for natural language finance queries
- **LangChain** — LLM orchestration and tool routing
- **SQLite** — Lightweight database for transactions, budgets, and user data
- **Python 3.11**

### Frontend
- **Streamlit** — Interactive web UI with custom CSS/HTML
- **Pandas** — Data manipulation and visualization

### AI & Intelligence
- **Conversational Agent** — Ask questions like "How much did I spend on food last week?" or "When did I pay my phone bill?"
- **Auto-Categorization** — GPT-powered transaction categorization
- **Receipt Scanning** — Upload receipt images, GPT Vision extracts details
- **Spending Forecasting** — Predicts next month's spending based on historical patterns
- **Weekly Insights** — AI-generated summaries of your spending habits

### Infrastructure
- **Render** — Backend API hosting
- **Streamlit Cloud** — Frontend hosting
- **Docker** — Containerized deployment support
- **GitHub Actions** — CI/CD ready

---

## Features

- **User Authentication** — Signup/login with hashed passwords
- **Transaction Management** — Import bank CSVs, add manually, scan receipts
- **Smart Budgets** — Set category limits, get alerts when overspending
- **Savings Goals** — Track progress toward financial targets with deadlines
- **Recurring Detection** — Auto-detect subscriptions and recurring bills
- **AI Chat** — Natural language queries about your finances with memory context
- **Spending Trends** — Monthly charts, category breakdowns, forecasting
- **Memory System** — Short-term (conversation) + long-term (facts/goals) memory

---

## Architecture

```
├── app/
│   ├── agents/          # AI agent with tool routing
│   ├── core/            # Config, prompts
│   ├── memory/          # Short-term + long-term memory
│   ├── models/          # Pydantic schemas
│   ├── routers/         # API endpoints (auth, chat, transactions, etc.)
│   ├── services/        # Business logic (categorizer, forecaster, etc.)
│   ├── tools/           # Agent tools (spending, budget, insight)
│   └── main.py          # FastAPI app entry point
├── frontend/
│   ├── assets/          # Images
│   └── streamlit_app.py # Streamlit UI
├── tests/               # Unit tests
├── Dockerfile
├── docker-compose.yml
└── render.yaml          # Render deployment config
```

---

## Run Locally

```bash
# Clone
git clone https://github.com/ruchitha-nandikonda/finance-ai.git
cd finance-ai

# Setup environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --port 8003

# Start frontend (in another terminal)
streamlit run frontend/streamlit_app.py
```

### Docker

```bash
docker-compose up --build
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `CHAT_MODEL` | GPT model (default: `gpt-3.5-turbo`) | No |
| `DB_PATH` | SQLite database path | No |
| `API_URL` | Backend URL (for Streamlit frontend) | For deployment |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Login |
| POST | `/chat` | Chat with AI agent |
| GET | `/transactions` | List transactions |
| POST | `/sync` | Import CSV |
| GET | `/budgets/status` | Budget status |
| GET | `/savings` | Savings goals |
| GET | `/analytics/trends` | Spending trends |
| GET | `/analytics/forecast` | Next month forecast |
| GET | `/analytics/recurring` | Recurring transactions |
| GET | `/insights/weekly` | AI weekly summary |
| GET | `/health` | Health check |
