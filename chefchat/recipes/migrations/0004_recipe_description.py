# Generated by Django 5.1.6 on 2025-03-04 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_qdrantmapping_recipe_user_recipessnapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='description',
            field=models.TextField(help_text='Short description of the recipe', null=True),
        ),
    ]
