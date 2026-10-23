from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from shared.agent_output import parse_agent_output
from dotenv import load_dotenv
load_dotenv()

groq_model = LiteLlm(model="groq/openai/gpt-oss-20b")

flight_agent = Agent(
    name="flight_agent",
    model=groq_model,
    description="Suggests flight options for a destination.",
    instruction=(
    "Suggest realistic round-trip flight options for the given origin, destination, dates, "
    "and flight budget. Treat prices as estimates; do not claim live availability. "
    "Never invent an option just to fit the budget. If no reliable option fits, return "
    '{"options": [], "note": "No reliable flight estimate fits the stated budget."}. '
    "Return only valid JSON with this shape: "
    '{"options": [{"airline": "name", "departure": "date and time", '
    '"return": "date and time", "stops": "direct or stop details", '
    '"estimated_price": 0, "currency": "USD"}], "note": "short note"}. '
    "Do not include markdown fences, reasoning, or text outside the JSON."
)
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

USER_ID = "user_1"
from uuid import uuid4

async def execute(request):
    # 🔧 Ensure session is created before running the agent
    session_id = f"session_{uuid4().hex}"
    await session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=session_id
    )

 
    prompt = (
    f"Origin: {request['origin']}\n"
    f"Destination: {request['destination']}\n"
    f"Dates: {request['start_date']} to {request['end_date']}\n"
    f"Maximum flight budget per traveler: ${request['flight_budget']} USD.\n"
    "Return only the JSON object required by your instructions."
    )


    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
        if event.is_final_response():
            parts = event.content.parts if event.content and event.content.parts else []
            response_text = "".join(part.text or "" for part in parts).strip()
            print(f"Flight model response: {response_text!r}")

            try:
                return parse_agent_output(
                    response_text,
                    {
                        "airline",
                        "departure",
                        "return",
                        "stops",
                        "estimated_price",
                        "currency",
                    },
                )
            except ValueError as exc:
                print(f"Flight response parsing failed: {exc}")
                raise RuntimeError(
                    "Flight agent did not return the expected JSON."
                ) from exc

    raise RuntimeError("Flight agent finished without a final response.")