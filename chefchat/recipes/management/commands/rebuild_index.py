from django.core.management.base import BaseCommand
from recipes.models import Recipe
from recipes.vector.index import build_faiss_index, save_index

class Command(BaseCommand):
    help = 'Rebuild FAISS index from all recipes'

    def handle(self, *args, **options):
        recipes = Recipe.objects.all()
        if not recipes:
            self.stdout.write(self.style.WARNING('No recipes found.'))
            return

        index = build_faiss_index(recipes)
        save_index(index, "faiss_index.index")
        self.stdout.write(self.style.SUCCESS('FAISS index rebuilt and saved.'))
