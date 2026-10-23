from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()

groq_model = LiteLlm(model="groq/openai/gpt-oss-20b")

host_agent = Agent(
    name="host_agent",
    model=groq_model,
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction="You are the host agent responsible for orchestrating trip planning tasks. "
                "You call external agents to gather flights, stays, and activities, then return a final result."
)

session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)

USER_ID = "user_host"

async def execute(request):
    session_id = f"session_{uuid4().hex}"
    await session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=session_id,
    )

    prompt = (
        f"Plan a trip from {request['origin']} to {request['destination']} "
        f"from {request['start_date']} to {request['end_date']}. "
        f"Flight budget: ${request['flight_budget']} USD per traveler; "
        f"stay budget: ${request['stay_budget']} USD for the whole visit; "
        f"activities budget: ${request['activity_budget']} USD per traveler. "
        "Summarize the trip clearly and label all prices as estimates."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            parts = event.content.parts if event.content and event.content.parts else []
            response_text = "".join(part.text or "" for part in parts).strip()
            if not response_text:
                raise RuntimeError("Host agent returned an empty response.")
            return {"summary": response_text}

    raise RuntimeError("Host agent finished without a final response.")
