from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from payments.models import BotInstance

class DemoInfoView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        demo = BotInstance.objects.order_by('created_at').first()
        if not demo:
            return Response({"detail": "No demo bot seeded yet"}, status=404)
        return Response({
            "reference": str(demo.reference),
            "status": demo.status,
            "bot_url": demo.bot_url,
        })
