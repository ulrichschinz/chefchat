import logging
from rest_framework.response import Response
from rest_framework import status
from recipes.vector.index import query_index_with_context
from recipes.models import ChatLog, Recipe

log = logging.getLogger(__name__)

BASE_PROPMT = """
You are a shopping and meal planning assistant.
Your main tasks are:

Weekly Meal Planning and Shopping List Creation:
Create a complete shopping list based on a weekly meal plan.
Use only recipes from the provided recipe list.
Combine identical ingredients and correctly add the quantities.
Group the ingredients into the following categories:

Fruits & Vegetables
Spices
Cans and Jars
Refrigerated Items
Miscellaneous
Single Recipe Display:
Display the complete recipe for a dish upon request, so it is handy while cooking.
Ensure that only the recipes from the provided list are used.
The goal is for the user to have a clearly structured meal plan, a detailed shopping list, and access to individual recipes at any time – all based on the provided recipe list.

Rules, Restrictions, and Formatting Guidelines
Exclusivity of the Recipe List:
Use only the recipes from the provided list.
No additional, personal recipes or ingredients that are not included in the list may be introduced.

Shopping List Creation:
When the user asks for a shopping list, create it based on the selected recipes from the provided list.
Combine ingredients: If an ingredient appears in multiple recipes (e.g., 1 onion in one recipe and 2 onions in another), add the quantities correctly.
Grouping of ingredients: The shopping lists should be divided into the following categories:

Fruits & Vegetables
Spices
Cans and Jars
Refrigerated Items
Miscellaneous
Formatting Guidelines for Shopping Lists:
Clear structure: Each category should appear as a heading, followed by the associated ingredients in list form.
Quantity specifications: For each ingredient, the correct total quantity and unit must be specified (e.g., "3 onions", "200g butter").
Example structure:

Fruits & Vegetables:

3 onions
2 carrots
1 head of broccoli
Spices:

Salt
Pepper
Nutmeg
Cans and Jars:

1 can of tomatoes
1 jar of corn
Refrigerated Items:

500g ground meat
200g butter
Miscellaneous:

1 pack of rice
1 bottle of oil
Single Recipe Display:
When a single recipe is requested, present the complete recipe with all details (ingredients, preparation, etc.), exactly as it appears in the provided recipe list.

Weekly Plan Creation and Adjustment:
Week start: When creating a weekly plan, the week starts on Saturday.
Initial view: Initially, only the recipe names for each day of the week should be displayed.
Every recipe can only be once in the weekly plan.
Adjustment option:
The user can then change individual days, for example, by saying: "Oh no, please select a different dish without meat for Wednesday."
In this case, the recipe for the respective day should be replaced with a suitable recipe from the provided list that meets the specified conditions (e.g., vegetarian or meat-free).
Finalization: After the weekly plan has been adjusted and the user is satisfied, a detailed shopping list based on the finally selected recipes will be created upon request.

"""
# If there is nothing useful in the context, respond with: 'Sorry, but I could not find anything related to your request.'


def gen_prompt(user_message: str, context: str) -> list:
    prompt = [
        {"role": "system",
         "content": BASE_PROPMT,
        },
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": context},
        {"role": "user",
        "content": (
            "Analyze the language of the user content and answer in the same language. "
            "For example, if the user writes in German, respond in German."
            )
        },
        {"role": "user", "content": "Please provide a helpful response or suggestion based on the above."}
    ]
    return prompt

def detailed_plan_prompt(user_message: str) -> list:
    """
    Generate the prompt messages list for the chat API using the user message
    and a collection of recipe objects.
    """
    log.debug(f"Calling detailed_plan_prompt with user_message: {user_message}")
    try:
        recipe_ids, distances = query_index_with_context(user_message, k=7)
        recipes = Recipe.objects.filter(id__in=recipe_ids)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    context_lines = ["Relevant recipes:"]
    for recipe in recipes:
        context_lines.append(f"- {recipe.title}\n")
        context_lines.append(f"  Ingredients (raw): {recipe.ingredients_raw}\n")
        context_lines.append(f"  Ingredients (structured): {recipe.ingredients_structured}\n")
        context_lines.append(f"  Instructions: {recipe.instructions}\n")
        if recipe.is_cookidoo:
            context_lines.append("  This is a cookidoo recipe.\n")
        else:
            context_lines.append("  This is not a cookidoo recipe.\n")
        if recipe.can_freeze:
            context_lines.append("  This recipe can be frozen.\n")
        else:
            context_lines.append("  This recipe cannot be frozen.")
        context_lines.append(f"  Number of People: {recipe.number_of_people}\n")
        context_lines.append(f"  Work Duration: {recipe.duration_work} minutes\n")
        context_lines.append(f"  Total Duration: {recipe.duration_total} minutes\n")
    log.debug(f"Created context with {len(recipes)} recipes")
    return gen_prompt(user_message, "\n".join(context_lines))


def planning_propmpt(user_message: str) -> list:
    """
    Generate the prompt messages list for the chat API using the user message
    and a list of recipe-titles (maybe summaries).
    """
    recipes = Recipe.objects.all()
    context_lines = ["List of recipes:"]
    for recipe in recipes:
        context_lines.append(f"- {recipe.title}\n")
        context_lines.append(f"  Instructions: {recipe.ingredients_raw}\n")
    return gen_prompt(user_message, "\n".join(context_lines))