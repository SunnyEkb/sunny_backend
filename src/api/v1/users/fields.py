from rest_framework import serializers

from comments.models import Comment
from comments.serializers import CommentImageRetrieveSerializer
from core.choices import SystemMessages


class FavoriteObjectRelatedField(serializers.RelatedField):
    """
    Поле для вывода объектов избранного.
    """

    def to_representation(self, value):
        if isinstance(value, Comment):
            serializer = CommentImageRetrieveSerializer(value)
        else:
            raise Exception(SystemMessages.SERIALIZER_NOT_FOUND_ERROR.value)
        return serializer.data
