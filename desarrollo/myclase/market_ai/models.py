from django.db import models

class ProductEmbedding(models.Model):
    # enlaza con tu modelo Product (ajusta el import si hace falta)
    from django.conf import settings
    # usa string para evitar import circular
    product = models.OneToOneField('market.Product', on_delete=models.CASCADE, related_name="embedding",)
    model = models.CharField(max_length=100, default="gemini-embedding-001")
    vector = models.JSONField()  # guardamos lista de floats
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding {self.product_id} ({self.model})"
