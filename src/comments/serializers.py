from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.v1.validators import validate_file_size
from comments.models import Comment, CommentImage
from core.choices import APIResponses
from users.serializers import UserReadSerializer


class CommentImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к комментарию."""

    image = serializers.ImageField(
        required=True,
        allow_null=False,
        validators=[validate_file_size],
    )

    class Meta:
        model = CommentImage
        fields = ("image",)


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        fields = CommentImageCreateSerializer.Meta.fields + ("id",)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    class Meta:
        model = Comment
        fields = (
            "content_type",
            "object_id",
            "rating",
            "feedback",
        )

    def validate(self, data):
        object_id = data.get("object_id", None)
        content_type = data.get("content_type", None)
        user = self.context.get("request").user
        cont_type_model = get_object_or_404(ContentType, pk=content_type.id)
        obj = get_object_or_404(cont_type_model.model_class(), pk=object_id)
        if obj.provider == user:
            raise serializers.ValidationError(
                APIResponses.COMMENTS_BY_PROVIDER_PROHIBITED.value
            )
        if Comment.cstm_mng.filter(
            author=user,
            content_type=content_type,
            object_id=object_id,
        ).exists():
            raise serializers.ValidationError(
                APIResponses.COMMENT_ALREADY_EXISTS.value
            )
        return data

    def create(self, validated_data):
        self.validate(validated_data)
        object_id = validated_data.pop("object_id")
        content_type = validated_data.pop("content_type")
        cont_type_model = get_object_or_404(ContentType, pk=content_type.id)
        obj = get_object_or_404(cont_type_model.model_class(), pk=object_id)
        comment = Comment.objects.create(
            content_type=cont_type_model, object_id=obj.id, **validated_data
        )
        return comment


class CommentReadSerializer(CommentCreateSerializer):
    """Сериализатор для чтения комментария."""

    author = UserReadSerializer(read_only=True)
    images = CommentImageRetrieveSerializer(many=True, read_only=True)

    class Meta(CommentCreateSerializer.Meta):
        fields = CommentCreateSerializer.Meta.fields + (
            "id",
            "author",
            "images",
        )
