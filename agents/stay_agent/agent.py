from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from shared.agent_output import parse_agent_output
from dotenv import load_dotenv
load_dotenv()

groq_model = LiteLlm(model="groq/openai/gpt-oss-20b")

stay_agent = Agent(
    name="stay_agent",
    model=groq_model,
    description="Suggests hotel or stay options for a destination.",
    instruction=(
    "Suggest realistic stays in the requested destination city and dates. "
    "The stay budget is for the entire visit, not per night. Prices are estimates, "
    "not live availability. Never invent a stay or price to fit the budget. "
    "If no reliable option fits, return "
    '{"options": [], "note": "No reliable stay estimate fits the stated budget."}. '
    "Return only valid JSON with this shape: "
    '{"options": [{"name": "stay name", "location": "area", '
    '"price_per_night": 0, "estimated_total": 0, "currency": "USD"}], '
    '"note": "short note"}. '
    "Do not include markdown fences, reasoning, or text outside the JSON."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)

USER_ID = "user_stay"
from uuid import uuid4

async def execute(request):
    session_id = f"session_{uuid4().hex}"
    await session_service.create_session(
        app_name="stay_app",
        user_id=USER_ID,
        session_id=session_id
    )

    prompt = (
        f"Origin: {request['origin']}\n"
        f"Destination: {request['destination']}\n"
        f"Dates: {request['start_date']} to {request['end_date']}\n"
        f"Maximum stay budget for the whole visit: ${request['stay_budget']} USD.\n"
        "Return only the JSON object required by your instructions."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            parts = event.content.parts if event.content and event.content.parts else []
            response_text = "".join(
                part.text or "" for part in parts
            ).strip()

            try:
                return parse_agent_output(
                    response_text,
                    {
                        "name",
                        "location",
                        "price_per_night",
                        "estimated_total",
                        "currency",
                    },
                )
            except ValueError as exc:
                print(f"Invalid stay-agent response: {response_text!r}")
                raise RuntimeError(
                    "Stay agent did not return the expected JSON."
                ) from exc

    raise RuntimeError("Stay agent finished without a final response.")