from rest_framework import serializers
from django.conf import settings
from .models import Category, Tag, Post, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), required=False)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Post
        fields = ("id", "title", "slug", "author", "excerpt", "content", "cover_image", "status", "published_at", "categories", "tags", "created_at")
        read_only_fields = ("id", "slug", "author", "created_at")


class PostDetailSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("content",)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "parent", "content", "status", "created_at")
        read_only_fields = ("id", "author", "status", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["author"] = request.user
        # auto-pend unless auto-approve flag is set
        from django.conf import settings
        if getattr(settings, "AUTO_APPROVE_COMMENTS", False):
            validated_data["status"] = Comment.Status.APPROVED
        return super().create(validated_data)


