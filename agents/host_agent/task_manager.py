import asyncio

from common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"

async def run(payload):
    # 👀 Print what the host agent is sending
    print("🚀 Incoming payload:", payload)

    flights, stay, activities = await asyncio.gather(
        call_agent(FLIGHT_URL, payload),
        call_agent(STAY_URL, payload),
        call_agent(ACTIVITIES_URL, payload),
    )

    # 🧾 Log outputs
    print("📦 flights:", flights)
    print("📦 stay:", stay)
    print("📦 activities:", activities)

    results = {
        "flights": flights,
        "stays": stay,
        "activities": activities,
    }

    for name, result in results.items():
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("options"), list)
            or not isinstance(result.get("note"), str)
        ):
            raise ValueError(f"{name} agent returned an invalid response.")

    return results