import logging
from django.core.management.base import BaseCommand
from recipes.models import Recipe,RecipesSnapshot
from recipes.vector.index import rebuild_index

log = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Build Qdrant index for recipes'

    def handle(self, *args, **kwargs):
        rebuild_index()
        self.stdout.write(self.style.SUCCESS('Successfully built and saved Qdrant chefchat index for all users'))