from pymongo import MongoClient

# Conexión a MongoDB local
uri = "mongodb://localhost:27017"
client = MongoClient(uri)

# Base de datos y colección
db = client["333"]
collection = db["empleado"]

# Filtrar documentos con status "activo"
status_filter = "activo"
cursor = collection.find({"status": status_filter})

# Iterar sobre los documentos encontrados
found = False
for doc in cursor:
    found = True
    print("📄 Documento encontrado:")
    for key, value in doc.items():
        print(f"{key}: {value}")
    print("-" * 30)  # Separador entre documentos

if not found:
    print("⚠️ No se encontró ningún documento con status 'activo'")

# Cerrar conexión
client.close()