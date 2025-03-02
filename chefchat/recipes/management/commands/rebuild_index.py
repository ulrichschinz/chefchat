import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe,RecipesSnapshot
from recipes.vector.index import build_qdrant_index
from recipes.services.index_builder import build_index_items

log = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Build Qdrant index for recipes'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        all_users = User.objects.all()
        for user in all_users:
            items = build_index_items(user)
            log.debug(f"Items: {items}")
            build_qdrant_index(user.id, items, text_fields=['title', 'content'], id_field='id')

        self.stdout.write(self.style.SUCCESS('Successfully built and saved Qdrant chefchat index for all users'))