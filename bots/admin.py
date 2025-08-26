from django.contrib import admin
from .models import Question, Answer, Review

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("bot", "text", "created_at")
    search_fields = ("text", "bot__reference")
    list_filter = ("created_at",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "created_at")
    search_fields = ("question__text",)
    list_filter = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("bot", "student", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("student__username", "student__email", "bot__reference")
