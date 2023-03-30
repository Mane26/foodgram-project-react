from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Настройка раздела пользователей."""

    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'first_name')
    search_fields = ('username', 'email')
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    list_filter = ('user', 'author')
    search_fields = ('author',)
    empty_value_display = settings.EMPTY_VALUE
