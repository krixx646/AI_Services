from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from payments.models import BotInstance
from .models import Question, Answer, Review
from .serializers import QuestionSerializer, AnswerSerializer, ReviewSerializer

class QuestionsView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, reference: str):
        bot = get_object_or_404(BotInstance, reference=reference)
        questions = Question.objects.filter(bot=bot).order_by("id")
        return Response(QuestionSerializer(questions, many=True).data)


class AnswerView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, reference: str):
        bot = get_object_or_404(BotInstance, reference=reference)
        if bot.status != BotInstance.Status.READY:
            return Response({"status": bot.status}, status=status.HTTP_200_OK)

        question_id = request.data.get("question_id")
        text = request.data.get("text")
        answer_text = None

        if question_id:
            try:
                q = Question.objects.get(id=question_id, bot=bot)
                answer_text = getattr(q.answer, "text", None)
            except Question.DoesNotExist:
                pass
        elif text:
            q = Question.objects.filter(bot=bot, text__iexact=text).first()
            if q:
                answer_text = getattr(q.answer, "text", None)

        if not answer_text:
            return Response({"detail": "No answer found for the provided question."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"answer": answer_text})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("bot", "student").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        bot_id = self.request.query_params.get("bot")
        if bot_id:
            qs = qs.filter(bot_id=bot_id)
        return qs

