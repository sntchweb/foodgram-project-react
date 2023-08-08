from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from api.serializers import (CreateRecipeSerializer, FavoriteRecipeSerializer,
                             IngredientSerializer, ReadRecipeSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserSerializer)
from api.utils import CustomPagination
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, User)
from users.models import Subscription


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        url_path='favorite',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            favorite_obj, created = FavoriteRecipe.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                serializer = FavoriteRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(serializer.data, status=HTTP_201_CREATED)
            return Response(
                'Рецепт уже в избранном', status=HTTP_400_BAD_REQUEST
            )
        favorite_obj = FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        )
        if not favorite_obj.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        favorite_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        url_path='shopping_cart',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            shopping_cart_obj, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                serializer = FavoriteRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(serializer.data, status=HTTP_201_CREATED)
            return Response(
                'Рецепт уже в корзине', status=HTTP_400_BAD_REQUEST
            )
        shopping_cart_obj = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        )
        if not shopping_cart_obj.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        shopping_cart_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shop_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))
        wishlist = ''
        for ingredient in ingredients:
            wishlist += f'{ingredient["ingredient__name"]}: {ingredient["total_sum"]}'
            wishlist += f'{ingredient["ingredient__measurement_unit"]}.\n'
        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=wishlist.txt'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # permission_classes = (AllowAny,)

    @action(
        methods=('get',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subs_quryset = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subs_quryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
            methods=('post', 'delete'),
            url_path='subscribe',
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        follow_obj = Subscription.objects.filter(
            user=request.user, author=get_object_or_404(User, pk=id)
        )
        if request.method == 'DELETE':
            follow_obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        if not follow_obj.exists():
            sub = Subscription.objects.create(
                user=request.user,
                author=get_object_or_404(User, pk=id)
            )
            serializer = SubscribeSerializer(sub, context={'request': request})
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(
                'На одного пользователя нельзя подписаться дважды!',
                status=HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name').lower()
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset