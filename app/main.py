from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.finance_agent import FinanceAgent
from app.core.config import get_settings
from app.memory.long_term import JsonLongTermMemory
from app.memory.memory_manager import MemoryManager
from app.memory.short_term import ShortTermMemory
from app.models.schemas import HealthResponse
from app.routers import analytics, auth, budgets, chat, insights, savings, transactions
from app.services.alert_service import AlertService
from app.services.auth_service import AuthService
from app.services.budget_service import BudgetService
from app.services.categorizer import CategorizationService
from app.services.csv_importer import CsvImporter
from app.services.forecaster import Forecaster
from app.services.receipt_scanner import ReceiptScanner
from app.services.recurring_detector import RecurringDetector
from app.services.savings_service import SavingsService
from app.tools.budget_tool import BudgetTool
from app.tools.insight_tool import InsightTool
from app.tools.spending_tool import SpendingTool


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Core services
    csv_importer = CsvImporter(db_path=settings.db_path)
    categorizer = CategorizationService(config=settings)

    # Memory
    short_term = ShortTermMemory()
    long_term = JsonLongTermMemory()
    memory_manager = MemoryManager(short_term=short_term, long_term=long_term)

    # Agent tools
    spending_tool = SpendingTool(transaction_source=csv_importer)
    budget_tool = BudgetTool(memory_manager=memory_manager, transaction_source=csv_importer)
    insight_tool = InsightTool(config=settings, transaction_source=csv_importer, memory_manager=memory_manager)

    # Agent
    agent = FinanceAgent(
        memory_manager=memory_manager,
        spending_tool=spending_tool,
        budget_tool=budget_tool,
        insight_tool=insight_tool,
        config=settings,
    )

    # New services
    auth_service = AuthService(db_path=settings.db_path)
    budget_service = BudgetService(db_path=settings.db_path)
    savings_service = SavingsService(db_path=settings.db_path)
    alert_service = AlertService(config=settings)
    recurring_detector = RecurringDetector(db_path=settings.db_path)
    forecaster = Forecaster(db_path=settings.db_path)
    receipt_scanner = ReceiptScanner(config=settings)

    # Attach to app state
    app.state.agent = agent
    app.state.auth_service = auth_service
    app.state.csv_importer = csv_importer
    app.state.categorizer = categorizer
    app.state.budget_service = budget_service
    app.state.savings_service = savings_service
    app.state.alert_service = alert_service
    app.state.recurring_detector = recurring_detector
    app.state.forecaster = forecaster
    app.state.receipt_scanner = receipt_scanner

    print(f"✓ Finance Agent ready | model: {settings.chat_model} | db: {settings.db_path}")
    yield


app = FastAPI(title="Personal Finance Agent", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(transactions.router)
app.include_router(insights.router)
app.include_router(budgets.router)
app.include_router(savings.router)
app.include_router(analytics.router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
