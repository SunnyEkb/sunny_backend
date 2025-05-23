from bad_word_filter.bad_word_filter import bad_words_filter

from celery import shared_task
from rest_framework.request import Request

from comments.models import Comment
from core.choices import SystemMessages
from core.utils import notify_about_moderation
from notifications.models import Notification


@shared_task
def moderate_comment_task(comment_id: int, request: Request) -> None:
    """
    Постановка задача по модерации комментария.

    :param comment_id: идентификатор комментария
    :param request: экземпляр объекта запроса
    """

    comment = Comment.objects.filter(pk=comment_id)
    if comment.exists():
        comment: Comment = comment.first()
        if len(bad_words_filter(comment.feedback)) > 0:
            Notification.objects.create(
                receiver=comment.author,
                text=SystemMessages.AUTOMATIC_COMMENT_MODERATION_FAILED.value,
            )
        else:
            notify_about_moderation(comment.get_admin_url(request))
