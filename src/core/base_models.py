
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db import models

from core.abstract_models import TimeCreateUpdateModel
from core.choices import AdvertisementStatus
from core.enums import Limits
from comments.models import Comment

User = get_user_model()


class AbstractAdvertisement(TimeCreateUpdateModel):
    """Абстрактная модель объявления."""

    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
    )
    title = models.CharField(
        "Название", max_length=Limits.MAX_LENGTH_ADVMNT_TITLE.value
    )
    description = models.TextField(
        "Описание", max_length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION.value
    )
    status = models.IntegerField(
        "Статус",
        choices=AdvertisementStatus.choices,
        default=AdvertisementStatus.DRAFT.value,
    )
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    def hide(self) -> None:
        if self.status == AdvertisementStatus.PUBLISHED.value:
            self.status = AdvertisementStatus.HIDDEN.value
            self.save()

    def send_to_moderation(self) -> None:
        if not self.status == AdvertisementStatus.CANCELLED.value:
            self.status = AdvertisementStatus.MODERATION.value
            self.save()

    def publish(self) -> None:
        if self.status == AdvertisementStatus.HIDDEN.value:
            self.status = AdvertisementStatus.PUBLISHED.value
            self.save()

    def cancell(self) -> None:
        if not self.status == AdvertisementStatus.DRAFT.value:
            self.status = AdvertisementStatus.CANCELLED.value
            self.save()

    def set_changed(self):
        if self.status in [
            AdvertisementStatus.PUBLISHED.value,
            AdvertisementStatus.HIDDEN.value,
        ]:
            self.status = AdvertisementStatus.CHANGED.value
            self.save()

    def moderate(self) -> None:
        if self.status == AdvertisementStatus.MODERATION:
            self.status = AdvertisementStatus.PUBLISHED.value
            self.save()

    def refusal_to_publish(self) -> None:
        if self.status == AdvertisementStatus.MODERATION:
            self.status = AdvertisementStatus.DRAFT.value
            self.save()

    def get_admin_url(self, request) -> str:
        """Возвращает ссылку на экземпляр модели в админке."""

        domain = get_current_site(request).domain
        app_name = self._meta.app_label
        name: str = self.__class__.__name__.lower()
        return "".join(
            ["https://", domain, f"/admin/{app_name}/{name}/{self.id}/change/"]
        )
