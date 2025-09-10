from django.db.models.signals import post_save
from django.dispatch import receiver
from market.models import Product
from .models import ProductEmbedding
from .gemini_client import embed_text

@receiver(post_save, sender=Product)
def compute_product_embedding(sender, instance, created, **kwargs):
    # crea o actualiza embedding (puede tardar, tenelo en cuenta)
    text = f"{instance.title}. {instance.description or ''}. Marca: {instance.marca or ''}"
    emb = embed_text(text)
    if emb:
        obj, _ = ProductEmbedding.objects.update_or_create(
            product=instance,
            defaults={"vector": emb}
        )
