ShotOps

AI Production Operations Director

«Your production has a problem. ShotOps finds out why.»

ShotOps is an agentic production operations platform for film and television teams. It uses Google Gemini + Google Agent Development Kit (ADK) to investigate production problems, correlate operational evidence, and produce actionable recommendations.

ShotOps is designed around a simple idea:

Production teams shouldn't have to manually investigate dozens of dashboards, logs, analytics systems, and external signals to understand why a production is falling behind.

They should be able to ask.

«"Why are we behind schedule?"»

ShotOps investigates.

---

🎬 What ShotOps Does

ShotOps acts as an AI production operations director.

A producer, VFX supervisor, production manager, or studio operator can submit a natural-language production question.

For example:

«"What's putting Shadow Protocol at risk?"»

The ShotOps agent can investigate available production intelligence, correlate evidence, identify potential root causes, and recommend an operational response.

The investigation workflow is designed around:

Production Problem
       ↓
Understand Request
       ↓
Build Investigation Plan
       ↓
Inspect Production Telemetry
       ↓
Analyze Historical Data
       ↓
Research External Intelligence
       ↓
Correlate Evidence
       ↓
Identify Root Cause
       ↓
Assess Production Impact
       ↓
Generate Recommendation

---

🧠 Agent Architecture

ShotOps separates the user interface, agent reasoning, and external intelligence systems.

┌──────────────────────────────────────────────┐
│                 SHOTOPS UI                   │
│                                              │
│ Overview · Production · Investigations      │
│ Intelligence · Incidents · Reports          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│       GOOGLE AGENT DEVELOPMENT KIT           │
│                  (ADK)                       │
│                                              │
│              ShotOps Agent                   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                  GOOGLE GEMINI
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Grafana      ClickHouse    Parallel
        MCP
          │            │            │
          ▼            ▼            ▼
       Current      Historical    External
       telemetry    analytics     intelligence
          │            │            │
          └────────────┼────────────┘
                       ▼
                Evidence Fusion
                       │
                       ▼
              Root Cause Analysis
                       │
                       ▼
                Recommendation

Partner responsibilities

System| Role
Google Gemini| Reasoning and synthesis
Google ADK| Agent orchestration and execution
Grafana| Production observability
ClickHouse| Historical production analytics
Parallel| External intelligence and research
ShotOps| Production operations interface

The systems have intentionally different responsibilities.

Grafana answers:

«What's happening right now?»

ClickHouse answers:

«What normally happens, and how does this compare historically?»

Parallel answers:

«What external information could explain or affect this situation?»

Gemini answers:

«What does all of this evidence mean?»

---

🔎 Example Investigation

User

«Why are we behind schedule?»

ShotOps investigates

The agent may discover:

Grafana
GPU utilization: 94%
Render queue: 42 jobs
Worker saturation: Critical

Historical analytics:

ClickHouse
Current render time: 11.3 min
Historical baseline: 4.2 min
Deviation: 2.7×

External intelligence:

Parallel
Recent VFX asset ingestion spike
Multiple unoptimized submissions detected

ShotOps conclusion

ROOT CAUSE

GPU render-worker saturation is creating a cascading
delay across the VFX delivery pipeline.

CONFIDENCE

94%

IMPACT

High production schedule risk.

RECOMMENDATION

Redistribute non-critical rendering workloads and
increase temporary GPU capacity.

The agent must distinguish observed evidence from inference and should not invent telemetry.

---

🖥️ Product Interface

ShotOps uses a production-operations dashboard rather than a traditional chatbot interface.

Main navigation

- Overview
- Production
- Investigations
- Intelligence
- Incidents
- Agent Activity
- Reports
- Settings

Investigation experience

The investigation interface exposes the agent's operational activity:

SHOTOPS IS INVESTIGATING

Understanding request          ✓
Building investigation plan    ✓
Querying production telemetry  ●
Comparing historical data      ○
Searching external intelligence ○
Correlating evidence           ○

Users can see what the agent is doing instead of receiving an opaque "AI is thinking..." message.

---

🤖 Agent Activity

ShotOps treats agent execution as an observable production system.

Agent activity can include:

Agent Run
   │
   ├── Planning
   ├── Tool Invocation
   ├── Tool Response
   ├── Reasoning
   ├── Evidence Collection
   ├── Correlation
   └── Recommendation

This creates an important feedback loop:

«The system uses observability to investigate production problems while also making the agent itself observable.»

---

⚙️ Technology Stack

Frontend

- Next.js
- TypeScript
- Tailwind CSS

Agent

- Python
- Google Agent Development Kit (ADK)
- Google Gemini

Production Intelligence

- Grafana / Grafana MCP
- ClickHouse
- Parallel

Backend

- FastAPI
- Server-Sent Events (SSE)

Development

- GitHub
- Google Stitch
- DeepSeek

---

📁 Project Structure

shotops/
│
├── app/
│   ├── overview/
│   ├── production/
│   ├── investigations/
│   ├── intelligence/
│   ├── incidents/
│   ├── agent-activity/
│   ├── reports/
│   ├── settings/
│   └── layout.tsx
│
├── components/
│   ├── layout/
│   ├── navigation/
│   ├── production/
│   ├── investigations/
│   ├── incidents/
│   ├── intelligence/
│   ├── agent/
│   ├── reports/
│   └── ui/
│
├── lib/
│   ├── api/
│   ├── demo/
│   ├── types/
│   ├── utils/
│   └── constants/
│
├── agent/
│   └── backend/
│       ├── app/
│       │   ├── agent.py
│       │   ├── config.py
│       │   ├── events.py
│       │   ├── runner.py
│       │   ├── schemas.py
│       │   ├── server.py
│       │   └── tools.py
│       │
│       ├── tests/
│       ├── requirements.txt
│       └── pyproject.toml
│
├── integrations/
│   ├── grafana/
│   ├── clickhouse/
│   └── parallel/
│
├── public/
├── tests/
├── .env.example
├── DESIGN.md
├── LICENSE
├── README.md
└── package.json

---

🚀 Local Development

Prerequisites

- Node.js 20+
- Python 3.11+
- Git
- Google Gemini API access

The agent backend can be developed locally without deploying to Google Cloud.

---

Frontend

Install dependencies:

npm install

Run the development server:

npm run dev

The frontend will be available at:

http://localhost:3000

---

🤖 Agent Backend

Navigate to:

cd agent/backend

Create a virtual environment:

python -m venv .venv

Activate it.

Linux/macOS

source .venv/bin/activate

Windows

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

---

Environment Variables

Create:

agent/backend/.env

Example:

GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=your_supported_gemini_model

Never commit API keys or other secrets to the repository.

---

Run the Agent API

From:

agent/backend

run:

uvicorn app.server:app --reload --port 8000

The API will be available at:

http://localhost:8000

---

🔌 Investigation API

Create an investigation

POST /investigations

Example request:

{
  "query": "Why are we behind schedule?"
}

Example response:

{
  "investigationId": "example-id",
  "status": "running"
}

---

Get investigation status

GET /investigations/{investigationId}

---

Stream investigation events

GET /investigations/{investigationId}/events

The endpoint uses Server-Sent Events to stream agent activity to the frontend.

---

🧪 Testing

Run backend tests with:

pytest

The test suite covers:

- Agent initialization
- Event adaptation
- Runner initialization
- Investigation event emission

Integration tests should be run against a configured Gemini environment.

---

🔐 Security

Secrets must never be committed to Git.

Use environment variables for:

- Gemini API keys
- Grafana credentials
- ClickHouse credentials
- Parallel credentials
- Cloud credentials

".env" files should remain local.

Use ".env.example" to document required variables without exposing secrets.

---

🛠️ Development Phases

ShotOps is being developed incrementally.

Phase 1 — Product Foundation

- Core product architecture
- Production dashboard
- Investigation experience
- Incidents
- Reports
- Agent activity interface
- Responsive design

Phase 2 — Investigation Infrastructure

- Investigation lifecycle
- Event model
- Investigation persistence layer
- SSE event streaming
- Loading experience
- Investigation workspace

Phase 3A — Real Gemini + ADK

Current phase.

- Real Google ADK agent
- Real Gemini execution
- ADK Runner
- ADK event streaming
- Local FastAPI backend
- Frontend event streaming

Partner integrations are intentionally not connected during this phase.

Phase 3B — Grafana

- Grafana Cloud
- Grafana MCP
- Production metrics
- Logs
- Traces
- Alerts
- Incident investigation

Phase 3C — ClickHouse + Parallel

- Historical production analytics
- Rendering analytics
- Production trends
- External intelligence
- Research workflows

Phase 3D — Evidence Fusion

- Cross-source correlation
- Root-cause analysis
- Confidence scoring
- Production impact assessment
- Recommendations
- Human approval workflow

---

🎯 Design Principles

1. Evidence before conclusions

ShotOps should never manufacture telemetry or pretend a tool returned information when it did not.

2. Agent transparency

Users should be able to understand what the agent is doing.

3. Tool specialization

Each external system has a clear role.

4. Human control

Recommendations can be reviewed before operational actions are executed.

5. Production-first UX

ShotOps should feel like a serious production operations system, not a generic AI chatbot.

6. Observable AI

The agent itself should generate useful operational telemetry so teams can understand its behavior, latency, tool usage, failures, and performance.

---

🏆 Agentic Cinema Hackathon

ShotOps is being developed for the Agentic Cinema: The Blockbuster Hackathon.

The project focuses on applying agentic AI to real production operations workflows.

The core concept is:

«Give a production team an AI operations director that can investigate problems across multiple sources of operational intelligence and explain why something is going wrong.»

The project is designed to demonstrate:

- Agentic reasoning
- Tool use
- Production observability
- Cross-source evidence correlation
- Human-in-the-loop operations
- Explainable recommendations
- AI observability

---

📜 License

This project is open source.

See ""LICENSE"" (./LICENSE) for the full license.

---

👥 Project

ShotOps

AI Production Operations Director

«Your production has a problem. ShotOps finds out why.»
