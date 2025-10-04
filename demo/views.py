from django.shortcuts import redirect
from django.views import View
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from payments.models import BotInstance

class DemoInfoView(View):
    """Redirect to the live demo bot"""
    def get(self, request):
        # Direct link to Pi gent demo bot on Botpress
        demo_url = "https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=https://files.bpcontent.cloud/2025/10/02/13/20251002132027-GSNRC2QE.json"
        return redirect(demo_url)


class DemoInfoAPIView(views.APIView):
    """API endpoint for demo bot info (legacy support)"""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "reference": "demo-bot",
            "status": "ready",
            "bot_url": "https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=https://files.bpcontent.cloud/2025/10/02/13/20251002132027-GSNRC2QE.json",
        })
