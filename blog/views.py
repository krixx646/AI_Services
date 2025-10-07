from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, PostDetailSerializer, CommentSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponseBadRequest
import os
from django.utils import timezone
from django.http import HttpResponseForbidden
from payments.models import BotInstance, PaymentTransaction

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

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

    @action(detail=False, methods=["get"], url_path=r"by-slug/(?P<slug>[^/.]+)")
    def by_slug(self, request, slug=None):
        obj = get_object_or_404(Post, slug=slug)
        if obj.status != Post.Status.PUBLISHED and not (request.user.is_staff or (request.user.is_authenticated and obj.author_id == request.user.id)):
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


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


class CommentDetailView(views.APIView):
    def get_object(self, request, comment_id: int):
        comment = get_object_or_404(Comment, pk=comment_id)
        user = request.user
        if not (user.is_authenticated and (user.is_staff or (comment.author_id == user.id))):
            return None
        return comment

    def get(self, request, comment_id: int):
        comment = self.get_object(request, comment_id)
        if not comment:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return Response(CommentSerializer(comment).data)

    def patch(self, request, comment_id: int):
        comment = self.get_object(request, comment_id)
        if not comment:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, comment_id: int):
        comment = self.get_object(request, comment_id)
        if not comment:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostEditorView(View):
    @method_decorator(login_required)
    def get(self, request, post_id: int = None):
        from .models import Category, Tag
        ctx = {
            "post": None,
            "form": {},
            "categories": Category.objects.all(),
            "tags": Tag.objects.all(),
            "selected_category_ids": [],
            "selected_tag_ids": [],
        }
        if post_id:
            obj = get_object_or_404(Post, pk=post_id)
            if not (request.user.is_staff or obj.author_id == request.user.id):
                return redirect("blog_list")
            ctx["post"] = obj
            ctx["selected_category_ids"] = list(obj.categories.values_list("id", flat=True))
            ctx["selected_tag_ids"] = list(obj.tags.values_list("id", flat=True))
        return render(request, "blog/editor.html", ctx)

    @method_decorator(login_required)
    def post(self, request, post_id: int = None):
        # Create or update via API serializer to reuse validation
        data = {
            "title": request.POST.get("title", "").strip(),
            "content": request.POST.get("content", "").strip(),
            "status": request.POST.get("status", "draft").strip() or "draft",
            "excerpt": request.POST.get("excerpt", "").strip(),
        }
        # Many-to-many selections
        category_ids = [int(x) for x in request.POST.getlist("categories") if x.isdigit()]
        tag_ids = [int(x) for x in request.POST.getlist("tags") if x.isdigit()]
        if category_ids:
            data["categories"] = category_ids
        if tag_ids:
            data["tags"] = tag_ids
        files = {}
        if request.FILES.get("cover_image"):
            files["cover_image"] = request.FILES["cover_image"]
        if post_id:
            obj = get_object_or_404(Post, pk=post_id)
            if not (request.user.is_staff or obj.author_id == request.user.id):
                return redirect("blog_list")
            ser = PostSerializer(obj, data=data, partial=True, context={"request": request})
        else:
            ser = PostSerializer(data=data, context={"request": request})
        if ser.is_valid():
            saved = ser.save(author=request.user)
            # Auto-set published_at when status is published
            if saved.status == Post.Status.PUBLISHED and not saved.published_at:
                saved.published_at = timezone.now()
                saved.save(update_fields=["published_at"])
            if files.get("cover_image"):
                saved.cover_image = files["cover_image"]
                saved.save(update_fields=["cover_image"])
            return redirect("blog_detail", slug=saved.slug)
        from .models import Category, Tag
        return render(
            request,
            "blog/editor.html",
            {
                "post": None,
                "errors": ser.errors,
                "form": data,
                "categories": Category.objects.all(),
                "tags": Tag.objects.all(),
                "selected_category_ids": category_ids,
                "selected_tag_ids": tag_ids,
            },
        )


class SiteBlogListView(View):
    def get(self, request):
        posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-published_at', '-created_at')[:20]
        return render(request, 'blog/list.html', { 'posts': posts })


class SiteBlogDetailView(View):
    def get(self, request, slug: str):
        post = get_object_or_404(Post, slug=slug)
        if post.status != Post.Status.PUBLISHED and not (request.user.is_authenticated and (request.user.is_staff or post.author_id == request.user.id)):
            return redirect('blog_list')
        can_manage = request.user.is_authenticated and (request.user.is_staff or post.author_id == request.user.id)
        
        # Get next and previous published posts
        next_post = None
        prev_post = None
        
        if post.published_at:
            next_post = Post.objects.filter(
                status=Post.Status.PUBLISHED,
                published_at__gt=post.published_at,
                published_at__isnull=False
            ).order_by('published_at').first()
            
            prev_post = Post.objects.filter(
                status=Post.Status.PUBLISHED,
                published_at__lt=post.published_at,
                published_at__isnull=False
            ).order_by('-published_at').first()
        
        return render(request, 'blog/detail.html', {
            'post': post,
            'can_manage': can_manage,
            'next_post': next_post,
            'prev_post': prev_post,
        })

    @method_decorator(login_required)
    def post(self, request, slug: str):
        # Allow delete via POST with _method=delete to avoid separate route
        if request.POST.get('_method') != 'delete':
            return redirect('blog_detail', slug=slug)
        post = get_object_or_404(Post, slug=slug)
        if not (request.user.is_staff or post.author_id == request.user.id):
            return HttpResponseForbidden("Not allowed")
        post.delete()
        return redirect('blog_list')


class EditorImageUploadView(View):
    @method_decorator(login_required)
    def post(self, request):
        # CKEditor simpleUpload sends the file under 'upload'
        file = request.FILES.get('upload') or request.FILES.get('file')
        if not file:
            return HttpResponseBadRequest('No file provided')
        # Save under media/editor/<username>/
        base_dir = os.path.join('editor', str(request.user.id))
        filename = default_storage.save(os.path.join(base_dir, file.name), file)
        url = default_storage.url(filename)
        # TinyMCE expects {location: url}; CKEditor expects {url: url}. Return both.
        return JsonResponse({"location": url, "url": url})


class CmsBotListView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_staff:
            return redirect('blog_list')
        q = (request.GET.get('q') or '').strip()
        bots = BotInstance.objects.select_related('owner').order_by('-created_at')[:50]
        if q:
            try:
                bots = bots.filter(owner__email__icontains=q) | bots.filter(owner__username__icontains=q)
            except Exception:
                pass
        return render(request, 'cms/bots.html', { 'bots': bots, 'q': q })


class CmsBotUpdateView(View):
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        bot_id = request.POST.get('bot_id')
        status_val = request.POST.get('status')
        url = (request.POST.get('bot_url') or '').strip()
        try:
            bot = BotInstance.objects.get(id=bot_id)
        except BotInstance.DoesNotExist:
            return redirect('cms_bots')
        if status_val in dict(BotInstance.Status.choices):
            bot.status = status_val
        bot.bot_url = url or None
        bot.save(update_fields=['status', 'bot_url', 'updated_at'])
        return redirect('cms_bots')


class BlogTextToSpeechView(views.APIView):
    """
    Generate natural-sounding audio from blog post text using Microsoft Edge TTS.
    Completely FREE, unlimited usage, no API key required!
    Uses edge-tts library for professional-quality voices.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        import re
        import base64
        import asyncio
        
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit text length for performance (Edge TTS has no hard limit)
        if len(text) > 5000:
            text = text[:5000] + '...'
        
        try:
            # Import edge-tts (install with: pip install edge-tts)
            import edge_tts
            
            # Choose voice
            # Male voices:
            # 'en-US-GuyNeural' - Deep, professional
            # 'en-US-ChristopherNeural' - Clear, friendly
            # Female voices:
            # 'en-US-AriaNeural' - Natural, conversational
            # 'en-US-JennyNeural' - Warm, expressive
            
            voice = 'en-US-GuyNeural'  # Professional male voice
            
            # Generate audio using edge-tts
            async def generate_audio():
                communicate = edge_tts.Communicate(text, voice)
                audio_data = b''
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(generate_audio())
            loop.close()
            
            if audio_data:
                # Convert to base64
                audio_content = base64.b64encode(audio_data).decode('utf-8')
                
                return Response({
                    'audioContent': audio_content,
                    'format': 'mp3'
                })
            else:
                return Response({
                    'error': 'No audio generated',
                    'fallback': 'web-speech-api'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ImportError:
            # edge-tts not installed
            return Response({
                'error': 'edge-tts library not installed. Run: pip install edge-tts',
                'fallback': 'web-speech-api'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'TTS error: {str(e)}',
                'fallback': 'web-speech-api'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class CmsPaymentListView(View):
    """Admin view to manage all payments and their associated bots"""
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_staff:
            return redirect('blog_list')
        
        from django.db.models import Q, Count, Sum
        
        # Get filters
        q = (request.GET.get('q') or '').strip()
        filter_status = request.GET.get('status', '').strip()
        filter_bot_status = request.GET.get('bot_status', '').strip()
        
        # Base queryset
        payments = PaymentTransaction.objects.select_related('student').order_by('-created_at')
        
        # Apply search filter
        if q:
            payments = payments.filter(
                Q(reference__icontains=q) |
                Q(student__email__icontains=q) |
                Q(student__username__icontains=q)
            )
        
        # Apply payment status filter
        if filter_status:
            payments = payments.filter(status=filter_status)
        
        # Get all payments (limit to 50 for performance)
        payments = list(payments[:50])
        
        # Attach bot info to each payment
        for payment in payments:
            try:
                raw = payment.raw_payload or {}
                if isinstance(raw, dict):
                    bot_ref = raw.get("bot_reference")
                    if bot_ref:
                        bot = BotInstance.objects.filter(reference=bot_ref).first()
                        if bot:
                            payment.bot_info = bot
                        else:
                            payment.bot_info = None
                    else:
                        payment.bot_info = None
                else:
                    payment.bot_info = None
            except Exception:
                payment.bot_info = None
        
        # Apply bot status filter
        if filter_bot_status:
            if filter_bot_status == 'none':
                payments = [p for p in payments if not hasattr(p, 'bot_info') or p.bot_info is None]
            else:
                payments = [p for p in payments if hasattr(p, 'bot_info') and p.bot_info and p.bot_info.status == filter_bot_status]
        
        # Calculate statistics
        all_payments = PaymentTransaction.objects.all()
        stats = {
            'success_count': all_payments.filter(status='success').count(),
            'success_amount': all_payments.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_count': all_payments.filter(status='pending').count(),
            'pending_amount': all_payments.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0,
            'bots_ready': BotInstance.objects.filter(status='ready').count(),
            'needs_processing': all_payments.filter(status='success').exclude(
                raw_payload__bot_reference__isnull=False
            ).count(),
            'currency': 'NGN',
        }
        
        return render(request, 'cms/payments.html', {
            'payments': payments,
            'stats': stats,
            'q': q,
            'filter_status': filter_status,
            'filter_bot_status': filter_bot_status,
        })


class CmsPaymentUpdateStatusView(View):
    """Update payment status"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        payment_id = request.POST.get('payment_id')
        new_status = request.POST.get('payment_status')
        
        try:
            payment = PaymentTransaction.objects.get(id=payment_id)
            if new_status in dict(PaymentTransaction.Status.choices):
                payment.status = new_status
                payment.save(update_fields=['status', 'updated_at'])
                
                # Auto-create bot if status changed to success and no bot exists
                if new_status == 'success':
                    raw = payment.raw_payload or {}
                    if not raw.get('bot_reference'):
                        bot = BotInstance.objects.create(
                            owner=payment.student,
                            status=BotInstance.Status.PENDING
                        )
                        raw['bot_reference'] = str(bot.reference)
                        payment.raw_payload = raw
                        payment.save(update_fields=['raw_payload'])
        except PaymentTransaction.DoesNotExist:
            pass
        
        return redirect('cms_payments')


class CmsPaymentUpdateBotView(View):
    """Update bot URL and status from payment management page"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        bot_id = request.POST.get('bot_id')
        bot_url = (request.POST.get('bot_url') or '').strip()
        
        try:
            bot = BotInstance.objects.get(id=bot_id)
            bot.bot_url = bot_url or None
            
            # Auto-update status to 'ready' if URL is provided
            if bot_url and bot.status != 'ready':
                bot.status = BotInstance.Status.READY
            
            bot.save(update_fields=['bot_url', 'status', 'updated_at'])
        except BotInstance.DoesNotExist:
            pass
        
        return redirect('cms_payments')


class CmsPaymentCreateBotView(View):
    """Create a bot for a payment that doesn't have one"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        payment_reference = request.POST.get('payment_reference')
        
        try:
            payment = PaymentTransaction.objects.get(reference=payment_reference)
            
            # Create bot
            bot = BotInstance.objects.create(
                owner=payment.student,
                status=BotInstance.Status.PENDING
            )
            
            # Link bot to payment
            raw = payment.raw_payload or {}
            raw['bot_reference'] = str(bot.reference)
            payment.raw_payload = raw
            payment.save(update_fields=['raw_payload'])
        except PaymentTransaction.DoesNotExist:
            pass
        
        return redirect('cms_payments')


class CmsPaymentDeleteView(View):
    """Delete a payment record"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        payment_id = request.POST.get('payment_id')
        
        try:
            payment = PaymentTransaction.objects.get(id=payment_id)
            
            # Also delete associated bot if it exists
            raw = payment.raw_payload or {}
            if isinstance(raw, dict):
                bot_ref = raw.get('bot_reference')
                if bot_ref:
                    BotInstance.objects.filter(reference=bot_ref).delete()
            
            payment.delete()
        except PaymentTransaction.DoesNotExist:
            pass
        
        return redirect('cms_payments')


class CmsCommentModerationView(View):
    """Admin interface to moderate blog comments"""
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_staff:
            return redirect('blog_list')
        
        from blog.models import Comment
        from django.db.models import Q
        
        # Get filters
        q = (request.GET.get('q') or '').strip()
        filter_status = request.GET.get('status', '').strip()
        
        # Base queryset
        comments = Comment.objects.select_related('post', 'author').order_by('-created_at')
        
        # Apply search filter
        if q:
            comments = comments.filter(
                Q(content__icontains=q) |
                Q(post__title__icontains=q) |
                Q(author__username__icontains=q) |
                Q(author__email__icontains=q)
            )
        
        # Apply status filter
        if filter_status:
            comments = comments.filter(status=filter_status)
        
        # Get comments (limit to 50 for performance)
        comments = list(comments[:50])
        
        # Calculate statistics
        from blog.models import Comment as CommentModel
        stats = {
            'pending_count': CommentModel.objects.filter(status='pending').count(),
            'approved_count': CommentModel.objects.filter(status='approved').count(),
            'rejected_count': CommentModel.objects.filter(status='rejected').count(),
            'total_count': CommentModel.objects.count(),
        }
        
        return render(request, 'cms/comments.html', {
            'comments': comments,
            'stats': stats,
            'q': q,
            'filter_status': filter_status,
        })


class CmsCommentApproveView(View):
    """Approve a comment"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        from blog.models import Comment
        comment_id = request.POST.get('comment_id')
        
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.status = Comment.Status.APPROVED
            comment.save(update_fields=['status', 'updated_at'])
        except Comment.DoesNotExist:
            pass
        
        return redirect('cms_comments')


class CmsCommentRejectView(View):
    """Reject a comment"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        from blog.models import Comment
        comment_id = request.POST.get('comment_id')
        
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.status = Comment.Status.REJECTED
            comment.save(update_fields=['status', 'updated_at'])
        except Comment.DoesNotExist:
            pass
        
        return redirect('cms_comments')


class CmsCommentDeleteView(View):
    """Delete a comment"""
    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden("Not allowed")
        
        from blog.models import Comment
        comment_id = request.POST.get('comment_id')
        
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
        except Comment.DoesNotExist:
            pass
        
        return redirect('cms_comments')
