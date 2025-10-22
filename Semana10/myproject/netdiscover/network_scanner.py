import subprocess
import platform
import socket
import re

class NetworkScanner:
    
    def get_local_ip(self):
        """Obtiene la IP local de la máquina"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None
    
    def get_network_range(self):
        """Calcula el rango de red basado en la IP local"""
        local_ip = self.get_local_ip()
        if not local_ip:
            return None
        base_ip = '.'.join(local_ip.split('.')[:-1])
        return f"{base_ip}.0/24"
    
    def ping(self, host):
        """Hace ping a un host"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', '1000', host]
        
        try:
            output = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                timeout=2
            )
            return output.returncode == 0
        except:
            return False
    
    def get_mac_windows(self, ip):
        """Obtiene la MAC en Windows usando arp"""
        try:
            output = subprocess.check_output(
                ['arp', '-a', ip], 
                timeout=2
            ).decode('utf-8', errors='ignore')
            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
            return mac.group(0) if mac else None
        except:
            return None
    
    def get_mac_linux(self, ip):
        """Obtiene la MAC en Linux/Mac usando arp"""
        try:
            output = subprocess.check_output(
                ['arp', '-n', ip], 
                timeout=2
            ).decode('utf-8', errors='ignore')
            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
            return mac.group(0) if mac else None
        except:
            return None
    
    def get_mac(self, ip):
        """Obtiene la MAC según el sistema operativo"""
        if platform.system().lower() == 'windows':
            return self.get_mac_windows(ip)
        else:
            return self.get_mac_linux(ip)
    
    def scan_network(self, progress_callback=None):
        """
        Escanea la red local
        
        Args:
            progress_callback: función opcional para reportar progreso
        
        Returns:
            Diccionario con resultados del escaneo
        """
        local_ip = self.get_local_ip()
        
        if not local_ip:
            return {"error": "No se pudo obtener la IP local"}
        
        base_ip = '.'.join(local_ip.split('.')[:-1])
        network_range = f"{base_ip}.0/24"
        
        devices = []
        
        # Escanear rango de IPs (1-254)
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            
            # Reportar progreso si hay callback
            if progress_callback:
                progress_callback(i, 254)
            
            if self.ping(ip):
                mac = self.get_mac(ip)
                
                # Intentar obtener hostname
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = 'Desconocido'
                
                devices.append({
                    'ip': ip,
                    'mac': mac if mac else 'No disponible',
                    'hostname': hostname,
                    'state': 'up'
                })
        
        return {
            'network_range': network_range,
            'local_ip': local_ip,
            'total_devices': len(devices),
            'devices': devices
        }