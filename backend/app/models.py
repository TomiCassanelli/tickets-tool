from pydantic import BaseModel, Field


class Ticket(BaseModel):
    title: str = Field(..., description="A short, clear title for the issue or feature")
    description: str = Field(..., description="User story or detailed technical description")
    type: str = Field(..., description="Must be 'Bug', 'Feature' or 'Task'")
    priority: str = Field(..., description="Must be 'High', 'Medium' or 'Low'")


class UserRequest(BaseModel):
    raw_text: str
