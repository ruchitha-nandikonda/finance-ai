"""Streamlit UI for the Personal Finance Agent — v3."""
from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

import os
API = os.environ.get("API_URL", "http://localhost:8003")

st.set_page_config(page_title="Personal Finance Agent", layout="wide", initial_sidebar_state="collapsed")

# ── Auth helpers ──────────────────────────────────────────────────────────────
def get_headers() -> dict:
    uid = st.session_state.get("user_id", "")
    return {"x-user-id": uid} if uid else {}

def show_auth():
    import os

    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stToolbar"], [data-testid="stHeader"],
    footer, #MainMenu, header { display: none !important; }
    [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }

    /* Pastel page background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: linear-gradient(145deg, #EEF2FF 0%, #F0F9FF 40%, #FDF4FF 100%) !important;
    }
    [data-testid="stMain"] {
        background: transparent !important;
    }

    .auth-title {
        font-size: 2.8rem; font-weight: 800; letter-spacing: -1px;
        color: #1E293B; margin-bottom: 6px; text-align: center;
    }
    .auth-sub { font-size: 1rem; color: #64748B; margin-bottom: 0; text-align: center; }

    /* All buttons on landing */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
        border: none !important; border-radius: 999px !important;
        color: #fff !important; font-weight: 700 !important; font-size: 16px !important;
        padding: 12px 48px !important;
        box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(59,130,246,0.45) !important;
    }

    [data-baseweb="tab-list"] {
        background: rgba(59,130,246,0.08) !important;
        border: 1px solid rgba(59,130,246,0.15) !important;
        border-radius: 999px !important; padding: 4px !important;
    }
    [data-baseweb="tab"] {
        border-radius: 999px !important; color: #64748B !important;
        font-weight: 600 !important; font-size: 13px !important;
        padding: 6px 20px !important; border: none !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
        color: #fff !important; box-shadow: 0 2px 10px rgba(59,130,246,0.35) !important;
    }
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

    [data-testid="stTextInput"] input {
        background: #fff !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important; color: #1E293B !important; font-size: 14px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important; outline: none !important;
    }
    [data-testid="stTextInput"] input::placeholder { color: #94A3B8 !important; }
    [data-testid="stTextInput"] label { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; color: #475569 !important; }

    [data-testid="stForm"] button[kind="primaryFormSubmit"],
    [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"] {
        background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
        border: none !important; border-radius: 10px !important;
        color: #fff !important; font-weight: 700 !important; font-size: 15px !important;
        box-shadow: 0 4px 18px rgba(59,130,246,0.35) !important;
    }
    [data-testid="stAlert"] { border-radius: 8px !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,0.75) !important;
        border: 1px solid rgba(99,102,241,0.15) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 32px rgba(99,102,241,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    img_path = os.path.join(os.path.dirname(__file__), "assets", "finance_hero.png")

    # ── Landing page ──
    if not st.session_state.get("show_login_form"):

        st.markdown("""
        <style>
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(28px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes floatImg {
            0%, 100% { transform: translateY(0px); }
            50%       { transform: translateY(-10px); }
        }
        @keyframes shimmer {
            0%   { background-position: -400px 0; }
            100% { background-position: 400px 0; }
        }
        @keyframes orbPulse {
            0%, 100% { transform: scale(1); opacity: 0.18; }
            50%       { transform: scale(1.12); opacity: 0.26; }
        }

        .lp-orb1 {
            position:fixed; width:520px; height:520px; border-radius:50%;
            background: radial-gradient(circle, rgba(147,197,253,0.5) 0%, transparent 70%);
            top:-160px; left:-160px; animation: orbPulse 7s ease-in-out infinite;
            pointer-events:none; z-index:0;
        }
        .lp-orb2 {
            position:fixed; width:420px; height:420px; border-radius:50%;
            background: radial-gradient(circle, rgba(196,181,253,0.45) 0%, transparent 70%);
            bottom:-120px; right:-100px; animation: orbPulse 9s ease-in-out infinite reverse;
            pointer-events:none; z-index:0;
        }

        .lp-badge {
            display:inline-flex; align-items:center; gap:6px;
            background: rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.25);
            border-radius:999px; padding:5px 14px; font-size:0.75rem;
            color:#2563EB; font-weight:600; letter-spacing:0.5px;
            animation: fadeUp 0.5s ease both;
        }
        .lp-badge-dot {
            width:7px; height:7px; background:#3B82F6; border-radius:50%;
            box-shadow: 0 0 6px rgba(59,130,246,0.6);
        }

        .lp-headline {
            font-size: clamp(2.2rem, 5vw, 3.4rem);
            font-weight: 900; letter-spacing: -2px; line-height: 1.12;
            background: linear-gradient(135deg, #1E293B 30%, #475569 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeUp 0.6s ease 0.1s both;
        }
        .lp-headline span {
            background: linear-gradient(135deg, #2563EB, #7C3AED);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .lp-desc {
            font-size: 1.05rem; color: #64748B; max-width: 520px;
            margin: 0 auto; line-height: 1.75; text-align: center;
            animation: fadeUp 0.6s ease 0.2s both;
        }

        .lp-img-wrap {
            animation: floatImg 4s ease-in-out infinite, fadeUp 0.7s ease 0.3s both;
        }

        .lp-cards {
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 14px; max-width: 780px; margin: 0 auto;
            animation: fadeUp 0.6s ease 0.4s both;
        }
        .lp-card {
            background: rgba(255,255,255,0.7);
            border: 1px solid rgba(99,102,241,0.12);
            border-radius: 16px; padding: 18px 14px;
            text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 2px 12px rgba(99,102,241,0.07);
            backdrop-filter: blur(8px);
        }
        .lp-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(99,102,241,0.18); }
        .lp-card-icon { font-size: 26px; margin-bottom: 8px; }
        .lp-card-title { font-size: 0.82rem; font-weight: 700; color: #1E293B; margin-bottom: 4px; }
        .lp-card-desc  { font-size: 0.72rem; color: #64748B; line-height: 1.5; }

        .lp-stats {
            display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
            animation: fadeUp 0.6s ease 0.5s both;
        }
        .lp-stat-val { font-size: 1.5rem; font-weight: 800; color: #1E293B; }
        .lp-stat-lbl { font-size: 0.72rem; color: #94A3B8; margin-top: 2px; }

        .lp-divider {
            width: 48px; height: 3px; margin: 0 auto;
            background: linear-gradient(90deg, #3B82F6, #7C3AED);
            border-radius: 999px;
        }
        </style>

        <div class="lp-orb1"></div>
        <div class="lp-orb2"></div>

        <!-- All hero content in one centered block -->
        <div style="width:100%; text-align:center; padding: 24px 0 20px; display:flex; flex-direction:column; align-items:center;">

          <!-- Logo + Name -->
          <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"
               style="margin-bottom:8px; filter:drop-shadow(0 0 18px rgba(59,130,246,0.5));">
            <rect width="64" height="64" rx="16" fill="url(#lgHero)"/>
            <rect x="12" y="38" width="8" height="14" rx="3" fill="white" opacity="0.9"/>
            <rect x="24" y="30" width="8" height="22" rx="3" fill="white" opacity="0.9"/>
            <rect x="36" y="22" width="8" height="30" rx="3" fill="white" opacity="0.9"/>
            <polyline points="14,28 26,18 38,12 52,6" stroke="white" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.8"/>
            <circle cx="52" cy="6" r="3.5" fill="white"/>
            <defs><linearGradient id="lgHero" x1="0" y1="0" x2="64" y2="64">
              <stop stop-color="#2563EB"/><stop offset="1" stop-color="#6366F1"/>
            </linearGradient></defs>
          </svg>
          <div style="font-size:1.5rem; font-weight:800; letter-spacing:-0.5px;
                      background:linear-gradient(135deg,#2563EB,#7C3AED);
                      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                      background-clip:text; margin-bottom:14px;">FinanceAI</div>

          <!-- Headline -->
          <div class="lp-headline" style="margin-bottom:12px;">
            Your Money,<br><span>Finally Under Control</span>
          </div>

          <!-- Description -->
          <p style="font-size:1.02rem; color:#64748B; max-width:500px;
                    margin:0; line-height:1.75; text-align:center;">
            FinanceAI connects to your transactions, understands your habits,
            and gives you a personal AI advisor — so every financial decision
            feels effortless and informed.
          </p>

        </div>
        """, unsafe_allow_html=True)

        # Floating image
        img_col = st.columns([2, 3, 2])[1]
        with img_col:
            if os.path.exists(img_path):
                st.markdown('<div class="lp-img-wrap">', unsafe_allow_html=True)
                st.image(img_path, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="lp-img-wrap" style="text-align:center;padding:10px 0;font-size:80px;">📊</div>
                """, unsafe_allow_html=True)

        # Feature cards + stats
        st.markdown("""
        <div style="padding: 28px 0 12px;">
          <div class="lp-cards">
            <div class="lp-card">
              <div class="lp-card-icon">📈</div>
              <div class="lp-card-title">Spending Analysis</div>
              <div class="lp-card-desc">See exactly where every dollar goes, automatically</div>
            </div>
            <div class="lp-card">
              <div class="lp-card-icon">🎯</div>
              <div class="lp-card-title">Budget Goals</div>
              <div class="lp-card-desc">Set limits and get alerted before you overspend</div>
            </div>
            <div class="lp-card">
              <div class="lp-card-icon">🤖</div>
              <div class="lp-card-title">AI Chat</div>
              <div class="lp-card-desc">Ask anything — "when did I pay my phone bill?"</div>
            </div>
            <div class="lp-card">
              <div class="lp-card-icon">🔮</div>
              <div class="lp-card-title">Forecasting</div>
              <div class="lp-card-desc">Predict next month's spend before it happens</div>
            </div>
          </div>
        </div>

        <div style="padding: 20px 0 6px;">
          <div class="lp-divider"></div>
        </div>

        <div style="padding: 16px 0 4px;">
          <div class="lp-stats">
            <div style="text-align:center;">
              <div class="lp-stat-val">100%</div>
              <div class="lp-stat-lbl">Auto-categorized</div>
            </div>
            <div style="text-align:center;">
              <div class="lp-stat-val">Real-time</div>
              <div class="lp-stat-lbl">Budget alerts</div>
            </div>
            <div style="text-align:center;">
              <div class="lp-stat-val">AI</div>
              <div class="lp-stat-lbl">Powered insights</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Get Started button
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        btn_col = st.columns([1.5, 1, 1.5])[1]
        with btn_col:
            if st.button("Get Started →", use_container_width=True):
                st.session_state.show_login_form = True
                st.rerun()

    # ── Auth form ──
    else:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 20px;">
          <div class="auth-title" style="font-size:2rem; color:#1E293B;">Welcome Back</div>
          <div class="auth-sub" style="color:#64748B;">Sign in or create your account</div>
        </div>
        """, unsafe_allow_html=True)

        _, form_col, _ = st.columns([1, 2, 1])
        with form_col:
            with st.container(border=True):
                tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

                with tab_login:
                    with st.form("login_form"):
                        username = st.text_input("Username", placeholder="Enter your username")
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        submitted = st.form_submit_button("Sign In →", use_container_width=True)
                        if submitted:
                            if not username or not password:
                                st.error("Please fill in all fields.")
                            else:
                                try:
                                    resp = requests.post(f"{API}/auth/login",
                                        json={"username": username, "password": password}, timeout=10)
                                    if resp.status_code == 200:
                                        data = resp.json()
                                        st.session_state.user_id = data["user_id"]
                                        st.session_state.username = data["username"]
                                        st.session_state.logged_in = True
                                        st.session_state.show_login_form = False
                                        st.rerun()
                                    else:
                                        st.error(resp.json().get("detail", "Login failed."))
                                except Exception:
                                    st.error("Cannot reach server. Make sure the API is running.")

                with tab_signup:
                    with st.form("signup_form"):
                        new_user = st.text_input("Username", placeholder="Choose a username")
                        new_email = st.text_input("Email", placeholder="you@example.com")
                        new_pass = st.text_input("Password", type="password", placeholder="At least 6 characters")
                        submitted = st.form_submit_button("Create Account →", use_container_width=True)
                        if submitted:
                            if not new_user or not new_email or not new_pass:
                                st.error("Please fill in all fields.")
                            else:
                                try:
                                    resp = requests.post(f"{API}/auth/signup",
                                        json={"username": new_user, "email": new_email, "password": new_pass}, timeout=10)
                                    if resp.status_code == 200:
                                        data = resp.json()
                                        st.session_state.user_id = data["user_id"]
                                        st.session_state.username = data["username"]
                                        st.session_state.logged_in = True
                                        st.session_state.show_login_form = False
                                        st.rerun()
                                    else:
                                        st.error(resp.json().get("detail", "Signup failed."))
                                except Exception:
                                    st.error("Cannot reach server. Make sure the API is running.")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        back_col = st.columns([1, 1, 1])[1]
        with back_col:
            if st.button("← Back", use_container_width=True):
                st.session_state.show_login_form = False
                st.rerun()


if not st.session_state.get("logged_in"):
    show_auth()
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.get('username', 'User')}**")
    if st.button("Logout", use_container_width=True):
        for key in ["logged_in", "user_id", "username", "messages"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.markdown("---")
    st.caption("Quick Add Transaction")
    with st.form("manual_add"):
        m_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
        m_desc = st.text_input("Description")
        m_cat = st.selectbox("Category", ["other", "food", "transport", "entertainment", "bills", "shopping", "health"])
        if st.form_submit_button("Add"):
            try:
                resp = requests.post(f"{API}/transactions/add",
                    params={"amount": m_amount, "description": m_desc, "category": m_cat},
                    headers=get_headers(), timeout=15)
                resp.raise_for_status()
                st.success(f"Added: {resp.json()['category']}")
            except Exception as e:
                st.error(str(e))
    st.markdown("---")
    if st.button("🗑️ Clear Memory"):
        requests.delete(f"{API}/memory", headers=get_headers())
        st.session_state.messages = []
        st.success("Memory cleared.")

st.title("💰 Personal Finance Agent")

tabs = st.tabs(["🏠 Dashboard", "💬 Chat", "📊 Transactions", "📈 Trends", "💰 Budgets & Goals", "🔁 Recurring", "📅 Weekly Insights"])
tab_dash, tab_chat, tab_txns, tab_trends, tab_budget, tab_recurring, tab_insights = tabs

# ── Dashboard ─────────────────────────────────────────────────────────────────
with tab_dash:
    st.subheader("Overview")
    try:
        summary = requests.get(f"{API}/transactions", params={"days": 30}, headers=get_headers(), timeout=10).json()
        budget_status = requests.get(f"{API}/budgets/status", headers=get_headers(), timeout=10).json()
        goals = requests.get(f"{API}/savings", headers=get_headers(), timeout=10).json()
        forecast = requests.get(f"{API}/analytics/forecast", headers=get_headers(), timeout=10).json()

        txns = summary if isinstance(summary, list) else []
        total = sum(t["amount"] for t in txns)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Spent This Month", f"${total:,.2f}")
        col2.metric("Transactions", len(txns))
        col3.metric("Next Month Forecast", f"${forecast.get('next_month_total', 0):,.2f}")
        col4.metric("Savings Goals", len(goals))

        # Budget alerts
        alerts = [s for s in budget_status if s["status"] in ("warning", "over")]
        if alerts:
            st.markdown("### ⚠️ Budget Alerts")
            for a in alerts:
                color = "🔴" if a["status"] == "over" else "🟡"
                st.warning(f"{color} **{a['category'].title()}**: ${a['spent']:.2f} / ${a['monthly_limit']:.2f} ({a['percentage']:.0f}%)")

        # Spending by category chart
        if txns:
            st.markdown("### Spending by Category (Last 30 Days)")
            by_cat: dict[str, float] = {}
            for t in txns:
                by_cat[t["category"]] = by_cat.get(t["category"], 0) + t["amount"]
            df = pd.DataFrame(list(by_cat.items()), columns=["Category", "Amount"]).sort_values("Amount", ascending=False)
            st.bar_chart(df.set_index("Category"))

        # Savings goals progress
        if goals:
            st.markdown("### Savings Goals")
            for g in goals:
                pct = min(g["percentage"], 100)
                st.write(f"**{g['name']}** — ${g['current_amount']:,.2f} / ${g['target_amount']:,.2f}")
                st.progress(pct / 100)

    except Exception as e:
        st.error(f"Dashboard error: {e}")

# ── Chat ──────────────────────────────────────────────────────────────────────
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Ask about your finances..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(f"{API}/chat", json={"message": user_input}, headers=get_headers(), timeout=30)
                    data = resp.json()
                    reply = data.get("reply", "No response.")
                    context = data.get("memory_context")
                except Exception as e:
                    reply = f"Error: {e}"
                    context = None
            st.write(reply)
            if context:
                with st.expander("🧠 Memory used"):
                    for item in context:
                        st.write(f"- {item}")
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Transactions ──────────────────────────────────────────────────────────────
with tab_txns:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Import Bank CSV")
        uploaded = st.file_uploader("Upload your bank CSV", type="csv")
        if uploaded and st.button("Import & Auto-Categorize"):
            with st.spinner("Detecting format, importing, categorizing..."):
                try:
                    resp = requests.post(f"{API}/sync",
                        files={"file": ("transactions.csv", uploaded.getvalue(), "text/csv")}, headers=get_headers(), timeout=120)
                    st.success(resp.json().get("message", "Done."))
                except Exception as e:
                    st.error(str(e))

        st.subheader("Scan a Receipt")
        receipt = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])
        if receipt and st.button("Scan Receipt"):
            with st.spinner("Reading receipt with GPT Vision..."):
                try:
                    resp = requests.post(f"{API}/transactions/scan-receipt",
                        files={"file": (receipt.name, receipt.getvalue(), receipt.type)}, headers=get_headers(), timeout=30)
                    data = resp.json()
                    st.success(f"Detected: **{data['description']}** — ${data['amount']:.2f} ({data['category']}) on {data['date']}")
                    if st.button("Add this transaction"):
                        requests.post(f"{API}/transactions/add",
                            params={"amount": data["amount"], "description": data["description"], "category": data["category"]}, headers=get_headers())
                        st.success("Added!")
                except Exception as e:
                    st.error(str(e))

    with col_right:
        st.subheader("Filter & Browse")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            date_from = st.date_input("From", value=None)
            date_to = st.date_input("To", value=None)
        with f_col2:
            cat_filter = st.selectbox("Category", ["all", "food", "transport", "entertainment", "bills", "shopping", "health", "other"])
            min_amt = st.number_input("Min Amount ($)", min_value=0.0, value=0.0)

    if st.button("Load Transactions"):
        params: dict = {}
        if date_from:
            params["date_from"] = str(date_from)
        if date_to:
            params["date_to"] = str(date_to)
        if cat_filter != "all":
            params["category"] = cat_filter
        if min_amt > 0:
            params["min_amount"] = min_amt
        try:
            txns = requests.get(f"{API}/transactions", params=params, headers=get_headers(), timeout=10).json()
            if txns:
                df = pd.DataFrame(txns)
                st.metric("Total", f"${df['amount'].sum():,.2f}", f"{len(df)} transactions")

                # Show with delete buttons
                for _, row in df.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([2, 3, 1, 1, 1])
                    c1.write(str(row["date"]))
                    c2.write(row["description"])
                    c3.write(row["category"])
                    c4.write(f"${row['amount']:.2f}")
                    if c5.button("🗑️", key=f"del_{row['id']}"):
                        requests.delete(f"{API}/transactions/{row['id']}", headers=get_headers())
                        st.rerun()
            else:
                st.info("No transactions found.")
        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    if st.button("⬇️ Export to CSV"):
        try:
            params = {}
            if cat_filter != "all":
                params["category"] = cat_filter
            resp = requests.get(f"{API}/transactions/export", params=params, headers=get_headers(), timeout=10)
            st.download_button("Download CSV", resp.content, "transactions.csv", "text/csv")
        except Exception as e:
            st.error(str(e))

# ── Trends ────────────────────────────────────────────────────────────────────
with tab_trends:
    st.subheader("Monthly Spending Trends")
    try:
        trends = requests.get(f"{API}/analytics/trends", headers=get_headers(), timeout=10).json()
        if trends:
            df = pd.DataFrame(trends)
            st.markdown("### Total Spending by Month")
            st.bar_chart(df.set_index("period")["total"])

            st.markdown("### Category Breakdown Over Time")
            cat_data = {}
            for row in trends:
                for cat, amt in row["by_category"].items():
                    if cat not in cat_data:
                        cat_data[cat] = {}
                    cat_data[cat][row["period"]] = amt
            if cat_data:
                cat_df = pd.DataFrame(cat_data).fillna(0)
                st.line_chart(cat_df)

            st.markdown("### Forecast for Next Month")
            forecast = requests.get(f"{API}/analytics/forecast", headers=get_headers(), timeout=10).json()
            col1, col2 = st.columns(2)
            col1.metric("Predicted Total", f"${forecast['next_month_total']:,.2f}")
            col2.write(f"*{forecast['basis']}*")
            if forecast["by_category"]:
                fdf = pd.DataFrame(list(forecast["by_category"].items()), columns=["Category", "Estimated"])
                st.dataframe(fdf.sort_values("Estimated", ascending=False), use_container_width=True)
        else:
            st.info("No transaction history yet. Import some transactions to see trends.")
    except Exception as e:
        st.error(str(e))

# ── Budgets & Goals ───────────────────────────────────────────────────────────
with tab_budget:
    col_b, col_g = st.columns(2)

    with col_b:
        st.subheader("Monthly Budgets")
        with st.form("set_budget"):
            b_cat = st.selectbox("Category", ["food", "transport", "entertainment", "bills", "shopping", "health", "other"])
            b_limit = st.number_input("Monthly Limit ($)", min_value=1.0, step=10.0)
            if st.form_submit_button("Set Budget"):
                try:
                    requests.post(f"{API}/budgets", params={"category": b_cat, "monthly_limit": b_limit}, headers=get_headers())
                    st.success(f"Budget set: {b_cat} → ${b_limit:.2f}/month")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        try:
            statuses = requests.get(f"{API}/budgets/status", headers=get_headers(), timeout=10).json()
            for s in statuses:
                icon = "🔴" if s["status"] == "over" else "🟡" if s["status"] == "warning" else "🟢"
                st.markdown(f"{icon} **{s['category'].title()}**")
                st.progress(min(s["percentage"] / 100, 1.0))
                c1, c2, c3 = st.columns(3)
                c1.metric("Spent", f"${s['spent']:.2f}")
                c2.metric("Budget", f"${s['monthly_limit']:.2f}")
                c3.metric("Remaining", f"${s['remaining']:.2f}")
                if st.button(f"Remove budget", key=f"delbud_{s['category']}"):
                    requests.delete(f"{API}/budgets/{s['category']}", headers=get_headers())
                    st.rerun()
                st.markdown("---")
        except Exception as e:
            st.error(str(e))

    with col_g:
        st.subheader("Savings Goals")
        with st.form("add_goal"):
            g_name = st.text_input("Goal name (e.g. Vacation)")
            g_target = st.number_input("Target Amount ($)", min_value=1.0, step=50.0)
            g_current = st.number_input("Already Saved ($)", min_value=0.0, step=10.0)
            g_deadline = st.date_input("Deadline (optional)", value=None)
            if st.form_submit_button("Add Goal"):
                try:
                    requests.post(f"{API}/savings", json={
                        "name": g_name, "target_amount": g_target,
                        "current_amount": g_current,
                        "deadline": str(g_deadline) if g_deadline else None,
                    }, headers=get_headers())
                    st.success(f"Goal added: {g_name}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        try:
            goals = requests.get(f"{API}/savings", headers=get_headers(), timeout=10).json()
            for g in goals:
                pct = min(g["percentage"], 100)
                st.markdown(f"**{g['name']}**" + (f" — due {g['deadline']}" if g.get('deadline') else ""))
                st.progress(pct / 100)
                c1, c2 = st.columns(2)
                c1.metric("Saved", f"${g['current_amount']:,.2f}")
                c2.metric("Target", f"${g['target_amount']:,.2f}")
                new_amt = st.number_input("Update saved amount", value=float(g["current_amount"]), key=f"upd_{g['id']}")
                col_upd, col_del = st.columns(2)
                if col_upd.button("Update", key=f"save_{g['id']}"):
                    requests.patch(f"{API}/savings/{g['id']}", json={"current_amount": new_amt}, headers=get_headers())
                    st.rerun()
                if col_del.button("Delete", key=f"delgoal_{g['id']}"):
                    requests.delete(f"{API}/savings/{g['id']}", headers=get_headers())
                    st.rerun()
                st.markdown("---")
        except Exception as e:
            st.error(str(e))

# ── Recurring ─────────────────────────────────────────────────────────────────
with tab_recurring:
    st.subheader("Recurring Transactions")
    st.caption("Automatically detected subscriptions and bills based on your transaction history.")
    if st.button("Detect Recurring"):
        with st.spinner("Analyzing patterns..."):
            try:
                data = requests.get(f"{API}/analytics/recurring", headers=get_headers(), timeout=15).json()
                if data:
                    df = pd.DataFrame(data)
                    df["likely_monthly"] = df["likely_monthly"].map({True: "✅ Yes", False: "Maybe"})
                    df.columns = ["Description", "Avg Amount", "Occurrences", "Category", "Likely Monthly"]
                    st.dataframe(df, use_container_width=True)
                    total_recurring = sum(r["average_amount"] for r in data if r["likely_monthly"] is True or r["likely_monthly"] == "✅ Yes")
                    st.metric("Estimated Monthly Recurring Cost", f"${sum(r['average_amount'] for r in data):,.2f}")
                else:
                    st.info("No recurring transactions detected yet. Import more history for better detection.")
            except Exception as e:
                st.error(str(e))

# ── Weekly Insights ───────────────────────────────────────────────────────────
with tab_insights:
    st.subheader("Weekly Spending Insights")
    st.caption("AI-generated summary of your last 7 days.")
    if st.button("Generate Insight"):
        with st.spinner("Analyzing your week..."):
            try:
                data = requests.get(f"{API}/insights/weekly", headers=get_headers(), timeout=30).json()
                st.markdown(f"**Period:** {data['period']}")
                st.metric("Total Spent This Week", f"${data['total_spent']:,.2f}")
                st.markdown("### Summary")
                st.write(data["summary"])
                if data["top_categories"]:
                    st.markdown("### Top Categories")
                    df = pd.DataFrame(data["top_categories"])
                    st.bar_chart(df.set_index("category")["amount"])
            except Exception as e:
                st.error(str(e))
