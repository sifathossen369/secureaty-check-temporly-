import asyncio
from core.orchestrator import SwarmOrchestrator

async def broadcast(m):
    print(f"BROADCAST: {m.get('event')}", flush=True)

async def main():
    print("STARTING TEST...", flush=True)
    orc = SwarmOrchestrator(broadcast)
    print("ORCHESTRATOR CREATED", flush=True)
    res = await orc.run_mission("Search user", attack_mode="SQL_INJECTION")
    print("MISSION FINISHED!", res, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
