from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeAddSerializer,
                             RecipeReadSerializer,
                             ShortRecipeShoppingSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping, Tag)
from users.models import Follow, User

User = get_user_model()
now = timezone.now()


class TagViewSet(ModelViewSet):
    """Вывод тегов."""
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вывод ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вывод рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeAddSerializer


class RecipeShoppingViewSet(ModelViewSet):
    """
    Вывод наличия рецептов в корзине.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeAddSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Shopping, request.user, pk)
        else:
            return self.delete_from(Shopping, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeShoppingSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)


class DownloadShoppingCartView(views.APIView):
    def get(self, request):
        items = IngredientRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session['purchases']
            )

        items = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename{filename}'

        return response


class UserViewSet(UserViewSet):
    """Вывод пользователей."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save(password=self.request.data['password'])

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        return self._set_status_favorite(
            request,
            User,
            Follow,
            SubscribeSerializer
        )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получить подписки пользователя."""

        queryset = request.user.follower.filter(user=request.user.id)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
