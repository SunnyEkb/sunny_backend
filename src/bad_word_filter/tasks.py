from celery import shared_task

from comments.models import Comment
from core.utils import notify_about_moderation


@shared_task
def moderate_comment_task(comment_id: int) -> None:
    """Постановка задача по модерации комментария.

    Args:
        comment_id: идентификатор комментария
        comment_id: int

    """
    comments = Comment.objects.filter(pk=comment_id)
    if comments.exists():
        comment: Comment = comments.first()
        notify_about_moderation(comment.get_admin_url())
