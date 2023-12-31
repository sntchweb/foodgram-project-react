from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = NumberFilter(field_name='author__id')
    is_favorited = NumberFilter(method='is_favorited_filter')
    is_in_shopping_cart = NumberFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def is_favorited_filter(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(shop_cart__user=self.request.user)
