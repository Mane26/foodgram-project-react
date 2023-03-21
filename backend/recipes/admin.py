from django.contrib import admin
from django.contrib.admin import display

from .models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """Настройки раздела избранное"""

    list_display = ('user', 'recipe',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка раздела Recipe"""

    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('favorite_count', 'shoppingcart_count')
    list_filter = ('author', 'name', 'tags',)

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки раздела тегов"""

    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Настройка раздела ингредиентов в классе RecipeAdmin.
    """

    search_fields = ('name',)
    list_display = ('name', 'measurement_unit')    


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    """Настройки соответствия ингредиентов и рецепта"""

    list_display = ('ingredient', 'recipe', 'amount',)