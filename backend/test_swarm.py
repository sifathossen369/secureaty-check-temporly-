import sys
import pathlib
# Ensure backend directory is in sys.path
backend_dir = pathlib.Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import asyncio
from core.orchestrator import SwarmOrchestrator

async def dummy_broadcast(msg):
    evt = msg.get("event")
    if evt in ("MISSION_STARTED", "SECURITY_ALERT", "THREAT_NEUTRALIZED", "MISSION_COMPLETE"):
        print(f"[{evt}] Threat Level: {msg.get('threat_level')}", flush=True)

async def main():
    print("Testing NexusCore Swarm with simulated SQL Injection...", flush=True)
    orc = SwarmOrchestrator(broadcast_fn=dummy_broadcast)
    result = await orc.run_mission("Search user directory", attack_mode="SQL_INJECTION")
    print(f"Mission Result: Success={result['success']}, ThreatNeutralized={result['threat_neutralized']}", flush=True)
    print(f"Sandbox Summary: {result['test_summary']}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
