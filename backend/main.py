"""
NexusCore Backend API & WebSocket Server
FastAPI server handling HUD WebSocket connections, swarm orchestration,
PR Review Engine, and serving the Futuristic Mission Control HUD.
"""

import sys
import pathlib

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is in sys.path
backend_dir = pathlib.Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.orchestrator import SwarmOrchestrator
from pr_reviewer import PRReviewEngine, PRReviewResult

app = FastAPI(
    title="NexusCore Mission Control API",
    description="Autonomous DevSecOps Swarm with Self-Healing Intelligence & PR Reviewer",
    version="2.0.0"
)

# Enable CORS for local Next.js / React / Static dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
orchestrator = SwarmOrchestrator(broadcast_fn=manager.broadcast)

class RunMissionRequest(BaseModel):
    task: str = "Build a secure user management module with database lookup"
    attack_mode: Optional[str] = None

class AttackSimulationRequest(BaseModel):
    attack_type: str

class PRReviewRequest(BaseModel):
    pr_title: str = "Update user authentication logic"
    code_or_diff: str

FRONTEND_HTML_PATH = backend_dir.parent / "frontend" / "index.html"

@app.get("/")
async def serve_hud():
    """Serves the Futuristic Mission Control Dashboard directly."""
    if FRONTEND_HTML_PATH.exists():
        return FileResponse(FRONTEND_HTML_PATH)
    return {
        "status": "ONLINE",
        "system": "NexusCore Mission Control v2.0",
        "agents": ["AGENT_SCOUT", "AGENT_BUILDER", "AGENT_GUARDIAN", "AGENT_AUDITOR"]
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "NexusCore Mission Control v2.0",
        "threat_level": orchestrator.threat_level,
        "token_burn": orchestrator.token_burn,
        "active_clients": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({
        "event": "SYSTEM_READY",
        "threat_level": orchestrator.threat_level,
        "token_burn": orchestrator.token_burn,
        "message": "Connected to NexusCore Mission Control WebSocket Stream.",
        "active_agents": 4
    })
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/run-swarm")
async def run_swarm(req: RunMissionRequest):
    if orchestrator.is_running:
        return {"status": "BUSY", "message": "A swarm mission is already in progress."}

    asyncio.create_task(orchestrator.run_mission(req.task, req.attack_mode))
    return {
        "status": "STARTED",
        "task": req.task,
        "attack_mode": req.attack_mode
    }

@app.post("/api/simulate-attack")
async def simulate_attack(req: AttackSimulationRequest):
    task_map = {
        "SQL_INJECTION": "Search user database with dynamic search filters",
        "SECRET_LEAK": "Initialize internal cloud notification service",
        "COMMAND_HIJACK": "Run server cache cleanup and disk optimization"
    }
    task = task_map.get(req.attack_type, "Perform system operation")
    asyncio.create_task(orchestrator.run_mission(task, req.attack_type))
    return {
        "status": "ATTACK_TRIGGERED",
        "attack_type": req.attack_type,
        "simulated_task": task
    }

@app.post("/api/review-pr")
async def review_pull_request(req: PRReviewRequest):
    """
    Automated PR Review Endpoint.
    Analyzes Pull Request code/diff, catches vulnerabilities, generates Git suggestions,
    and returns a structured Markdown PR comment.
    """
    result: PRReviewResult = await PRReviewEngine.review_pr(req.pr_title, req.code_or_diff)
    
    # Broadcast PR Review event over WebSocket so HUD updates in real-time
    await manager.broadcast({
        "event": "PR_REVIEW_COMPLETED",
        "threat_level": "CRITICAL" if result.status == "REQUEST_CHANGES" else "SAFE",
        "data": {
            "pr_title": req.pr_title,
            "status": result.status,
            "verdict": result.executive_verdict,
            "findings_count": len(result.findings),
            "findings": [f.dict() for f in result.findings],
            "markdown_report": result.markdown_report,
            "raw_diff": result.raw_diff,
            "healed_code": result.healed_code
        }
    })

    return result.dict()

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🛰️  NEXUSCORE MISSION CONTROL v2.0")
    print("🚀  Dashboard URL: http://localhost:8000")
    print("⚡  WebSocket:    ws://localhost:8000/ws")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
