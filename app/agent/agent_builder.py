import json
import logging
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.agent.tools import TOOLS
from app.agent.prompt_template import SYSTEM_PROMPT_TEXT

logger = logging.getLogger(__name__)


class AgentBuilder:
    _instance = None
    _agent = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentBuilder, cls).__new__(cls)
        return cls._instance

    def build_agent(self):
        """Builds and returns a LangGraph ReAct Agent using ChatGroq."""
        if self._agent is not None:
            return self._agent

        logger.info("Initializing Groq LLM and LangGraph Agent...")

        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is not set correctly!")

        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
        )

        self._agent = create_react_agent(
            model=llm,
            tools=TOOLS,
            prompt=SYSTEM_PROMPT_TEXT,
        )

        logger.info("Agent initialized successfully.")
        return self._agent

    async def invoke_agent(self, question: str) -> dict:
        """Invokes the ReAct agent and parses the structured JSON response."""
        agent = self.build_agent()

        try:
            result = await agent.ainvoke({"messages": [("user", question)]})
            messages = result.get("messages", [])

            # Walk backward through messages to find the final AIMessage
            # that has non-empty text content and no pending tool_calls
            output_str = ""
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    # An AIMessage with pending tool calls is NOT the final answer
                    if msg.tool_calls:
                        continue
                    content = msg.content
                    if isinstance(content, str) and content.strip():
                        output_str = content.strip()
                        break
                    elif isinstance(content, list):
                        # Some models return content as a list of blocks
                        text_parts = [
                            block.get("text", "") if isinstance(block, dict) else str(block)
                            for block in content
                        ]
                        combined = " ".join(p for p in text_parts if p.strip())
                        if combined.strip():
                            output_str = combined.strip()
                            break

            if not output_str:
                logger.error("No usable AI message found in response.")
                output_str = "{}"

            logger.info(f"Raw agent output: {output_str[:300]}")

            # Strip markdown fences if the model wrapped JSON in them
            cleaned = output_str.strip()
            for fence in ("```json", "```"):
                if cleaned.startswith(fence):
                    cleaned = cleaned[len(fence):]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                parsed = json.loads(cleaned)
                logger.info(
                    f"Parsed agent response: requires_chart={parsed.get('requires_chart')}, "
                    f"chart_type={parsed.get('chart_type')}"
                )
                return parsed
            except json.JSONDecodeError:
                logger.warning(f"JSON parse failed, returning plain answer: {cleaned[:200]}")
                return {
                    "answer": cleaned or "I could not generate an answer.",
                    "requires_chart": False,
                    "chart_code": None,
                    "chart_type": None,
                }

        except Exception as e:
            logger.error(f"Agent invocation failed: {e}")
            raise RuntimeError(f"Agent execution error: {str(e)}")


agent_builder = AgentBuilder()
