from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings

from recipes.models import (Ingredient, IngredientRecipe, Recipe, Shopping,
                            Tag, TagRecipe)
from users.models import Follow, User

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'password',
        )


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Провоеряем подписанны пользователи.
        """
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class FollowShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для короткой модели рецепта
    для избранных рецептов в подписках.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода подписок у авторов.
    """
    recipes = serializers.SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())
        return FollowShortRecipeSerializer(
            recipes,
            many=True).data

    def validate(self, data):
        request = self.context['request']
        author = self.initial_data['author']
        if request.user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя.'}
            )
        if request.user.follower.filter(author=author).exists():
            raise serializers.ValidationError({'errors': 'Есть подписка.'})
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return obj.following.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тэгов.
    """
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов и рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы и просмотра рецепта """
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, )
    ingredients = SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()


class TagRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализтор для вывода тэгов в рецепте.
    """

    class Meta:
        model = TagRecipe
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "name", "color", "slug",)

    def to_internal_value(self, data):
        if isinstance(data, int):
            return get_object_or_404(Tag, pk=data)
        return data


class RecipeAddSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецептов.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления еды не меньше одной минуты'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        """
        Проверка ингредиентов.
        """
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингридиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
        return ingredients

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError('Тег отсутствует')
        return tags

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient_list.append(
                IngredientRecipe(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)

    @staticmethod
    def add_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if IngredientRecipe.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            IngredientRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        request = self.context.get('request', None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)

        self.create_ingredients(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShortRecipeShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения сведений о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    """
    Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = ShortRecipeShoppingSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = int(self.context['request'].GET.get(
            'recipes_limit', api_settings.PAGE_SIZE))

        user = get_object_or_404(User, pk=obj.pk)
        recipes = Recipe.objects.filter(author=user)[:recipes_limit]

        return ShortRecipeShoppingSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False

        return Follow.objects.filter(
            author=obj, user=self.context['request'].user).exists()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes')
        model = User


class ShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок """

    class Meta:
        model = Shopping
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if Shopping.objects.filter(user=user,
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeShoppingSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
