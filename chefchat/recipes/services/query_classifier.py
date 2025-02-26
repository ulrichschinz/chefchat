from openai import OpenAI
from chefchat.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
import logging
from chefchat.config import OPENAI_API_KEY

log = logging.getLogger(__name__)

def classify_query(query: str) -> str:
    prompt = (
        "Classify the following user query into one of two categories:\n"
        "1. weekly_plan - if the query is about creating or adjusting a weekly meal plan (e.g., 'gimme something for 5 days', 'weekly meal plan').\n"
        "2. detailed_request - if the query asks for detailed recipe information or a shopping list.\n"
        "Return only one word: either 'weekly_plan' or 'detailed_request'.\n"
        "User Query: " + query
    )
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an assistant that classifies user queries."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=10,
    temperature=0)
    log.debug(response)
    classification = response.choices[0].message.content.strip().lower()
    log.debug(f"Classification: {classification}")
    if "weekly" in classification:
        return "weekly_plan"
    else:
        return "detailed_request"
