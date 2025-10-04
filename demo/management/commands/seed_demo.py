from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from payments.models import BotInstance
from bots.models import Question, Answer


class Command(BaseCommand):
    help = "Seed a demo BotInstance with sample Q&A"

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="demo", defaults={"email": "demo@example.com"})
        if not user.password:
            user.set_password("demo12345")
            user.save()

        bot = BotInstance.objects.filter(owner=user).first()
        if not bot:
            bot = BotInstance.objects.create(
                owner=user, 
                status=BotInstance.Status.READY, 
                bot_url="https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=https://files.bpcontent.cloud/2025/10/02/13/20251002132027-GSNRC2QE.json"
            )

        if not Question.objects.filter(bot=bot).exists():
            q1 = Question.objects.create(bot=bot, text="What is this service?")
            Answer.objects.create(question=q1, text="We turn your notes into a chatbot with verified Q&A.")
            q2 = Question.objects.create(bot=bot, text="How long does processing take?")
            Answer.objects.create(question=q2, text="Typically 24-72 hours depending on volume.")

        self.stdout.write(self.style.SUCCESS(f"Demo bot ready. Reference: {bot.reference}"))

