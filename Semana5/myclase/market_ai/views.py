from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PriceSuggestForm, ChatForm
from .gemini_client import generate_text, embed_text
from market.models import Product
from .models import ProductEmbedding
import math

def price_suggest(request):
    sugerencia = None
    prompt_example = (
        "Eres un asistente que sugiere un precio justo para un producto en un marketplace argentino. "
        "Recibís título, descripción y marca. Devuelve solo un número entero (sin moneda) y una breve razón."
    )
    if request.method == "POST":
        form = PriceSuggestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            prompt = (
                f"{prompt_example}\n\n"
                f"Titulo: {data['title']}\n"
                f"Descripcion: {data['description']}\n"
                f"Marca: {data['marca']}\n"
                f"Precio actual (si hay): {data.get('current_price')}\n\n"
                "Devuelve: Precio sugerido y una explicación corta."
            )
            respuesta = generate_text(prompt)
            sugerencia = respuesta
    else:
        form = PriceSuggestForm()
    return render(request, "price_suggest.html", {"form": form, "sugerencia": sugerencia})

def ai_chat(request):
    # simple chat basado en session (no persistente)
    if "ai_chat_history" not in request.session:
        request.session["ai_chat_history"] = []
    history = request.session["ai_chat_history"]

    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_msg = form.cleaned_data["message"]
            # armamos prompt con historia corta
            system = "Sos un asistente amablemente orientado a ayudar en un marketplace (publicar, comprar, trueque). Responde en español."
            accumulated = system + "\n\n"
            for turn in history[-6:]:
                accumulated += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n"
            accumulated += f"Usuario: {user_msg}\nAsistente: "
            ai_resp = generate_text(accumulated)
            # guardamos en history
            history.append({"user": user_msg, "ai": ai_resp})
            request.session["ai_chat_history"] = history
            request.session.modified = True
    else:
        form = ChatForm()
    return render(request, "ai_chat.html", {"form": form, "history": history})

def recommend_similar(request, pk):
    # recomienda productos similares por embeddings
    producto = get_object_or_404(Product, pk=pk, active=True)
    try:
        # intentamos usar embeddings guardados
        target = producto.embedding.vector
    except Exception:
        # si no hay embedding guardado, generamos en vuelo
        text = f"{producto.title}. {producto.description or ''}"
        target = embed_text(text)

    # calculo de similitud simple con todos los product embeddings
    candidates = ProductEmbedding.objects.exclude(product=producto)
    results = []
    import numpy as np
    tvec = np.array(target, dtype=float)
    for c in candidates:
        vec = np.array(c.vector, dtype=float)
        # coseno
        cos = float(np.dot(tvec, vec) / (np.linalg.norm(tvec) * np.linalg.norm(vec)))
        results.append((c.product, cos))
    results.sort(key=lambda x: x[1], reverse=True)
    top = [p for p,score in results[:6]]
    return render(request, "market_ai/recommendations.html", {"product": producto, "recommended": top})


