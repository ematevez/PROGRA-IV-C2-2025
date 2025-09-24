from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import UserActivity

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now_ts = timezone.now().timestamp()
            last = request.session.get("last_activity", now_ts)
            # 30 minutos = 1800 segundos
            if now_ts - last > 1800:
                logout(request)
                # después de logout, opcionalmente redirigir a página informativa
                return redirect("session_expired")
            request.session["last_activity"] = now_ts
        return self.get_response(request)

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserActivity.objects.update_or_create(user=request.user, defaults={"last_seen": timezone.now()})
        return self.get_response(request)
