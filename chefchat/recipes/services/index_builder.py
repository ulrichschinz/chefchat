import logging
from recipes.models import Recipe,RecipesSnapshot

log = logging.getLogger(__name__)

def build_index_items(user):
    
    # Fetch all recipes from the database
    recipes = Recipe.objects.filter(user=user)

    # Prepare the data
    items = []
    snapshot = []
    for recipe in recipes:
        items.append({
            'id': recipe.id,
            'title': recipe.title,
            'content': f"{recipe.ingredients_raw}\n{recipe.ingredients_structured}\n{recipe.instructions}\n",
            'type': 'recipe',
            'additional_info': {
                'ingredients_raw': recipe.ingredients_raw,
                'ingredients_structured': recipe.ingredients_structured,
                'instructions': recipe.instructions,
                'durationtotal': {recipe.duration_total},
                'durationwork': {recipe.duration_work},
                'cookidoo': {recipe.is_cookidoo},
                'freeze': {recipe.can_freeze}
            }
        })
        snapshot.append({
            'title': recipe.title,
            'content': f"{recipe.ingredients_raw}",
        })

    log.debug(f"snapshot: {snapshot}")
    recipes_snapshot = RecipesSnapshot.objects.create(
        user=user,
        snapshot=snapshot
    )

    log.debug(f"Recipes snapshot created: {recipes_snapshot}")

    items.append({
        'id': recipes_snapshot.id,
        'title': f"{recipes_snapshot.timestamp} - List of Recipes - Recipes Snapshot - Recipes Shortlist",
        'content': f"{recipes_snapshot.snapshot}",
        'type': 'recipes_snapshot',
        'additional_info': {
            'snapshot': recipes_snapshot.snapshot
        }
    })
    return items