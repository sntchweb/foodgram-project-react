from django.db.models import (CASCADE, CharField, DateTimeField,
                              ForeignKey, ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User

MIN_VALUE = 1
MAX_VALUE = 32_000


class Tag(Model):
    """Модель тегов."""

    name = CharField(
        verbose_name='Тег',
        max_length=200,
        unique=True,
    )
    color = CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
    )
    slug = SlugField(
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(Model):
    """Модель ингредиентов."""

    name = CharField(
        verbose_name='Название ингридиента',
        max_length=200
    )
    measurement_unit = CharField(
        verbose_name='Единица измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(Model):
    """Модель рецептов."""

    author = ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=CASCADE,
        related_name='recipes'
    )
    name = CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
    )
    description = TextField(
        verbose_name='Описание рецепта',
    )
    ingredient = ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe',
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='Тег',
        through='TagsRecipe',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Время готовки не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Время готовки не может быть больше 32 000 минут'
            )
        ]
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(
                fields=['author', 'name'],
                name='unique_recipe_by_author'
            )
        ]

    def __str__(self) -> str:
        return self.name


class FavoriteRecipe(Model):
    """Модель избранных рецептов."""

    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe}'


class ShoppingCart(Model):
    """Модель списка покупок."""

    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=CASCADE,
        related_name='shop_cart'
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='shop_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('recipe_id',)

    def __str__(self) -> str:
        return f'{self.recipe}'


class TagsRecipe(Model):
    """Промежуточная модель для связи тегов и рецептов."""

    tag = ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ('recipe__name',)

    def __str__(self) -> str:
        return f'{self.tag}'


class IngredientRecipe(Model):
    """Промежуточная модель для связи ингредиентов и рецептов."""

    ingredient = ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=CASCADE,
        related_name='ingredient'
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='recipe'
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Количество ингредиентов не может быть меньше 1'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Количество ингредиентов не может быть больше 32 000'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        ordering = ('ingredient__name',)

    def __str__(self) -> str:
        return f'{self.ingredient} в {self.recipe}: {self.amount}'
