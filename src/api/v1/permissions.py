from rest_framework.permissions import BasePermission, SAFE_METHODS


class SelfOnly(BasePermission):
    """
    Редактирование данных только о себе.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class OwnerOrReadOnly(BasePermission):
    """
    Редактирование только своих услуг.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.provider == request.user


class ReadOnly(BasePermission):
    """
    Разрешения на просмотр услуги незарегистрированному пользователю.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
