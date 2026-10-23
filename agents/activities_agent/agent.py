from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from shared.agent_output import parse_agent_output
from dotenv import load_dotenv
load_dotenv()

groq_model = LiteLlm(model="groq/openai/gpt-oss-20b")

activities_agent=Agent(
    name="activities_agent",
    model=groq_model,
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
    "Suggest 2-3 engaging activities in the requested destination city and dates. "
    "Prices are estimates. Keep each activity within the activities budget where possible. "
    "Return only valid JSON with this shape: "
    '{"options": [{"name": "activity name", "description": "short description", '
    '"estimated_price": 0, "duration_hours": 1, "currency": "USD"}], '
    '"note": "short note"}. '
    "If no suitable activity is available, return an empty options list and explain why in note. "
    "Do not include markdown fences, reasoning, or text outside the JSON."
)
)

session_service=InMemorySessionService()
runner=Runner(agent=activities_agent, app_name="activities_app", session_service=session_service)

USER_ID="user_activities"
from uuid import uuid4

async def execute(request):
    session_id = f"session_{uuid4().hex}"

    await session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=session_id
    )

    prompt = (
        f"Origin: {request['origin']}\n"
        f"Destination: {request['destination']}\n"
        f"Dates: {request['start_date']} to {request['end_date']}\n"
       f"Maximum activities budget per traveler: ${request['activity_budget']} USD.\n"
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

            if not response_text:
                raise RuntimeError(
                    "Activities agent returned an empty response. "
                    "Check the model/provider logs and API configuration."
                )

            try:
                return parse_agent_output(
                    response_text,
                    {
                        "name",
                        "description",
                        "estimated_price",
                        "duration_hours",
                        "currency",
                    },
                )
            except ValueError as exc:
                print(f"Invalid activities-agent response: {response_text!r}")
                raise RuntimeError(
                    "Activities agent did not return the expected JSON."
                ) from exc

    raise RuntimeError("Activities agent finished without a final response.")