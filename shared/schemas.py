from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

class TravelRequest(BaseModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date
    flight_budget: float = Field(ge=0, allow_inf_nan=False)
    stay_budget: float = Field(ge=0, allow_inf_nan=False)
    activity_budget: float = Field(ge=0, allow_inf_nan=False)

    @field_validator("origin", "destination")
    @classmethod
    def strip_location(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Location must not be empty.")
        return value

    @model_validator(mode="after")
    def validate_trip_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date.")
        return self
