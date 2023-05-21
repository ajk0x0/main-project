import subprocess
import shlex, netifaces, re

class Network:
    def __init__(self) -> None:
        output = subprocess.check_output(['nmcli', '-f', 'SSID', 'dev', 'wifi'])
        output = output.decode('utf-8')
        networks = [i.strip() for i in output.split('\n')[1:] if i]
        self.available_networks = self.filter_network(list(set(networks)))
        output = subprocess.check_output(['iwgetid', '-r']).decode('utf-8')
        self.current_wifi = output.strip()

    def get_host_ip(self) -> str:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if interface.startswith('w'):  # Assuming Wi-Fi interface starts with 'wlan'
                try:
                    addresses = netifaces.ifaddresses(interface)
                    ip_address = addresses[netifaces.AF_INET][0]['addr'].split(".")
                    print(ip_address)
                    ip_address[-1] = "137"
                    # return ".".join(ip_address)
                    return "192.168.43.137"

                except (KeyError, IndexError):
                    pass
        return None

    def filter_network(self, networks):
        pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
        return [network for network in networks if re.match(pattern, network)]

    def connect_wifi(self, ssid, password) -> None:
        if (ssid != self.current_wifi):
                subprocess.check_output( \
                    shlex.split(f"nmcli device wifi connect {ssid} password {password}") \
                        )
                self.current_wifi = ssid
