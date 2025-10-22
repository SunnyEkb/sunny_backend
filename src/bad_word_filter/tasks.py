from bad_word_filter.bad_word_filter import bad_words_filter

from celery import shared_task

from comments.models import Comment
from core.choices import SystemMessages
from core.utils import notify_about_moderation
from notifications.models import Notification


@shared_task
def moderate_comment_task(comment_id: int) -> None:
    """
    Постановка задача по модерации комментария.

    :param comment_id: идентификатор комментария
    :type comment_id: int
    """

    comments = Comment.objects.filter(pk=comment_id)
    if comments.exists():
        comment: Comment = comments.first()
        if len(bad_words_filter(comment.feedback)) > 0:
            Notification.objects.create(
                receiver=comment.author,
                text=SystemMessages.AUTOMATIC_COMMENT_MODERATION_FAILED,
            )
        else:
            notify_about_moderation(comment.get_admin_url())
