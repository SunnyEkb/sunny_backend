from rest_framework.permissions import SAFE_METHODS, BasePermission

from ads.models import AdImage
from core.choices import AdvertisementStatus
from services.models import ServiceImage


class SelfOnly(BasePermission):
    """Редактирование данных только о себе."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class OwnerOrReadOnly(BasePermission):
    """Редактирование только своих услуг и объявлений."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.provider == request.user


class PhotoOwnerOrReadOnly(BasePermission):
    """Редактирование только фото своих услуг."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, ServiceImage):
            return obj.service.provider == request.user
        if isinstance(obj, AdImage):
            return obj.ad.provider == request.user
        return False


class PhotoReadOnly(BasePermission):
    """Разрешение на просмотр фото услуги или объявления
    незарегистрированному пользователю.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, ServiceImage):
            return obj.service.status == AdvertisementStatus.PUBLISHED
        if isinstance(obj, AdImage):
            return obj.ad.status == AdvertisementStatus.PUBLISHED
        return False


class ReadOnly(BasePermission):
    """Разрешение на просмотр услуги или объявления
    незарегистрированному пользователю.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (
            obj.provider == request.user or obj.status == AdvertisementStatus.PUBLISHED
        )


class CommentAuthorOnly(BasePermission):
    """Разрешения на удаление комментария автору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ModeratorOnly(BasePermission):
    """Разрешения на совершение действий только модератору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator

    def has_object_permission(self, request, view, obj):
        return request.user.is_moderator


class NotificationRecieverOnly(BasePermission):
    """Только получатель уведомления."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.receiver == request.user
