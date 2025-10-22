# #!/usr/bin/env python3
# """
# Escáner simple usando ping y comandos del sistema
# No requiere librerías externas, pero es más básico
# Funciona mejor en Windows
# """

# import subprocess
# import platform
# import socket
# import re

# def get_local_ip():
#     """Obtiene la IP local"""
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         local_ip = s.getsockname()[0]
#         s.close()
#         return local_ip
#     except:
#         return None

# def ping(host):
#     """Hace ping a un host"""
#     param = '-n' if platform.system().lower() == 'windows' else '-c'
#     command = ['ping', param, '1', '-w', '1000', host]
    
#     try:
#         output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
#         return output.returncode == 0
#     except:
#         return False

# def get_mac_windows(ip):
#     """Obtiene la MAC en Windows usando arp"""
#     try:
#         output = subprocess.check_output(['arp', '-a', ip], timeout=2).decode('utf-8', errors='ignore')
#         mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
#         return mac.group(0) if mac else None
#     except:
#         return None

# def get_mac_linux(ip):
#     """Obtiene la MAC en Linux/Mac usando arp"""
#     try:
#         output = subprocess.check_output(['arp', '-n', ip], timeout=2).decode('utf-8', errors='ignore')
#         mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
#         return mac.group(0) if mac else None
#     except:
#         return None

# def get_mac(ip):
#     """Obtiene la MAC según el sistema operativo"""
#     if platform.system().lower() == 'windows':
#         return get_mac_windows(ip)
#     else:
#         return get_mac_linux(ip)

# def scan_network():
#     """Escanea la red local"""
    
#     local_ip = get_local_ip()
    
#     if not local_ip:
#         print("❌ No se pudo obtener la IP local")
#         return
    
#     base_ip = '.'.join(local_ip.split('.')[:-1])
    
#     print("=" * 70)
#     print(f"🔍 Escaneando red: {base_ip}.0/24")
#     print(f"💻 Tu IP: {local_ip}")
#     print("=" * 70)
#     print()
#     print("⏳ Escaneando... (esto puede tardar 2-3 minutos)")
#     print()
    
#     devices = []
    
#     # Escanear rango de IPs
#     for i in range(1, 255):
#         ip = f"{base_ip}.{i}"
        
#         # Mostrar progreso
#         if i % 10 == 0:
#             print(f"   Progreso: {i}/254", end='\r')
        
#         if ping(ip):
#             mac = get_mac(ip)
#             devices.append({
#                 'ip': ip,
#                 'mac': mac if mac else 'No disponible'
#             })
    
#     print()
#     print()
#     print("=" * 70)
#     print(f"📱 DISPOSITIVOS ENCONTRADOS: {len(devices)}")
#     print("=" * 70)
#     print()
#     print(f"{'#':<5} {'IP':<18} {'MAC Address':<20}")
#     print("-" * 70)
    
#     for i, device in enumerate(devices, 1):
#         print(f"{i:<5} {device['ip']:<18} {device['mac']:<20}")
    
#     print("=" * 70)
#     print(f"✅ Escaneo completado: {len(devices)} dispositivos activos")
#     print("=" * 70)
    
#     if len(devices) == 0:
#         print()
#         print("⚠️  No se encontraron dispositivos (además de este equipo)")
#         print("💡 Esto puede deberse a:")
#         print("   - Firewall bloqueando ping")
#         print("   - Red muy grande o lenta")
#         print("   - Estar desconectado de la red")

# if __name__ == "__main__":
#     try:
#         scan_network()
#     except KeyboardInterrupt:
#         print("\n\n⚠️  Escaneo cancelado por el usuario")
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
        

"""
Script básico para escanear IPs y MACs en la red local
Requiere: pip install python-nmap
También necesitas tener nmap instalado en tu sistema
"""

import nmap
import socket

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def scan_network(network_range=None):
    """Escanea la red local"""
    
    # Si no se proporciona un rango, usa la IP local con /24
    if network_range is None:
        local_ip = get_local_ip()
        # Asume red /24 (255.255.255.0)
        base_ip = '.'.join(local_ip.split('.')[:-1])
        network_range = f"{base_ip}.0/24"
    
    print("=" * 60)
    print(f"🔍 Escaneando red: {network_range}")
    print("=" * 60)
    print()
    
    # Crear escáner
    nm = nmap.PortScanner()
    
    # Escanear red (puede requerir permisos de admin/root para ver MACs)
    print("⏳ Escaneando... (esto puede tardar 30-60 segundos)")
    nm.scan(hosts=network_range, arguments='-sn')
    
    print()
    print("=" * 60)
    print("📱 DISPOSITIVOS ENCONTRADOS")
    print("=" * 60)
    print()
    
    device_count = 0
    
    for host in nm.all_hosts():
        device_count += 1
        print(f"Dispositivo #{device_count}")
        print(f"  IP:       {host}")
        print(f"  Estado:   {nm[host].state()}")
        
        # Hostname
        hostname = nm[host].hostname()
        print(f"  Hostname: {hostname if hostname else 'Desconocido'}")
        
        # MAC Address (requiere permisos elevados)
        if 'mac' in nm[host]['addresses']:
            mac = nm[host]['addresses']['mac']
            print(f"  MAC:      {mac}")
            
            # Vendor (fabricante)
            if nm[host]['vendor']:
                vendor = list(nm[host]['vendor'].values())[0]
                print(f"  Vendor:   {vendor}")
        else:
            print(f"  MAC:      No disponible (ejecuta con sudo/admin)")
        
        print("-" * 60)
        print()
    
    print("=" * 60)
    print(f"✅ Escaneo completado: {device_count} dispositivos encontrados")
    print("=" * 60)
    
    if device_count == 0:
        print()
        print("⚠️  No se encontraron dispositivos.")
        print("💡 Asegúrate de:")
        print("   - Estar conectado a una red")
        print("   - Tener nmap instalado")
        print("   - Ejecutar con permisos elevados (sudo) para ver MACs")

if __name__ == "__main__":
    import sys
    
    # Puedes pasar el rango de red como argumento
    # Ejemplo: python scan_network.py 192.168.1.0/24
    if len(sys.argv) > 1:
        network_range = sys.argv[1]
    else:
        network_range = None
    
    try:
        scan_network(network_range)
    except KeyboardInterrupt:
        print("\n\n⚠️  Escaneo cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de tener instalado:")
        print("   pip install python-nmap")
        print("   Y nmap en tu sistema (apt install nmap / brew install nmap)")
        
#==================================================================
# #!/usr/bin/env python3
# """
# Escáner de red usando ARP con Scapy
# Requiere: pip install scapy
# Debe ejecutarse con permisos elevados (sudo en Linux/Mac)
# """

# from scapy.all import ARP, Ether, srp
# import socket

# def get_local_ip():
#     """Obtiene la IP local"""
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         local_ip = s.getsockname()[0]
#         s.close()
#         return local_ip
#     except:
#         return "127.0.0.1"

# def scan_network(ip_range=None):
#     """Escanea la red usando ARP"""
    
#     if ip_range is None:
#         local_ip = get_local_ip()
#         base_ip = '.'.join(local_ip.split('.')[:-1])
#         ip_range = f"{base_ip}.0/24"
    
#     print("=" * 70)
#     print(f"🔍 Escaneando red: {ip_range}")
#     print("=" * 70)
#     print()
    
#     # Crear paquete ARP
#     arp = ARP(pdst=ip_range)
#     ether = Ether(dst="ff:ff:ff:ff:ff:ff")
#     packet = ether/arp
    
#     print("⏳ Enviando paquetes ARP...")
#     result = srp(packet, timeout=3, verbose=0)[0]
    
#     devices = []
#     for sent, received in result:
#         devices.append({
#             'ip': received.psrc,
#             'mac': received.hwsrc
#         })
    
#     # Ordenar por IP
#     devices.sort(key=lambda x: [int(i) for i in x['ip'].split('.')])
    
#     print()
#     print("=" * 70)
#     print(f"📱 DISPOSITIVOS ENCONTRADOS: {len(devices)}")
#     print("=" * 70)
#     print()
#     print(f"{'#':<5} {'IP':<18} {'MAC Address':<20}")
#     print("-" * 70)
    
#     for i, device in enumerate(devices, 1):
#         print(f"{i:<5} {device['ip']:<18} {device['mac']:<20}")
    
#     print("=" * 70)
#     print(f"✅ Escaneo completado: {len(devices)} dispositivos")
#     print("=" * 70)
    
#     return devices

# if __name__ == "__main__":
#     import sys
#     import os
    
#     # Verificar si se ejecuta con permisos elevados
#     if os.geteuid() != 0:
#         print("⚠️  ADVERTENCIA: Este script requiere permisos de superusuario")
#         print("💡 Ejecuta con: sudo python3 scan_arp.py")
#         print()
    
#     ip_range = sys.argv[1] if len(sys.argv) > 1 else None
    
#     try:
#         scan_network(ip_range)
#     except KeyboardInterrupt:
#         print("\n\n⚠️  Escaneo cancelado")
#     except PermissionError:
#         print("\n❌ Error: Permisos insuficientes")
#         print("💡 Ejecuta con: sudo python3 scan_arp.py")
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         print("\n💡 Instala scapy con: pip install scapy")