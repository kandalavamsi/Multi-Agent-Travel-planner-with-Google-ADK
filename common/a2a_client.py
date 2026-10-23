import httpx


async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError(f"Agent at {url} returned a non-object response.")
        return result