import os
from dotenv import load_dotenv
import pyautogui
import asyncio
from typing import Optional, Dict, Any

# Google Agent Development Kit (ADK) Imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool

# Custom Module Imports
from assistant.sub_agents.browser_agent import browser_agent
from assistant.sub_agents.desktop_agent import desktop_agent
from assistant.sub_agents.research_agent import research_agent
from assistant.sub_agents.feedback_agent import feedback_agent
from assistant import prompt

# Logging Setup
import logging
logging.basicConfig(level=logging.ERROR)

# Load environment variables from .env file
load_dotenv()

# Configure API keys using environment variables
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "default_value")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "default_value")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "False")

# Application Constants
APP_NAME = "assistant_agent"
USER_ID = "user_1"

# Model Constants
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_DEEPSEEK_CHAT = "deepseek/deepseek-chat"

# Root Agent Configuration
root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    description="A Travel Concierge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        desktop_agent,
        browser_agent,
        research_agent,
        feedback_agent
    ]
)