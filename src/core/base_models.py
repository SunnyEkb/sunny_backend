import sys

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db import models, transaction

from core.abstract_models import TimeCreateUpdateModel
from core.choices import AdvertisementStatus
from core.enums import Limits
from comments.models import Comment
from services.tasks import delete_images_dir_task, notify_about_moderation_task
from users.models import Favorites

User = get_user_model()


class AbstractAdvertisement(TimeCreateUpdateModel):
    """Абстрактная модель объявления."""

    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
    )
    title = models.CharField(
        "Название", max_length=Limits.MAX_LENGTH_ADVMNT_TITLE
    )
    description = models.TextField(
        "Описание", max_length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION
    )
    status = models.IntegerField(
        "Статус",
        choices=AdvertisementStatus.choices,
        default=AdvertisementStatus.DRAFT,
    )
    address = models.CharField(
        "Адрес",
        max_length=Limits.MAX_LENGTH_SERVICE_ADDRESS,
        null=True,
        blank=True,
    )
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    def hide(self) -> None:
        """Изменить статус на \"Скрыто\"."""

        if self.status == AdvertisementStatus.PUBLISHED:
            with transaction.atomic():
                Favorites.clear_favorites(self)
                self.status = AdvertisementStatus.HIDDEN
                self.save()

    def publish(self, request) -> None:
        """
        Опубликовать услугу или объявление.

        Если текущий статус объявления - \"Черновик\", то статус меняется на \
            \"На модерации\".
        Если статус объявления - \"Скрыто\", то на \"Опубликовано\"

        :request: http запрос
        """

        if self.status == AdvertisementStatus.HIDDEN:
            self.status = AdvertisementStatus.PUBLISHED
            self.save()
        if self.status == AdvertisementStatus.DRAFT:
            self.status = AdvertisementStatus.MODERATION
            self.save()
            url = self.get_admin_url(request)
            if "test" not in sys.argv:
                notify_about_moderation_task.delay(url)

    def set_draft(self):
        """Изменить статус на \"Черновик\"."""

        with transaction.atomic():
            self.status = AdvertisementStatus.DRAFT
            Favorites.clear_favorites(self)
            self.save()

    def approve(self) -> None:
        """
        Подтверлить публикацию.

        Изменить статус на \"Опубликовано\".
        """

        if self.status == AdvertisementStatus.MODERATION:
            self.status = AdvertisementStatus.PUBLISHED
            self.save()

    def reject(self) -> None:
        """
        Отказать в публикации.

        Изменить статус на \"Черновик\".
        """

        if self.status == AdvertisementStatus.MODERATION:
            self.status = AdvertisementStatus.DRAFT
            self.save()

    def get_admin_url(self, request) -> str:
        """Возвращает ссылку на экземпляр модели в админке."""

        domain = get_current_site(request).domain
        app_name = self._meta.app_label
        name: str = self.__class__.__name__.lower()
        return "".join(
            ["https://", domain, f"/admin/{app_name}/{name}/{self.id}/change/"]
        )

    def delete_images(self):
        """Удаление файлов с фото."""

        images = self.images.all()
        name: str = self.__class__.__name__.lower()
        if images:
            for image in images:
                image.delete()
            delete_images_dir_task.delay(f"{name}/{self.id}")
