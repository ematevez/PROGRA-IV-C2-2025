# netdiscover/utils/network.py  (versión mejorada)
import ipaddress
import platform
import subprocess
import re
import time
from concurrent.futures import ThreadPoolExecutor

# Si en Windows usás netifaces2 (recomendado), importalo como netifaces.
try:
    import netifaces as netifaces
except Exception:
    try:
        import netifaces2 as netifaces
    except Exception:
        netifaces = None

def get_default_cidr():
    """
    Detecta la interfaz por defecto y devuelve cidr tipo '192.168.1.0/24'.
    Lanza RuntimeError si no puede determinarlo.
    """
    if not netifaces:
        raise RuntimeError("netifaces no está disponible (instalá netifaces o netifaces2).")

    gws = netifaces.gateways()
    default = gws.get('default', {}).get(netifaces.AF_INET)
    if not default:
        raise RuntimeError("No se pudo detectar puerta de enlace por defecto.")
    iface = default[1]
    addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
    if not addrs:
        raise RuntimeError(f"No se encontraron direcciones en la interfaz {iface}")
    addr = addrs[0]
    ip = addr['addr']
    netmask = addr['netmask']
    # convertir máscara a prefixlen
    prefixlen = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False).prefixlen
    # calcular dirección de red
    net = ipaddress.IPv4Network(f"{ip}/{prefixlen}", strict=False).network_address
    return f"{net}/{prefixlen}"


# ----- Nmap method -----
def scan_with_nmap(network_cidr):
    try:
        import nmap
    except Exception:
        raise RuntimeError("python-nmap no instalado.")
    nm = nmap.PortScanner()
    nm.scan(hosts=network_cidr, arguments='-sn')
    hosts = []
    for host in nm.all_hosts():
        # algunos diccionarios de nmap usan 'addresses' u otros; control defensivo
        info = nm[host]
        addr = info.get('addresses') or info.get('address') or {}
        ip = addr.get('ipv4') or addr.get('ipv6') or host
        mac = addr.get('mac')
        # hostnames puede venir en lista
        hostname = None
        hostnames = info.get('hostnames')
        if hostnames:
            if isinstance(hostnames, list) and hostnames:
                hostname = hostnames[0].get('name')
        hosts.append({'ip': ip, 'mac': _normalize_mac(mac), 'hostname': hostname})
    return hosts


# ----- Scapy method (requires privileges) -----
def scan_with_scapy(network_cidr, timeout=2):
    try:
        from scapy.all import ARP, Ether, srp
    except Exception:
        raise RuntimeError("Scapy no instalado o fallo importando.")
    arp = ARP(pdst=network_cidr)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    ans, _ = srp(ether/arp, timeout=timeout, verbose=0)
    results = []
    for sent, received in ans:
        results.append({'ip': received.psrc, 'mac': _normalize_mac(received.hwsrc), 'hostname': None})
    return results


# ----- Helpers para ARP parsing -----
def _normalize_mac(mac):
    """Normaliza MACs a formato aa:bb:cc:dd:ee:ff o devuelve None si no hay."""
    if not mac:
        return None
    mac = mac.strip().lower()
    # reemplazar '-' por ':' y quitar posibles '0x' o paréntesis
    mac = mac.replace('-', ':').replace('0x', '').replace('(', '').replace(')', '')
    # extraer 6 bytes hex
    m = re.findall(r'([0-9a-f]{2})', mac)
    if len(m) >= 6:
        return ':'.join(m[:6])
    # fallback simple
    return mac


def parse_proc_arp():
    """
    Intenta leer /proc/net/arp (Linux) o arp -a (Windows/Mac).
    Devuelve lista de dicts {'ip','mac','hostname':None}.
    """
    results = []
    system = platform.system().lower()
    if system == 'linux':
        try:
            with open("/proc/net/arp") as f:
                lines = f.readlines()[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[0]
                    mac = parts[3]
                    if mac != "00:00:00:00:00:00":
                        results.append({'ip': ip, 'mac': _normalize_mac(mac), 'hostname': None})
            return results
        except Exception:
            # caemos a arp -a si algo falla
            pass

    # General fallback usando `arp -a`
    try:
        out = subprocess.check_output(["arp", "-a"], text=True, encoding="utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        # devolver vacío y permitir que el caller lo maneje
        return results
    # Windows y BSD/Mac tienen distintos formatos. Buscamos ip y mac en cada línea.
    for line in out.splitlines():
        # buscar IP
        ip_m = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
        # MAC puede venir con ':' o '-' o sin separadores
        mac_m = re.search(r'([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})', line, re.I)
        if ip_m:
            ip = ip_m.group(1)
            mac = mac_m.group(1) if mac_m else None
            if mac:
                results.append({'ip': ip, 'mac': _normalize_mac(mac), 'hostname': None})
    return results


# ----- Ping sweep + arp table fallback -----
def _ping(host):
    # en Windows el flag es -n, en Unix -c
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        subprocess.run(['ping', param, '1', host],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
    except Exception:
        pass


def scan_with_ping_then_arp(network_cidr, max_workers=100):
    """
    Hace ping a todos los hosts del CIDR y luego lee la tabla ARP.
    max_workers: ajustar según tu máquina (en Windows valores muy altos pueden fallar).
    """
    net = ipaddress.ip_network(network_cidr, strict=False)
    ips = [str(ip) for ip in net.hosts()]
    # limitar cantidad de workers razonable
    workers = min(max_workers, 200)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        ex.map(_ping, ips)
    # esperar un momento para que SO actualice ARP
    time.sleep(1.2)
    entries = parse_proc_arp()

    # Normalizar y eliminar duplicados por IP (mantener último)
    seen = {}
    for e in entries:
        if e.get('ip'):
            seen[e['ip']] = {'ip': e['ip'], 'mac': _normalize_mac(e.get('mac')), 'hostname': None}
    return list(seen.values())
