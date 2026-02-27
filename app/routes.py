from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse, HealthResponse
from app.agent.agent_builder import agent_builder
from app.services.dataset_loader import dataset_loader
from app.services.visualization import execute_chart_code
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts natural language questions, analyzes Titanic dataset using Agent,
    and returns a clean textual answer with optional visualization base64 chart.
    """
    try:
        # 1. Invoke agent to generate structured response
        agent_response = await agent_builder.invoke_agent(request.question)
        
        answer = agent_response.get("answer", "No answer provided.")
        requires_chart = agent_response.get("requires_chart", False)
        chart_code = agent_response.get("chart_code")
        chart_type = agent_response.get("chart_type")

        final_chart_base64 = None
        final_chart_type = None

        # 2. Generate visualization if requested and code is provided
        if requires_chart and chart_code:
            logger.info("Chart requested by agent. Generating visualization.")
            df = dataset_loader.load_dataset()
            base64_str, generated_type = execute_chart_code(chart_code, df)
            
            if base64_str:
                final_chart_base64 = base64_str
                # Prefer generated_type if detected, else fallback to agent's guess
                final_chart_type = generated_type if generated_type and generated_type != "unknown" else chart_type

        return ChatResponse(
            answer=answer,
            chart=final_chart_base64,
            chart_type=final_chart_type
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint to ensure API and dataset are ready."""
    return HealthResponse(status="ok")
