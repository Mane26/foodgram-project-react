from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешения для администратора.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Полный доступ предоставляется только автору объекта и
    суперпользователю Джанго.
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_active)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
