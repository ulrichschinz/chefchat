from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from recipes.models import Recipe
from recipes.vector.index import rebuild_index

@receiver(post_save, sender=Recipe)
def update_index_on_save(sender, instance, **kwargs):
    # For simplicity, rebuild the entire index on each save.
    rebuild_index()

@receiver(post_delete, sender=Recipe)
def update_index_on_delete(sender, instance, **kwargs):
    # Rebuild the index when a recipe is deleted.
    rebuild_index()
