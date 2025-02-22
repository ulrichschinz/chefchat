from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Recipe
from .vector.index import build_faiss_index, save_index
from django.conf import settings

def rebuild_index():
    recipes = Recipe.objects.all()
    if recipes.exists():
        index = build_faiss_index(recipes)
        save_index(index, "faiss_index.index")
        print("FAISS index rebuilt.")
    else:
        print("No recipes found, index not rebuilt.")

@receiver(post_save, sender=Recipe)
def update_index_on_save(sender, instance, **kwargs):
    # For simplicity, rebuild the entire index on each save.
    rebuild_index()

@receiver(post_delete, sender=Recipe)
def update_index_on_delete(sender, instance, **kwargs):
    # Rebuild the index when a recipe is deleted.
    rebuild_index()
