from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

def chat_view(request):
    return render(request, "simple_chat/chat.html")

@login_required
def messages_api(request):
    # opcional: soportar ?after_id=nnn para solo devolver nuevos
    after = request.GET.get("after_id")
    qs = ChatMessage.objects.all()
    if after:
        qs = qs.filter(id__gt=int(after))
    msgs = [{"id": m.id, "user": m.user.username if m.user else "Anon", "text": m.text, "created_at": m.created_at.isoformat()} for m in qs]
    return JsonResponse({"messages": msgs})

@require_POST
def post_message_api(request):
    # Usar autenticación si querés solo logueados; aquí permitimos anon también
    user = request.user if request.user.is_authenticated else None
    text = request.POST.get("text","").strip()
    if not text:
        return JsonResponse({"error": "empty"}, status=400)
    m = ChatMessage.objects.create(user=user, text=text)
    return JsonResponse({"id": m.id, "created_at": m.created_at.isoformat()})
