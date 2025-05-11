from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.config import get_stream_writer
from langchain_google_genai import GoogleGenerativeAI
from github import Github
import os
import logging
import random
from dotenv import load_dotenv

# print executing directory
print(f"Executing directory: {os.getcwd()}")


from services.RAG.rag_service import RAGModule
# Initialize RAG module
rag = RAGModule(index_path="./faiss_index/", model_name="all-MiniLM-L6-v2")


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

# def call_gemini(prompt: str) -> str:
#     logger.info(f"LLM Prompt: {prompt}")
#     response = gemini_model.invoke(prompt)
#     return response.strip()

def call_gemini(prompt: str, stream: bool = False) -> str:
    logger.info(f"LLM Prompt: {prompt}")
    try:
        if stream:
            return gemini_model.stream(prompt)
        else:
            return gemini_model.invoke(prompt).strip()
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        return f"Error: {str(e)}"

# -------------------------------
# Step 3: Define Agent Nodes
# -------------------------------

def categorize_problem(state: EmailState) -> Dict[str, Any]:

    writer = get_stream_writer()

    prompt = f"""
        Classify the email with subject: {state.subject}, content: {state.email_content} into one of these categories:
        username_change, password_reset, refund_request, bug_report, faq or other
    """
    response = call_gemini(prompt)
    category = f"<thinking> categorize problem ... {response} </thinking>"
    writer({"custom_key": category})
    return {"problem_type": response}


def account_management(state: EmailState) -> Dict[str, Any]:

    if "password" in state.problem_type.lower():

        writer = get_stream_writer()
        writer({"custom_key": "<action> generate password reset link </action>"})

        def generate_password_reset_link():
            # Generate a secure password reset link that concatenates a random string with the base URL
            base_url = f"https://example.com/reset_"
            random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
            return f"{base_url}?token={random_string}"
        # Generate a password reset link
        state.link = generate_password_reset_link()
    elif "username" in state.problem_type.lower():

        writer = get_stream_writer()
        writer({"custom_key": "<action> generate username reset link </action>"})

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

    writer = get_stream_writer()
    writer({"custom_key": "<action> creating ticket for the bug </action>"})

    prompt = f"""
        Bug report: {state.email_content}

        Output format:
        summarize the bug without adding any other information, just the bug description
    """
    response = call_gemini(prompt)
    user = g.get_user()
    repo = g.get_repo("bonsurha/EXAMPLE")
    # Get the first project
    bug_body = response
    print(f"Bug body: {bug_body}")
    # Create a new issue in the GitHub repository   
    issue = repo.create_issue(
        title=f"Bug Report",
        body=bug_body,
        labels=["bug", "triage"]
    )

    return {"bug_analysis": response}

def faq_answer(state: EmailState) -> Dict[str, Any]:

    writer = get_stream_writer()
    writer({"custom_key": "<thinking> retrieve data from knowledge based </thinking>"})

    rag_response = rag.generate_context(state.email_content)
    prompt = f"""
        Answer common questions using provided documentation:
        Include just the email body

        Question: {state.email_content}
        Provided rag context: {rag_response}
    """
    response = call_gemini(prompt)

    return {"faq_answer": response}

def check_compliance(state: EmailState) -> Dict[str, Any]:

    writer = get_stream_writer()
    writer({"custom_key": "<action> retrieving data from knowledge based </action>"})

    rag_response = rag.generate_context("What is the company policy for refund requests?")
    prompt = f"""
        Check request {state.email_content} from {state.destination_email} against company policies.
        Company policy: {rag_response}
        RESPOND WITH ONLY True OR False
    """
    response = call_gemini(prompt)
    compliant = response.lower() == "true"
    return {"compliant": compliant}

def refund_request(state: EmailState):
    # Verify payments information

    writer = get_stream_writer()
    writer({"custom_key": "<action> Researching user payment information </action>"})
    return

def generate_draft(state: EmailState) -> Dict[str, Any]:
    print("Generating draft...")
    writer = get_stream_writer()
    writer({"custom_key": "<thinking> Generating draft email </thinking>"})

    print(f"Content: {state}")

    if state.problem_type == "password_reset":
        prompt = f"""
        Generate professional email to {state.destination_email} with password reset link: {state.link} for username: {state.username}
        Do not add any subject, just the body of the email.
        Here's a template:

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
        Do not add any subject, just the body of the email.
        Here's a template:

        Dear [User's First Name],

        We received a request to change username. If you initiated this request, please click the button below to set a new username:

        (Link: [Insert Secure Reset Link])

        This link will expire in 24h for security purposes.

        Message by pippo company.

        If you did not request a username change, you can safely ignore this email or contact our support team at [Support Email/Phone] to investigate further. 
    """
    elif state.problem_type == "bug_report":
        prompt = f"""
        Generate professional email to {state.destination_email} for username: {state.username}
        Do not add any subject, just the body of the email.
        
        Template:
        Dear {state.username},
        Thank you for reporting the issue with our application. We appreciate your feedback and are actively working to resolve it.
        We have created a ticket for this issue and will keep you updated on its progress. In the meantime, if you have any further information or questions, please feel free to reach out.

        Best regards,
        Example company"""
    elif state.problem_type == "faq" or state.problem_type == "other":
        prompt = f"""
        Generate professional email to {state.destination_email} with FAQ answer: {state.faq_answer}
        Do not add any subject, just the body of the email.
    """
    elif state.problem_type == "refund_request":
        prompt = f"""Do not add any subject, just the mail content.
        Ironic email to not refund the user

    """
    response = call_gemini(prompt, True)

    for chunk in response:
        writer({"custom_key": chunk})
    return {"draft": response}



# -------------------------------
# Step 4: Define Conditional Routing
# -------------------------------

def route_after_categorization(state: EmailState):

    if state.problem_type in ["password_reset", "username_change"]:
        return "account_management"
    elif state.problem_type == "bug_report":
        return "bug_report"
    elif state.problem_type == "refund_request":
        return "refund_request"
    elif state.problem_type == "faq" or state.problem_type == "other":
        return "faq_handler"


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
graph.add_node("refund_request", refund_request)



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
        "refund_request": "refund_request"
    }
)

# Add direct edges
graph.add_edge("account_management", "generate_draft")
graph.add_edge("bug_report", "generate_draft")
graph.add_edge("faq_handler", "generate_draft")
graph.add_edge("check_compliance", "generate_draft")
graph.add_edge("refund_request", "generate_draft")
graph.add_edge("generate_draft", END)

# Compile the graph
app = graph.compile()


# -------------------------------
# Step 6: Run the Workflow
# -------------------------------

def process_email(initial_state: EmailState):
    stream = app.stream(initial_state, stream_mode="custom")
    return stream


def summary_email(state: str) -> [str]:
    prompt = f"""
        Summarize the email content: {state}
        Output format:
        - summary
    """
    stream = call_gemini(prompt, True)
    return stream