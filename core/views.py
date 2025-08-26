from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class SearchView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        scope = (request.query_params.get("type", "").strip() or "all").lower()
        if not query:
            return Response({"detail": "q is required"}, status=status.HTTP_400_BAD_REQUEST)

        results = {}

        if scope in ("all", "posts"):
            try:
                from blog.models import Post

                posts_qs = (
                    Post.objects.filter(status=Post.Status.PUBLISHED)
                    .filter(
                        models.Q(title__icontains=query)
                        | models.Q(content__icontains=query)
                        | models.Q(tags__name__icontains=query)
                        | models.Q(categories__name__icontains=query)
                    )
                    .distinct()
                )[:10]
                results["posts"] = [
                    {"id": p.id, "title": p.title, "slug": p.slug, "published_at": p.published_at}
                    for p in posts_qs
                ]
            except Exception:
                results["posts"] = []

        if scope in ("all", "bots"):
            try:
                from bots.models import Question

                qs = Question.objects.filter(text__icontains=query).select_related("bot")[:10]
                results["bots"] = [
                    {
                        "bot_reference": str(q.bot.reference),
                        "question_id": q.id,
                        "question": q.text,
                    }
                    for q in qs
                ]
            except Exception:
                results["bots"] = []

        if scope in ("all", "reviews"):
            try:
                from bots.models import Review

                rv = Review.objects.filter(comment__icontains=query).select_related("bot")[:10]
                results["reviews"] = [
                    {
                        "id": r.id,
                        "bot_id": r.bot_id,
                        "rating": r.rating,
                        "comment": r.comment,
                    }
                    for r in rv
                ]
            except Exception:
                results["reviews"] = []

        return Response({"q": query, "type": scope, "results": results})


