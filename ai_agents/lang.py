from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import GoogleGenerativeAI
from github import Github
import os
import logging
import random
from dotenv import load_dotenv





# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
g = Github(os.getenv("GITHUB_TOKEN"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Step 1: Define the State Schema
# -------------------------------

class EmailState(BaseModel):
    subject: str
    link: Optional[str] = None
    username: str
    email_content: str
    destination_email: str
    problem_type: Optional[str] = None
    draft: Optional[str] = None
    compliant: Optional[bool] = None
    is_reply: bool = False
    persistent_tech_issue: bool = False
    summary: Optional[str] = None
    jira_ticket: Optional[str] = None
    bug_analysis: Optional[str] = None
    faq_answer: Optional[str] = None
    solutions: Optional[List[str]] = []

# -------------------------------
# Step 2: Gemini Model Setup
# -------------------------------

gemini_model = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

def call_gemini(prompt: str) -> str:
    logger.info(f"LLM Prompt: {prompt}")
    response = gemini_model.invoke(prompt)
    return response.strip()

# -------------------------------
# Step 3: Define Agent Nodes
# -------------------------------

def categorize_problem(state: EmailState) -> Dict[str, Any]:
    prompt = f"""
Classify the email with subject: {state.subject}, content: {state.email_content} into one of these categories:
username_change, password_reset, refund_request, bug_report, faq
    """
    response = call_gemini(prompt)

    # update counter of problem types on excel using Google Sheets API


    return {"problem_type": response}


def account_management(state: EmailState) -> Dict[str, Any]:

    if "password" in state.problem_type.lower():
        def generate_password_reset_link():
            # Generate a secure password reset link that concatenates a random string with the base URL
            base_url = f"https://example.com/reset_"
            random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
            return f"{base_url}?token={random_string}"
        # Generate a password reset link
        state.link = generate_password_reset_link()
    elif "username" in state.problem_type.lower():
        def generate_username_change_link():
            print("Generating username change link")
            # Generate a secure username change link that concatenates a random string with the base URL
            base_url = f"https://example.com/change_"
            random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
            return f"{base_url}?token={random_string}"
        # Generate a username change link
        state.link = generate_username_change_link()
        print(f"Username change link: {state.link}")
    else:
        # Handle other account actions
        state.link = None
        
    return {"link": state.link} 

def bug_report(state: EmailState) -> Dict[str, Any]:
    prompt = f"""
        Analyze bug reports:
        - Identify affected components
        - Suggest temporary workarounds

        Bug report: {state.email_content}

        Output format:
        summarize the bug
    """
    response = call_gemini(prompt)
    user = g.get_user()
    repo = g.get_repo("EXAMPLE")
    project = repo.get_projects()[0]  
    # Get the first project
    bug_body = response.split(":")[1]
    print(f"Bug body: {bug_body}")
    # Create a new issue in the GitHub repository   


    return {"bug_analysis": response}

def faq_answer(state: EmailState) -> Dict[str, Any]:
    prompt = f"""
        Answer common questions using provided documentation:
        [Insert your FAQ document here]

        Question: {state.email_content}
    """
    response = call_gemini(prompt)

    return {"faq_answer": response}

def check_compliance(state: EmailState) -> Dict[str, Any]:
    prompt = f"""
        Check request {state.email_content} from {state.destination_email} against company policies.
        RESPOND WITH ONLY True OR False
    """
    response = call_gemini(prompt)
    compliant = response.lower() == "true"
    return {"compliant": compliant}

def generate_draft(state: EmailState) -> Dict[str, Any]:
    print(f"Content: {state}")

    if state.problem_type == "password_reset":
        prompt = f"""
        Generate professional email to {state.destination_email} with password reset link: {state.link} for username: {state.username}
        Here's a template:
        Subject: Reset Your Account Password

        Dear [User's First Name],

        We received a request to reset the password for your account. If you initiated this request, please click the button below to set a new password:

        (Link: [Insert Secure Reset Link])

        This link will expire in 24h for security purposes.

        Message by pippo company.

        If you did not request a password reset, you can safely ignore this email or contact our support team at [Support Email/Phone] to investigate further. 


    """
    elif state.problem_type == "username_change":
        prompt = f"""
        Generate professional email to {state.destination_email} with username change link: {state.link} for username: {state.username}
        Here's a template:
        Subject: Change Your Account Username

        Dear [User's First Name],

        We received a request to change username. If you initiated this request, please click the button below to set a new username:

        (Link: [Insert Secure Reset Link])

        This link will expire in 24h for security purposes.

        Message by pippo company.

        If you did not request a username change, you can safely ignore this email or contact our support team at [Support Email/Phone] to investigate further. 
    """
    elif state.problem_type == "bug_report":
        prompt = f"""
        Generate professional email to {state.destination_email} with bug analysis: {state.bug_analysis}
    """
    elif state.problem_type == "faq":
        prompt = f"""
        Generate professional email to {state.destination_email} with FAQ answer: {state.faq_answer}
    """
    response = call_gemini(prompt)
    return {"draft": response}

def retrieve_solutions(state: EmailState) -> Dict[str, Any]:
    prompt = f"""
    Retrieve similar past solutions from knowledge base for: {state.email_content}
    """
    response = call_gemini(prompt).splitlines()
    return {"solutions": response}



# -------------------------------
# Step 4: Define Conditional Routing
# -------------------------------

def route_after_categorization(state: EmailState):
    if state.is_reply:
        return "retrieve_solutions"
    else:
        if state.problem_type in ["password_reset", "username_change"]:
            return "account_management"
        elif state.problem_type == "bug_report":
            return "bug_report"
        elif state.problem_type == "refund_request":
            return "check_compliance"
        elif state.problem_type == "faq":
            return "faq_handler"
        else:
            return "retrieve_solutions"

# -------------------------------
# Step 5: Build the Graph
# -------------------------------

graph = StateGraph(EmailState)

# Add nodes
graph.add_node("categorize_problem", categorize_problem)
graph.add_node("account_management", account_management)
graph.add_node("bug_report", bug_report)
graph.add_node("faq_handler", faq_answer)
graph.add_node("check_compliance", check_compliance)
graph.add_node("generate_draft", generate_draft)
graph.add_node("retrieve_solutions", retrieve_solutions)


# Set entry point
graph.set_entry_point("categorize_problem")

# Add conditional edges
graph.add_conditional_edges(
    "categorize_problem",
    route_after_categorization,
    {
        "account_management": "account_management",
        "bug_report": "bug_report",
        "check_compliance": "check_compliance",
        "faq_handler": "faq_handler",
        "retrieve_solutions": "retrieve_solutions"
    }
)

# Add direct edges
graph.add_edge("account_management", "generate_draft")
graph.add_edge("bug_report", "generate_draft")
graph.add_edge("faq_handler", "generate_draft")
graph.add_edge("check_compliance", "generate_draft")
graph.add_edge("generate_draft", END)

# Compile the graph
app = graph.compile()


# -------------------------------
# Step 6: Run the Workflow
# -------------------------------

def process_email(username: str,email_subject: str, email_body: str, user_email: str):
    initial_state = EmailState(
        username=username,
        subject=email_subject,
        email_content=email_body,
        destination_email=user_email,
        is_reply=False
    )
    final_state = app.invoke(initial_state)
    logger.info("Final Draft:\n%s", final_state["draft"])

# Example usage
if __name__ == "__main__":
    process_email("maradona", "gui error", "gui is broken", "user@example.com")