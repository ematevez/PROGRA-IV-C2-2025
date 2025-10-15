from django.core.management.base import BaseCommand
from django.utils import timezone
from netdiscover.models import Host
from .network import get_default_cidr, scan_with_nmap, scan_with_scapy, scan_with_ping_then_arp

class Command(BaseCommand):
    help = "Escanea la red local y guarda IPs/MACs en la DB."

    def add_arguments(self, parser):
        parser.add_argument('--network', type=str, help='Red CIDR, ej 192.168.1.0/24')
        parser.add_argument('--method', type=str, choices=['nmap','scapy','ping'], default='nmap',
                            help='Metodo de escaneo: nmap (por defecto), scapy (necesita root), ping (broadcast via ping+arp)')

    def handle(self, *args, **options):
        network = options.get('network') or get_default_cidr()
        method = options.get('method') or 'nmap'
        self.stdout.write(f"Escaneando {network} con método {method}...")
        try:
            if method == 'nmap':
                hosts = scan_with_nmap(network)
            elif method == 'scapy':
                hosts = scan_with_scapy(network)
            else:
                hosts = scan_with_ping_then_arp(network)
        except Exception as e:
            self.stderr.write(f"Error en escaneo: {e}")
            return

        count = 0
        for h in hosts:
            ip = h.get('ip')
            mac = h.get('mac')
            hostname = h.get('hostname')
            obj, created = Host.objects.update_or_create(
                ip=ip,
                defaults={'mac': mac, 'hostname': hostname, 'last_seen': timezone.now()}
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Escaneo finalizado. Hosts guardados/actualizados: {count}"))