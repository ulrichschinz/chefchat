from django.core.management.base import BaseCommand
from recipes.models import Recipe
from recipes.vector.index import build_faiss_index, save_index_with_mapping

class Command(BaseCommand):
    help = 'Rebuild FAISS index from all recipes'

    def handle(self, *args, **options):
        recipes = Recipe.objects.all()
        if not recipes:
            self.stdout.write(self.style.WARNING('No recipes found.'))
            return

        index, mapping = build_faiss_index(recipes)
        save_index_with_mapping(index, mapping)
        self.stdout.write(self.style.SUCCESS('FAISS index rebuilt and saved.'))
