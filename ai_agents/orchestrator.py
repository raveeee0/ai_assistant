import os
from dotenv import load_dotenv
import asyncio
from typing import Optional, Dict, Any

import logging
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from pydantic import BaseModel, Field
from google.adk.events import Event

from typing_extensions import override

load_dotenv()

# Configure API keys using os.getenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "default_value")

print("Google API Key:", os.getenv("GOOGLE_API_KEY"))

# Logging Setup
import logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure API keys using environment variables
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "default_value")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "default_value")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "False")

# Model Constants
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_DEEPSEEK_CHAT = "deepseek/deepseek-chat"

# Constants
APP_NAME = "email_processor"
USER_ID = "12345"
SESSION_ID = "email_session_001"
GEMINI_MODEL = "gemini-2.0-flash"



class EmailProcessorAgent(BaseAgent):
    """
    Orchestrates email processing workflow with specialized agents
    """
    # Sub-agents
    problem_categorizer: LlmAgent
    account_mgmt_agent: LlmAgent
    bug_report_agent: LlmAgent
    faq_agent: LlmAgent
    draft_generator: LlmAgent
    compliance_checker: LlmAgent
    solution_retriever: LlmAgent
    it_task_generator: LlmAgent

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        print("Starting email processing workflow")
        
        if "email_content" not in ctx.session.state:
            raise ValueError("Email content not found in session state")
        email_content = ctx.session.state["email_content"]
        
        print(f"Processing email content: {email_content}")
            
        # Check if email is a reply
        is_reply = ctx.session.state.get("is_reply", False)
        
        print(is_reply)
        
        if is_reply:
            # Handle reply flow with proper event streaming
            async for event in self.handle_reply_flow(ctx):
                yield event
        else:
            print(".----------------------------------------")
            print(ctx.session.state)
            # Handle new email flow with proper event streaming
            async for event in self.handle_new_email_flow(ctx):
                yield event

    async def handle_reply_flow(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Content examination with event streaming
        async for event in self.problem_categorizer.run_async(ctx):
            yield event
        
        # Check for persistent tech issues
        if ctx.session.state.get("persistent_tech_issue"):
            # Retrieve and summarize previous emails
            async for event in self.solution_retriever.run_async(ctx):
                yield event
            summary = ctx.session.state["summary"]
            logger.info(f"Email summary: {summary}")
            
            # Generate IT task
            async for event in self.it_task_generator.run_async(ctx):
                yield event
        else:
            logger.info("No persistent issues detected")

    async def handle_new_email_flow(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Categorize problem type with event streaming
        async for event in self.problem_categorizer.run_async(ctx):
            yield event
        
        
        print(ctx.session.state)
        
        if ctx.session.state["problem_type"].endswith("\n"):
            ctx.session.state["problem_type"] = ctx.session.state["problem_type"][:-1]
            
        problem_type = ctx.session.state["problem_type"]
        
        
        print(ctx.session.state)
        
        if problem_type == "password_reset":
            print("Password reset request detected")
            async for event in self.account_mgmt_agent.run_async(ctx):
                yield event
        elif problem_type == "username_change":
            print("Username change request detected")
            async for event in self.account_mgmt_agent.run_async(ctx):
                yield event
        elif problem_type == "refund_request":
            print("Refund request detected")
            async for event in self.compliance_checker.run_async(ctx):
                yield event
            print(ctx.session.state)
            
            if ctx.session.state["compliant"].endswith("\n"):
                ctx.session.state["compliant"] = ctx.session.state["compliant"][:-1]
                
            print(ctx.session.state)
            
            if ctx.session.state["compliant"]:
                async for event in self.draft_generator.run_async(ctx):
                    yield event
                    
                print(ctx.session.state)
                    
                    
        elif problem_type == "bug_report":
            print("Bug report detected")
            async for event in self.bug_report_agent.run_async(ctx):
                yield event
            async for event in self.solution_retriever.run_async(ctx):
                yield event
        else:
            async for event in self.faq_agent.run_async(ctx):
                yield event
        
        # Draft generation with event streaming
        async for event in self.draft_generator.run_async(ctx):
            yield event
        
        draft = ctx.session.state["draft"]
        logger.info(f"Draft generated: {draft}") 
    
# Define individual agents
problem_categorizer = LlmAgent(
    name="ProblemCategorizer",
    model=GEMINI_MODEL,
    instruction="""Classify the email {email_content} into one of these categories:
    password_reset, username_change, refund_request, bug_report
    RESPOND WITH ONLY ONE OF THE ABOVE LISTED CATEGORIES
    DO NOT ADD ANY ADDITIONAL CHARACTER""",
    output_key="problem_type"
)

account_mgmt_agent = LlmAgent(
    name="AccountManagement",
    model=GEMINI_MODEL,
    instruction="""Handle account-related requests:
    1. Password reset: Generate secure link
    2. Username change: Validate new username""",
    output_key="account_action"
)


bug_report_agent = LlmAgent(
    name="BugReportAgent",
    model=GEMINI_MODEL,
    instruction="""Analyze bug reports:
    - Identify affected components
    - Suggest temporary workarounds""",
    output_key="bug_analysis"
)

faq_agent = LlmAgent(
    name="FAQAgent",
    model=GEMINI_MODEL,
    instruction="""Answer common questions using provided documentation:
    [Insert your FAQ document here]""",
    output_key="faq_answer"
)

draft_generator = LlmAgent(
    name="DraftGenerator",
    model=GEMINI_MODEL,
    instruction="""Generate professional email to {destination_email} based on the email content {email_content} for {problem_type}""",
    output_key="draft"
)

compliance_checker = LlmAgent(
    name="ComplianceChecker",
    model=GEMINI_MODEL,
    instruction="""Check request {email_content} from {destination_email} against company policies, 
    RESPOND WITH ONLY True OR False""",
    output_key="compliant"
)

solution_retriever = LlmAgent(
    name="SolutionRetriever",
    model=GEMINI_MODEL,
    instruction="""Retrieve similar past solutions from knowledge base""",
    output_key="solutions"
)

it_task_generator = LlmAgent(
    name="ITTaskGenerator",
    model=GEMINI_MODEL,
    instruction="""Create Jira ticket for IT team""",
    output_key="jira_ticket"
)

# Create orchestrator
email_processor = EmailProcessorAgent(
    name="EmailProcessor",
    problem_categorizer=problem_categorizer,
    account_mgmt_agent=account_mgmt_agent,
    bug_report_agent=bug_report_agent,
    faq_agent=faq_agent,
    draft_generator=draft_generator,
    compliance_checker=compliance_checker,
    solution_retriever=solution_retriever,
    it_task_generator=it_task_generator
)



# Run the workflow
def process_email(email: str, user_email: str):
    # Setup session
    session_service = InMemorySessionService()
    initial_state = {
        "email_content": email,
        "destination_email": user_email,
        "is_reply": False
    }
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID, 
        session_id=SESSION_ID,
        state=initial_state
    )

    runner = Runner(
        agent=email_processor,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    print(f"Processing email: {email}")
    
    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role='user',
            parts=[types.Part(text="Process this email")]
        )
    )
    
    final_response = "not executed"
    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
            
    print(f"Final response: {final_response}")

# Example usage
process_email("Voglio un rimborso, mia madre è morta", "gmail@gmail.com")