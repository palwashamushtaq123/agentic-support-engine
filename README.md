
# 🤖 LangGraph Customer Support & Refund Agent — CSV Edition

An autonomous, stateful customer support and dispute resolution engine built using **Groq + LangGraph + FastAPI**, utilizing CSV storage (`data/orders.csv` and `data/refunds.csv`) for a demo refund ledger without relying on SQLite.

---

## 📁 Project Directory Structure

```text
langgraph-refund-agent/
│
├── Assets/
│   ├── outcome (1).png
│   ├── outcome (2).png
│   ├── outcome (3).png
│   ├── outcome (4).png
│   └── Refund file update.png
│
├── data/
│   ├── orders.csv          # Store demo order inventory & status
│   └── refunds.csv         # Audit trail for processed refunds
│
├── agents.py               # LLM initialization, intent classification, and reply generation
├── database.py             # CSV reading, locking, seeding, and ledger updates
├── graph.py                # LangGraph workflow definition, nodes, and conditional edges
├── index.html              # Frontend chat interface & admin review dashboard
├── main.py                 # FastAPI application endpoints and HITL resume logic
├── schemas.py              # Pydantic models for data validation and structured output
├── tools.py                # LangChain tool definitions for order lookup & refund processing
├── requirements.txt        # Python package dependencies
├── .env                    # Environment variables (Groq API Key)
├── .env.example            # Sample environment configuration template
└── .gitignore              # Git ignore rules
```

### 🖼️ Application Previews & Outcomes

Here is a visual preview of the autonomous workflows, decision logs, and ledger updates:

- Automated Support & Chat UI
- Human-in-the-Loop Review Portal

- Graph State & Telemetry
- Refund Ledger Update
### 🚀 Quick Start (Windows PowerShell)

Follow these commands to set up and run the project locally using PowerShell:

- py -3.11 -m venv venv

- .\venv\Scripts\Activate.ps1

- pip install -r requirements.txt

- Copy-Item .env.example .env



1. Edit the .env file and set your GROQ_API_KEY.

2. Start the FastAPI server:

uvicorn main:app --reload

3. Open your browser and navigate to http://127.0.0.1:8000 (or explore the API docs at http://127.0.0.1:8000/docs).

### 🎯 Usage Examples & Scenarios

Use a unique thread_id per request to test different agent behaviors:

`Auto-Approved Refund ($75):

    POST /support with:
    JSON

    {"thread_id": "demo-1", "message": "Please refund ORD-1001"}

Human-in-the-Loop Review ($120):

    POST /support with:
    JSON

    {"thread_id": "demo-2", "message": "Please refund ORD-1002"}

    Note: ORD-1002 costs $120 and triggers human approval. Resume the graph by POSTing to /review/demo-2:
    JSON

    {"approved": true}

Other Test Scenarios:

    ORD-1003: $350 (triggers human review)

    ORD-1004: Expired refund window (> 7 days)

    ORD-1005: Already refunded order
### 📊 Data Files & Initialization

    On the first server startup, the project automatically provisions 20 demo orders in data/orders.csv and initializes an empty data/refunds.csv audit ledger.

    Subsequent startups preserve edits and refunds.

    To Reset Data: Stop the server, delete the two CSV files inside the data/ folder, and restart the application.

### ⚠️ Important Limitations

    Checkpoints: LangGraph uses InMemorySaver for state checkpoints; pending approvals will be lost on server restart (though CSV data remains intact).

    Concurrency: CSV writes are protected by a Python thread lock only within a single process. Run a single server worker and avoid editing CSV files manually while the server is running.

    Non-Transactional Storage: CSV storage is educational and non-transactional across multiple files. A crash between writing the refund ledger and updating the order status may lead to inconsistent records, although the refund history protects against duplicate payouts.

    Simulated Payments: The demo only records local refunds; no real financial transactions are executed.

    Authentication: The review endpoint currently lacks authentication; secure it before any production deployment.

### 🛠️ Tech Stack & Architecture

    Backend & API: Python, FastAPI, Uvicorn, Pydantic

    Agentic Framework: LangGraph (MemorySaver, Command, interrupt), LangChain

    LLM Integration: Groq API (ChatGroq)

    Frontend UI: Tailwind CSS, HTML5, Vanilla JavaScript

    Database: Structured CSV flat files with thread-safe locking

### 👤 Author

    Palwasha Mushtaq