from django.shortcuts import render

from django.utils import timezone
from datetime import timedelta
from .models import UserActivity

def online_users(request):
    cutoff = timezone.now() - timedelta(minutes=5)  # considerar "activo" si vió hace 5 min
    active = UserActivity.objects.filter(last_seen__gte=cutoff).select_related("user")
    return render(request, "presence/online_users.html", {"active": active})


def session_expired(request):
    return render(request, "presence/session_expired.html")
