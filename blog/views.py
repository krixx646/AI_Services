from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, PostDetailSerializer, CommentSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return super().get_permissions()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return super().get_permissions()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("categories", "tags").all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["author", "status", "categories", "tags"]
    search_fields = ["title", "content", "tags__name", "categories__name"]
    ordering_fields = ["published_at", "created_at"]

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET" and self.action == "list":
            # Public should see only published posts
            return qs.filter(status=Post.Status.PUBLISHED)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        post = self.get_object()
        user = self.request.user
        if not (user.is_staff or post.author_id == user.id):
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        user = self.request.user
        if not (user.is_staff or post.author_id == user.id):
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class PostCommentsView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id: int):
        status_filter = request.query_params.get("status", "approved")
        post = get_object_or_404(Post, pk=post_id)
        qs = Comment.objects.filter(post=post)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(CommentSerializer(qs.order_by("created_at"), many=True).data)

    def post(self, request, post_id: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        post = get_object_or_404(Post, pk=post_id)
        data = {**request.data, "post": post.id}
        serializer = CommentSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(CommentSerializer(obj).data, status=status.HTTP_201_CREATED)


class CommentModerateView(views.APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, comment_id: int):
        action = request.data.get("action")  # "approve" or "reject"
        comment = get_object_or_404(Comment, pk=comment_id)
        if action == "approve":
            comment.status = Comment.Status.APPROVED
        elif action == "reject":
            comment.status = Comment.Status.REJECTED
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        comment.save(update_fields=["status"])
        return Response({"status": comment.status})

