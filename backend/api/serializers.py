from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):

        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SetPasswordSerializer(ModelSerializer):
    current_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class TagSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    text = CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'cooking_time', 'text'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        if not data.get('tags'):
            raise ValidationError(
                'Количество тегов не может быть меньше одного!'
            )
        if data.get('cooking_time') < 1:
            raise ValidationError(
                'Время приготовления блюда не может быть меньше 1 минуты!'
            )
        for ingredient in data.get('ingredients'):
            if ingredient.get('amount') < 1:
                raise ValidationError(
                    'Количество ингридиентов не может быть меньше одного!'
                )
        return data

    def create(self, validated_data):
        tags = validated_data.get('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            name=validated_data.get('name'),
            image=validated_data.get('image'),
            description=validated_data.get('description'),
            cooking_time=validated_data.get('cooking_time')
        )
        recipe.save()
        for ingredient in validated_data.get('ingredients'):
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ).save()
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        # user = self.context.get('request').user
        instance.name = validated_data.get('name')
        instance.image = validated_data.get('image')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        for ingredient in validated_data.get('ingredients'):
            IngredientRecipe.objects.filter(
                recipe=instance,
                ingredient=ingredient.get('id')
            ).update(amount=ingredient.get('amount'))
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data


class ReadIngredientRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('amount',)


class ReadRecipeSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = ReadIngredientRecipeSerializer(
        many=True, read_only=True, source='recipe'
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    text = CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return FavoriteRecipe.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()


class FavoriteRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(ModelSerializer):
    author = UserSerializer()
    recipes = FavoriteRecipeSerializer(
        many=True, source='author.recipes', read_only=True
    )
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('author', 'recipes', 'recipes_count')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя!'
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('author'):
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # breakpoint()
        return {
            'email': data['author']['email'],
            'id': data['author']['id'],
            'username': data['author']['username'],
            'first_name': data['author']['first_name'],
            'last_name': data['author']['last_name'],
            'is_subscribed': data['author']['is_subscribed'],
            'recipes': data['recipes'],
            'recipes_count': data['recipes_count'],
        }
