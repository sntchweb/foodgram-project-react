import csv
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            with open(
                'G:\\Dev\\foodgram-project-react\\data\\ingredients.csv',
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
            print(error)
        else:
            print('Загрузка данных в таблицу завершена успешно.')
