import os
import requests
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import MessageForm
from .models import TelegramMessage
from django.http import JsonResponse
from django.core.files.base import ContentFile
import json

TELEGRAM_BOT_TOKEN = "8414095917:AAFgFNwVIZH3Iec9SjkGTftncs7abr1nRFM"  # ⚠️ Usa tu token regenerado
# CHAT_ID = "1252733785"  # Tu chat_id
CHAT_ID = "-1003176121142"  # Tu chat_id

BOT_TOKEN = TELEGRAM_BOT_TOKEN
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# def chat_view(request):
#     form = MessageForm()

#     if request.method == 'POST':
#         form = MessageForm(request.POST, request.FILES)
#         if form.is_valid():
#             text = form.cleaned_data.get('message')
#             image = form.cleaned_data.get('image')

#             # Guardar texto y/o imagen en Telegram y base de datos
#             if image:
#                 # Guardar temporalmente la imagen
#                 path = default_storage.save(f"temp/{image.name}", image)
#                 full_path = os.path.join(settings.MEDIA_ROOT, path)
#                 with open(full_path, 'rb') as img_file:
#                     requests.post(
#                         f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
#                         data={"chat_id": CHAT_ID},
#                         files={"photo": img_file}
#                     )
#                 TelegramMessage.objects.create(sender='user', image_url=request.build_absolute_uri(settings.MEDIA_URL + path))
#             elif text:
#                 requests.post(
#                     f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
#                     data={"chat_id": CHAT_ID, "text": text}
#                 )
#                 TelegramMessage.objects.create(sender='user', text=text)

#             return redirect('chat_view')

#     # Obtener nuevos mensajes del bot
#     updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates").json()
#     if updates.get("ok"):
#         for update in updates["result"]:
#             msg = update.get("message", {})
#             if not msg:
#                 continue

#             sender_name = msg["from"]["first_name"]

#             # Si tiene texto
#             text = msg.get("text")
#             if text and not TelegramMessage.objects.filter(sender=sender_name, text=text).exists():
#                 TelegramMessage.objects.create(sender=sender_name, text=text)

#             # Si tiene imagen
#             if "photo" in msg:
#                 file_id = msg["photo"][-1]["file_id"]  # la de mayor resolución
#                 file_info = requests.get(
#                     f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
#                 ).json()
#                 file_path = file_info["result"]["file_path"]
#                 image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
#                 if not TelegramMessage.objects.filter(sender=sender_name, image_url=image_url).exists():
#                     TelegramMessage.objects.create(sender=sender_name, image_url=image_url)

#     messages = TelegramMessage.objects.all().order_by('date')

#     return render(request, 'chat.html', {'form': form, 'messages': messages})

# def telegram_webhook(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         if 'message' in data:
#             msg = data['message']
#             chat_id = msg['chat']['id']

#             # --- TEXTO ---
#             if 'text' in msg:
#                 TelegramMessage.objects.create(
#                     sender='Usuario',
#                     text=msg['text']
#                 )

#             # --- IMAGEN ---
#             elif 'photo' in msg:
#                 file_id = msg['photo'][-1]['file_id']
#                 file_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
#                 file_path = file_info['result']['file_path']
#                 file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

#                 image_response = requests.get(file_url)
#                 TelegramMessage.objects.create(
#                     sender='Usuario',
#                     image=ContentFile(image_response.content, name=file_path.split('/')[-1])
#                 )

#             # --- AUDIO / VOZ ---
#             elif 'voice' in msg or 'audio' in msg:
#                 file_id = msg.get('voice', msg.get('audio'))['file_id']
#                 file_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
#                 file_path = file_info['result']['file_path']
#                 file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

#                 audio_response = requests.get(file_url)
#                 TelegramMessage.objects.create(
#                     sender='Usuario',
#                     audio=ContentFile(audio_response.content, name=file_path.split('/')[-1])
#                 )

#         return JsonResponse({"ok": True})

# def chat_view(request):
#     if request.method == 'POST':
#         # --- Envío de texto ---
#         if 'text' in request.POST and request.POST['text']:
#             text = request.POST['text']
#             TelegramMessage.objects.create(sender='Tú', text=text)
#             requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': CHAT_ID, 'text': text})

#         # --- Envío de imagen ---
#         if 'image' in request.FILES:
#             image = request.FILES['image']
#             path = default_storage.save(f"images/{image.name}", image)
#             TelegramMessage.objects.create(sender='Tú', image=path)
#             with open(default_storage.path(path), 'rb') as img:
#                 requests.post(
#                     f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
#                     data={'chat_id': CHAT_ID},
#                     files={'photo': img}
#                 )

#         # --- Envío de audio ---
#         if 'audio' in request.FILES:
#             audio = request.FILES['audio']
#             path = default_storage.save(f"audios/{audio.name}", audio)
#             TelegramMessage.objects.create(sender='Tú', audio=path)
#             with open(default_storage.path(path), 'rb') as aud:
#                 requests.post(
#                     f'https://api.telegram.org/bot{BOT_TOKEN}/sendAudio',
#                     data={'chat_id': CHAT_ID},
#                     files={'audio': aud}
#                 )

#         return redirect('chat_view')

#     messages = TelegramMessage.objects.all().order_by('date')
#     return render(request, 'chat.html', {'messages': messages})


import os
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TelegramMessage
from .forms import MessageForm

TELEGRAM_BOT_TOKEN = 'TU_API_KEY'   # Cambiar por tu API Key
CHAT_ID = 'TU_CHAT_ID'              # Cambiar por tu chat_id

def chat_view(request):
    form = MessageForm()

    # --- POST: enviar mensaje ---
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data.get('message')
            photo = form.cleaned_data.get('photo')
            audio = form.cleaned_data.get('audio')

            # --- Enviar imagen ---
            if photo:
                path = default_storage.save(f"telegram_photos/{photo.name}", photo)
                full_path = os.path.join(settings.MEDIA_ROOT, path)
                with open(full_path, 'rb') as img_file:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                        data={"chat_id": CHAT_ID},
                        files={"photo": img_file}
                    )
                TelegramMessage.objects.create(sender='Tú', photo=path)

            # --- Enviar audio ---
            elif audio:
                path = default_storage.save(f"telegram_audios/{audio.name}", audio)
                full_path = os.path.join(settings.MEDIA_ROOT, path)
                with open(full_path, 'rb') as audio_file:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio",
                        data={"chat_id": CHAT_ID},
                        files={"audio": audio_file}
                    )
                TelegramMessage.objects.create(sender='Tú', audio=path)

            # --- Enviar texto ---
            elif text:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    data={"chat_id": CHAT_ID, "text": text}
                )
                TelegramMessage.objects.create(sender='Tú', text=text)

            return redirect('chat_view')

    # --- Obtener mensajes del bot de Telegram ---
    last_update_id = request.session.get('last_update_id', 0)

    updates = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}"
    ).json()

    if updates.get("ok"):
        for update in updates["result"]:
            msg = update.get("message")
            if not msg:
                continue

            sender_name = msg["from"]["first_name"]

            # --- Texto ---
            text = msg.get("text")
            if text and not TelegramMessage.objects.filter(sender=sender_name, text=text).exists():
                TelegramMessage.objects.create(sender=sender_name, text=text)

            # --- Imagen ---
            if "photo" in msg:
                file_id = msg["photo"][-1]["file_id"]
                file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()
                file_path = file_info["result"]["file_path"]
                response = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}")
                file_name = os.path.basename(file_path)
                saved_path = default_storage.save(f"telegram_photos/{file_name}", ContentFile(response.content))
                if not TelegramMessage.objects.filter(sender=sender_name, photo=saved_path).exists():
                    TelegramMessage.objects.create(sender=sender_name, photo=saved_path)

            # --- Audio / Voz ---
            if "voice" in msg or "audio" in msg:
                file_id = msg.get("voice", msg.get("audio"))["file_id"]
                file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()
                file_path = file_info["result"]["file_path"]
                response = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}")
                file_name = os.path.basename(file_path)
                saved_path = default_storage.save(f"telegram_audios/{file_name}", ContentFile(response.content))
                if not TelegramMessage.objects.filter(sender=sender_name, audio=saved_path).exists():
                    TelegramMessage.objects.create(sender=sender_name, audio=saved_path)

            # Actualizar último update_id
            last_update_id = update["update_id"]

    request.session['last_update_id'] = last_update_id

    messages = TelegramMessage.objects.all().order_by('date')

    # --- Si es AJAX, devolver JSON ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for msg in messages:
            data.append({
                'sender': msg.sender,
                'text': msg.text,
                'photo': msg.photo.url if msg.photo else '',
                'audio': msg.audio.url if msg.audio else '',
            })
        return JsonResponse({'messages': data})

    return render(request, 'chat.html', {'form': form, 'messages': messages})
