**DevOps Agent** is an autonomous, AI-driven platform that uses a **ReAct (Reasoning + Acting)** engine to automate complex DevOps workflows — from CI/CD pipeline management and infrastructure provisioning to real-time incident response and cost optimization.

Instead of manually running commands, configuring YAML, or debugging failures at 3 AM, DevOps Agent **thinks, plans, and executes** — all while keeping a human-in-the-loop for critical operations.

**Quick Start**

 Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional, for full stack)
- Git

1. Clone the Repository
bash
git clone https://github.com/hitesh0106/DevOps-Agent.git
cd DevOps-Agent

2. Set Up Environment
bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

3. Configure Environment Variables
bash
cp .env.example .env
# Edit .env with your API keys and configuration

4. Run the Application
bash
# Start the API server + Dashboard

uvicorn api.main:app --reload --port 8000

# Open browser → http://localhost:8000

5. Full Stack with Docker (Optional)
bash
docker-compose up -d
This starts: **API Server**, **PostgreSQL**, **Redis**, **Prometheus**, **Grafana**, and **Alertmanager**.
    <img src="https://img.shields.io/github/forks/hitesh0106/DevOps-Agent?style=social" alt="GitHub Forks"/>
  </a>
</p>

