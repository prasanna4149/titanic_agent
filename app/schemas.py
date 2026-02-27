from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(..., description="Natural language question about the Titanic dataset")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Clean textual explanation answering the question")
    chart: Optional[str] = Field(None, description="Base64 encoded matplotlib PNG chart, if visualization was requested")
    chart_type: Optional[str] = Field(None, description="Type of chart generated (bar, histogram, pie, etc) or None")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status of the API")
