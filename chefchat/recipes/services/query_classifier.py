from openai import OpenAI
from chefchat.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
import logging
from chefchat.config import OPENAI_API_KEY

log = logging.getLogger(__name__)


CLASSIFICATION_PROMPT = """
You are a query analysis assistant for a meal planning and recipe management system.
Your primary task is to analyze incoming user queries and determine the type of action the user intends to perform.
The query types are defined as follows:

# Planning Mode:
Purpose: The user wants to create or view a meal plan.
Indicators: Look for keywords or phrases such as "plan", "menu", "schedule", "week", "meal plan", "propose recipes", "for #number days" or "list recipes for the week".
Answer: planning_request

# Plan Modification Mode:
Purpose: The user wishes to change or adjust an existing weekly plan.
Indicators: Look for terms like "change", "replace", "swap", "modify", "adjust", or conditions like "without meat" when referring to a specific day.
Answer: planning_change_request

# Use Plan Mode:
Purpose: The user requests detailed information, such as displaying a full recipe or generating a shopping list.
Indicators: Look for requests like "show me", "display", "full recipe", "detailed", "ingredients", or "shopping list".
Answer: use_plan_request

Instructions:
Step 1: Read the incoming query carefully.
Step 2: Identify key phrases or keywords that point to one of the three modes above.
Step 3: Categorize the query into Planning, Modification, or Execution Mode.
Step 4: Answer only one word for each query, the word you can find in Answer.
Step 5: If the query is ambiguous or does not clearly fall into one category, ask a clarifying question such as: "Can you please clarify if you want to create a new plan, modify an existing plan, or view detailed recipe information?"
"""

def classify_query(query: str) -> str:
    prompt = (
        CLASSIFICATION_PROMPT + query
    )
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a query analysis assistant for a meal planning and recipe management system. Your primary task is to analyze incoming user queries and determine the type of action the user intends to perform."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=10,
    temperature=0)
    classification = response.choices[0].message.content.strip().lower()
    log.debug(f"Classification: {classification}")
    if "planning_request" in classification:
        return "planning_request"
    elif "planning_change_request" in classification:
        return "planning_change_request"
    elif "use_plan_request" in classification:
        return "use_plan_request"
    elif "clarify if you want to create a new plan" in classification:
        return "clarify_request"
