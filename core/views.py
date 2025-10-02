from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import models
from django.views.generic import TemplateView
from django.conf import settings


class SearchView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Cache simple search results for 60s based on q and type
        try:
            from django.core.cache import cache
            q = request.GET.get("q", "").strip()
            t = (request.GET.get("type", "all").strip() or "all").lower()
            cache_key = f"search:{t}:{q}"
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)
        except Exception:
            cache = None
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

        payload = {"q": query, "type": scope, "results": results}
        try:
            if cache and query:
                cache.set(cache_key, payload, 60)
        except Exception:
            pass
        return Response(payload)


# Site views
class PricingPageView(TemplateView):
    template_name = "pricing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        allowed = getattr(settings, "PAYSTACK_ALLOWED_CURRENCIES", ["NGN"]) or []

        # Infer country (very lightweight): Cloudflare header or generic 'X-Country', then Accept-Language
        request = self.request
        country = (request.META.get("HTTP_CF_IPCOUNTRY") or request.META.get("HTTP_X_COUNTRY") or "").strip().upper()
        if not country:
            al = (request.META.get("HTTP_ACCEPT_LANGUAGE") or "").lower()
            # Any locale ending with -ng (e.g., en-NG)
            if "-ng" in al:
                country = "NG"

        # Gate: Nigerians → NGN only; others → USD only (if allowed)
        show_ngn = ("NGN" in allowed) and (country == "NG" or "USD" not in allowed)
        show_usd = ("USD" in allowed) and (country != "NG")
        # Fallbacks to ensure at least one is visible
        if not show_ngn and not show_usd:
            show_ngn = "NGN" in allowed
        gated_currency = "NGN" if show_ngn else ("USD" if show_usd else "NGN")

        ctx["SHOW_NGN"] = show_ngn
        ctx["SHOW_USD"] = show_usd
        ctx["GATED_CURRENCY"] = gated_currency
        return ctx

