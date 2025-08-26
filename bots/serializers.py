from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from payments.models import BotInstance
from .models import Question, Answer, Review


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "text")


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id", read_only=True)

    class Meta:
        model = Answer
        fields = ("question_id", "text")


class ReviewSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "bot", "student", "rating", "comment", "created_at")
        read_only_fields = ("id", "student", "created_at")

    def validate_rating(self, value: int) -> int:
        if value < 1 or value > 5:
            raise serializers.ValidationError(_("Rating must be between 1 and 5."))
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method.lower() == "post":
            bot = attrs.get("bot")
            if bot and bot.owner != request.user:
                raise serializers.ValidationError({"bot": _("You can only review your own bot.")})
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["student"] = request.user
        return super().create(validated_data)


