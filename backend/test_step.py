import sys, pathlib, asyncio
backend_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
from agents.scout import ScoutAgent
from agents.builder import BuilderAgent
from agents.guardian import GuardianAgent
from agents.auditor import AuditorAgent

async def emit(n, a, m): print(f"[{n}] {m}", flush=True)
async def alert(d): print("ALERT!", flush=True)

async def main():
    print("Testing Scout...", flush=True)
    bp = await ScoutAgent.research("test", emit, delay=0)
    print("Scout done!", flush=True)

    print("Testing Builder...", flush=True)
    b_res = await BuilderAgent.build_code(bp, "SQL_INJECTION", emit, delay=0)
    print("Builder done!", flush=True)

    print("Testing Guardian...", flush=True)
    scan, dec = await GuardianAgent.audit_code(b_res["code"], emit, alert, delay=0)
    print("Guardian done! Decision:", dec, flush=True)

    print("Testing Builder Self-Heal...", flush=True)
    healed = await BuilderAgent.self_heal(b_res["code"], "fix", "SQL_INJECTION", emit, delay=0)
    print("Self-heal done!", flush=True)

    print("Testing Auditor...", flush=True)
    t_res = await AuditorAgent.generate_and_run_tests(healed, "SQL_INJECTION", emit, delay=0)
    print("Auditor done! Result:", t_res["passed"], flush=True)

asyncio.run(main())
