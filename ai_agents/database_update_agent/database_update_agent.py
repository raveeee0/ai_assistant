from google.adk.agents import Agent

from ai_agents.database_update_agent import prompt

categorization_agent = Agent(
    model="gemini-2.0-flash-001",
    name="database_update_agent",
    description="Updates the RAG system",
    instruction=prompt.DATABASE_UPDATE_AGENT_INSTR,
)