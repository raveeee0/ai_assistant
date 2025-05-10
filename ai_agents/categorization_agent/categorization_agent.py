from google.adk.agents import Agent

from ai_agents.categorization_agent import prompt

categorization_agent = Agent(
    model="gemini-2.0-flash-001",
    name="categorization_agent",
    description="Categorizes emails into different categories",
    instruction=prompt.CATEGORIZATION_AGENT_INSTR,
)