# 🚀 DevOps Agent — AI-Powered Infrastructure Automation

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white" />
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" />
</p>

## 🧠 What is DevOps Agent?

DevOps Agent is an **AI-powered automation system** that handles tasks across the entire software delivery lifecycle — CI/CD pipelines, infrastructure provisioning, monitoring, alerting, incident response, and deployments — with minimal human intervention.

It uses a **ReAct (Reasoning + Acting)** loop powered by LLMs (Claude/GPT-4) to:
- **Perceive** — Receive events from GitHub, Prometheus, Slack
- **Reason** — Think about what happened and what to do
- **Act** — Execute tools (kubectl, terraform, docker, git)
- **Learn** — Store resolutions in vector memory for future reference

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EVENT SOURCES                         │
│  GitHub Webhooks │ Prometheus Alerts │ Slack │ API       │
└────────┬────────────────┬───────────────┬───────────────┘
         │                │               │
         ▼                ▼               ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Gateway                         │
│  /webhook/github │ /webhook/alertmanager │ /agent/task   │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────────────────────┐
│   Redis Queue    │───▶│       Celery Workers             │
└─────────────────┘    └──────────┬───────────────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │     🧠 Agent Core       │
                     │                         │
                     │  ┌───────────────────┐  │
                     │  │   ReAct Engine     │  │
                     │  │                   │  │
                     │  │  Think → Act →    │  │
                     │  │  Observe → Repeat │  │
                     │  └───────────────────┘  │
                     │                         │
                     │  ┌───────────────────┐  │
                     │  │   Tool Registry   │  │
                     │  │                   │  │
                     │  │  GitHub │ Docker  │  │
                     │  │  K8s │ Terraform  │  │
                     │  │  Shell │ Monitor  │  │
                     │  └───────────────────┘  │
                     │                         │
                     │  ┌───────────────────┐  │
                     │  │   Memory System   │  │
                     │  │                   │  │
                     │  │  Short │ Long     │  │
                     │  │  Term  │ Term     │  │
                     │  └───────────────────┘  │
                     └─────────────────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │    Safety Guardrails     │
                     │  Block dangerous cmds    │
                     │  Human approval flow     │
                     │  Audit logging           │
                     └─────────────────────────┘
```

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | Custom ReAct Engine + LangChain |
| LLM | Claude API / OpenAI GPT-4 (configurable) |
| Backend API | FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Vector DB | ChromaDB |
| Containers | Docker + Docker Compose |
| IaC | Terraform + Ansible |
| Monitoring | Prometheus + Grafana |
| Dashboard | Premium HTML/CSS/JS |
| Testing | Pytest + Coverage |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- Git

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/devops-agent.git
cd devops-agent

# 2. Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python -c "from api.models.database import init_db; init_db()"

# 6. Run the API server
uvicorn api.main:app --reload --port 8000

# 7. Open Dashboard
# Navigate to http://localhost:8000
```

### Docker Setup

```bash
docker-compose up -d
# Dashboard: http://localhost:8000
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### Run Agent Standalone

```bash
# Run a single task
python -m agent.core "Check the health of all running containers"

# Run with verbose ReAct trace
python -m agent.core "Diagnose why the API is returning 500 errors" --verbose
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=agent --cov=tools --cov=api

# Run specific module
pytest tests/test_agent/ -v
```

## 📁 Project Structure

```
devops-agent/
├── agent/          # 🧠 Core AI agent engine (ReAct loop, memory, prompts)
├── tools/          # 🔧 Agent tools (GitHub, Docker, K8s, Terraform, etc.)
├── api/            # 🌐 FastAPI backend (routes, models, middleware)
├── workers/        # ⚙️ Celery background workers
├── pipelines/      # 🔄 CI/CD pipeline definitions
├── infra/          # 🏗️ Infrastructure as Code (Terraform, Ansible)
├── monitoring/     # 📊 Prometheus, Grafana, Alertmanager configs
├── safety/         # 🛡️ Guardrails, approval system, sandboxing
├── dashboard/      # 🎨 Premium web dashboard
└── tests/          # 🧪 Test suite
```

## 🔑 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 ReAct Agent | Multi-step reasoning with tool use |
| 🔄 CI/CD Auto-Fix | Diagnoses build failures and creates fix PRs |
| 🏗️ IaC Management | Terraform plan/apply with safety checks |
| 📊 Self-Healing | Auto-restarts crashed pods, rolls back bad deploys |
| 🧠 Memory | Remembers past incidents via vector search |
| 👥 Multi-Agent | Specialized agents (CI/CD, Infra, Security) |
| 🛡️ Safety | Blocks dangerous commands, requires approval |
| 📈 Dashboard | Real-time monitoring with premium UI |

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
#   D e v O p s - A g e n t  
 