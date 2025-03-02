from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from recipes.models import Recipe
from recipes.services.index_builder import build_index_items
from recipes.vector.index import build_qdrant_index

def rebuild_index():
    items = build_index_items()

    if items.exists():
        build_qdrant_index(items)
        print("Qdrant index rebuilt.")
    else:
        print("No items to index, index not rebuilt.")

@receiver(post_save, sender=Recipe)
def update_index_on_save(sender, instance, **kwargs):
    # For simplicity, rebuild the entire index on each save.
    rebuild_index()

@receiver(post_delete, sender=Recipe)
def update_index_on_delete(sender, instance, **kwargs):
    # Rebuild the index when a recipe is deleted.
    rebuild_index()
