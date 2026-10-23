from fastapi import FastAPI
from shared.schemas import TravelRequest

def create_app(agent):
    app = FastAPI()

    @app.post("/run")
    async def run(request: TravelRequest):
        return await agent.execute(request.model_dump(mode="json"))

    return app