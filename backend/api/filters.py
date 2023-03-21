from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


filter_user = {'favorites': 'favorites__user',
               'shop_list': 'shop_list__user'}


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def _get_queryset(self, queryset, name, value, model):
        if value:
            return queryset.filter(**{filter_user[model]: self.request.user})
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._get_queryset(queryset, name, value, 'favorites')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._get_queryset(queryset, name, value, 'shop_list')


class IngredientFilter(FilterSet):
    """Поиск по названию ингредиента."""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']