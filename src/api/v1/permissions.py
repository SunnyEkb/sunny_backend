from rest_framework.permissions import BasePermission


class SelfOnly(BasePermission):
    """
    Редактирование данных только о себе.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user
