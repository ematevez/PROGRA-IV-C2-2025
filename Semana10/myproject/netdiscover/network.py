import netifaces
import ipaddress
import platform
import subprocess
import re
import time
from concurrent.futures import ThreadPoolExecutor

def get_default_cidr():
    """
    Detecta la interfaz por defecto y devuelve cidr tipo '192.168.1.0/24'.
    """
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
    # calcular red
    ip_int = int(ipaddress.IPv4Address(ip))
    mask_int = int(ipaddress.IPv4Address(netmask))
    network_int = ip_int & mask_int
    network = ipaddress.IPv4Address(network_int)
    # convertir mask a prefixlen
    prefixlen = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False).prefixlen
    return f"{network}/{prefixlen}"


# ----- Nmap method -----
def scan_with_nmap(network_cidr):
    try:
        import nmap
    except Exception:
        raise RuntimeError("python-nmap no instalado.")
    nm = nmap.PortScanner()
    # -sn = host discovery
    nm.scan(hosts=network_cidr, arguments='-sn')
    hosts = []
    for host in nm.all_hosts():
        addr = nm[host].get('addresses', {})
        ip = addr.get('ipv4') or addr.get('ipv6') or host
        mac = addr.get('mac')
        hostname = nm[host].get('hostnames', [{}])[0].get('name')
        hosts.append({'ip': ip, 'mac': mac, 'hostname': hostname})
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
        results.append({'ip': received.psrc, 'mac': received.hwsrc, 'hostname': None})
    return results


# ----- Ping sweep + arp table fallback -----
def _ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    try:
        subprocess.run(['ping', param, '1', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
    except Exception:
        pass

def parse_proc_arp():
    results = []
    try:
        with open("/proc/net/arp") as f:
            lines = f.readlines()[1:]
        for line in lines:
            parts = line.split()
            ip = parts[0]
            mac = parts[3]
            if mac != "00:00:00:00:00:00":
                results.append({'ip': ip, 'mac': mac, 'hostname': None})
    except FileNotFoundError:
        # Windows/mac parsing would go here (arp -a)
        out = subprocess.check_output(["arp", "-a"], text=True)
        entries = []
        for line in out.splitlines():
            m = re.search(r'\(([\d\.]+)\)\s+at\s+([0-9a-f:]+)', line, re.I)
            if m:
                ip, mac = m.group(1), m.group(2)
                entries.append({'ip': ip, 'mac': mac, 'hostname': None})
        return entries
    return results

def scan_with_ping_then_arp(network_cidr):
    net = ipaddress.ip_network(network_cidr, strict=False)
    ips = [str(ip) for ip in net.hosts()]
    with ThreadPoolExecutor(max_workers=200) as ex:
        ex.map(_ping, ips)
    time.sleep(1)
    return parse_proc_arp()