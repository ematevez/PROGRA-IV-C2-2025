from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .network_scanner import NetworkScanner

def index(request):
    """Página principal del escáner"""
    scanner = NetworkScanner()
    local_ip = scanner.get_local_ip()
    network_range = scanner.get_network_range()
    
    context = {
        'local_ip': local_ip,
        'network_range': network_range
    }
    
    return render(request, 'scanner.html', context)

@csrf_exempt
def scan(request):
    """Escanear la red - API endpoint"""
    if request.method == 'POST':
        try:
            scanner = NetworkScanner()
            results = scanner.scan_network()
            return JsonResponse(results)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'error': 'Método no permitido'
    }, status=405)








# import threading
# import time
# from datetime import timedelta

# from django.shortcuts import render
# from django.http import JsonResponse, HttpResponseNotAllowed
# from django.utils import timezone
# from django.views.decorators.http import require_POST

# from .models import Host
# from .network import get_default_cidr, scan_with_nmap, scan_with_ping_then_arp
# import subprocess, re, platform, ipaddress
# import logging

# logger = logging.getLogger(__name__)

# # --- Scan control (module-level) ---
# _scan_lock = threading.Lock()
# _is_scanning = False
# _last_scan_at = None
# _SCAN_COOLDOWN_SECONDS = 60  # tiempo mínimo entre escaneos automáticos

# def _can_start_scan():
#     global _is_scanning, _last_scan_at
#     if _is_scanning:
#         return False
#     if _last_scan_at is None:
#         return True
#     return (timezone.now() - _last_scan_at) > timedelta(seconds=_SCAN_COOLDOWN_SECONDS)

# def _run_scan(method="nmap"):
#     """Función que ejecuta el escaneo y guarda resultados en DB."""
#     global _is_scanning, _last_scan_at
#     with _scan_lock:
#         if _is_scanning:
#             return
#         _is_scanning = True

#     try:
#         try:
#             network = get_default_cidr()
#         except Exception:
#             network = "192.168.10.0/255"

#         try:
#             if method == "nmap":
#                 hosts_data = scan_with_nmap(network)
#             else:
#                 hosts_data = scan_with_ping_then_arp(network)
#         except Exception as e:
#             print(f"[netdiscover] Error durante escaneo: {e}")
#             hosts_data = []

#         for h in hosts_data:
#             Host.objects.update_or_create(
#                 ip=h.get("ip"),
#                 defaults={
#                     "mac": h.get("mac"),
#                     "hostname": h.get("hostname"),
#                     "last_seen": timezone.now()
#                 }
#             )

#         _last_scan_at = timezone.now()
#         print(f"[netdiscover] Escaneo completado: {len(hosts_data)} hosts; network={network}")

#     finally:
#         with _scan_lock:
#             _is_scanning = False


# # --- Views ---
# def hosts_list_page(request):
#     """
#     Página que muestra los hosts. Lanza un escaneo en background si no hay uno activo
#     y si ya pasó el cooldown.
#     """
#     try:
#         if _can_start_scan():
#             thread = threading.Thread(target=_run_scan, kwargs={"method": "nmap"}, daemon=True)
#             thread.start()
#     except Exception as e:
#         print("[netdiscover] fallo al iniciar thread:", e)

#     hosts = Host.objects.all().order_by("-last_seen")
#     return render(request, "hosts.html", {"hosts": hosts})


# def hosts_list_json(request):
#     """JSON con hosts actuales (útil para polling desde frontend)."""
#     hosts = Host.objects.all().order_by("-last_seen")
#     data = [
#         {"ip": h.ip, "mac": h.mac, "hostname": h.hostname, "last_seen": h.last_seen.isoformat()}
#         for h in hosts
#     ]
#     return JsonResponse({"hosts": data})


# def scan_status(request):
#     """Estado del escaneo: si está corriendo y timestamp del último escaneo."""
#     global _is_scanning, _last_scan_at
#     last = _last_scan_at.isoformat() if _last_scan_at else None
#     return JsonResponse({"is_scanning": bool(_is_scanning), "last_scan_at": last})


# # --- Nuevo endpoint PARA PRUEBAS (sin validación staff) ---

# def start_scan(request):
#     """
#     Inicia un scan en background si no hay uno activo y si pasó el cooldown.
#     Para pruebas locales: NO requiere usuario staff.
#     Devuelve JSON con {started: bool, message: str}.
#     """
#     global _is_scanning

#     # si ya está corriendo
#     if _is_scanning:
#         return JsonResponse({"started": False, "message": "Ya hay un escaneo en curso."}, status=409)

#     if not _can_start_scan():
#         return JsonResponse({"started": False, "message": "Cooldown activo. Esperá antes de iniciar otro escaneo."}, status=429)

#     # lanzar el thread
#     try:
#         thread = threading.Thread(target=_run_scan, kwargs={"method": "nmap"}, daemon=True)
#         thread.start()
#         return JsonResponse({"started": True, "message": "Escaneo iniciado en background (modo pruebas)."})
#     except Exception as e:
#         print("[netdiscover] fallo iniciando scan desde endpoint:", e)
#         return JsonResponse({"started": False, "message": "Error al iniciar el escaneo."}, status=500)

# def scan_network(request):
#     """
#     Escanea la red local y devuelve las IPs y MACs encontradas.
#     """
#     try:
#         print("🔍 Iniciando escaneo de red...")
#         system = platform.system()
#         print(f"Sistema operativo detectado: {system}")

#         # Intentamos obtener la red local
#         local_ip = "192.168.10.167"
#         cidr = "192.168.10.0/255"

#         try:
#             # Detectar red con ipconfig / ifconfig
#             if system == "Windows":
#                 output = subprocess.check_output("ipconfig", text=True, encoding="utf-8", errors="ignore")
#                 ip_match = re.search(r"IPv4.+?:\s*([\d\.]+)", output)
#                 mask_match = re.search(r"Máscara.+?:\s*([\d\.]+)", output)
#                 if ip_match and mask_match:
#                     ip = ip_match.group(1)
#                     mask = mask_match.group(1)
#                     prefix = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
#                     net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False).network_address
#                     cidr = f"{net}/{prefix}"
#             print(f"Red detectada: {cidr}")
#         except Exception as e:
#             print(f"⚠️ No se pudo detectar red automáticamente: {e}")

#         # Ejecutamos escaneo
#         print("Ejecutando escaneo ARP...")
#         command = "arp -a" if system == "Windows" else "arp -n"
#         result = subprocess.check_output(command, shell=True, text=True, encoding="utf-8", errors="ignore")
#         print(f"Salida del comando:\n{result}")

#         hosts = []
#         for line in result.splitlines():
#             if re.search(r"(\d+\.\d+\.\d+\.\d+)", line):
#                 ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
#                 mac_match = re.search(r"([0-9A-Fa-f:-]{17})", line)
#                 if ip_match and mac_match:
#                     ip = ip_match.group(1)
#                     mac = mac_match.group(1)
#                     hosts.append({"ip": ip, "mac": mac})
#         print(f"✅ {len(hosts)} hosts encontrados.")
#         return JsonResponse({"hosts": hosts})

#     except subprocess.CalledProcessError as e:
#         print(f"❌ Error ejecutando comando: {e}")
#         return JsonResponse({"error": str(e)}, status=500)
#     except Exception as e:
#         print(f"❌ Error desconocido: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)