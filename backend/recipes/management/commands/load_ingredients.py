import csv
import os

from django.core.management import BaseCommand

from recipes.models import Ingredient

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))


class Command(BaseCommand):
    """Команда для загрузки ингредиентов."""

    def handle(self, *args, **kwargs):
        try:
            with open(
                f'{PROJECT_PATH}/../data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as file:
                reader = csv.reader(file)
                Ingredient.objects.bulk_create(
                    Ingredient(
                        name=line[0],
                        measurement_unit=line[1]
                    ) for line in reader
                )
        except Exception as error:
            self.stdout.write(self.style.ERROR(error))
        else:
            self.stdout.write(self.style.SUCCESS('Ингредиенты загружены.'))
