from django.contrib import admin

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, TagsRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}


class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'recipe_added_to_favorite'
    )
    search_fields = ('id', 'name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientRecipeInline,)

    def recipe_added_to_favorite(self, obj):
        return obj.favorites.count()
    recipe_added_to_favorite.short_description = 'Добавлен в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(TagsRecipe)
class TagsRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
