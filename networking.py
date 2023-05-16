import subprocess
import shlex, netifaces

class Network:
    def __init__(self) -> None:
        output = subprocess.check_output(['nmcli', '-f', 'SSID', 'dev', 'wifi'])
        output = output.decode('utf-8')
        networks = [i.strip() for i in output.split('\n')[1:] if i]
        self.available_networks = list(set(networks))

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
                    ip_address[-1] = "254"
                    #return ".".join(ip_address)
                    return "192.168.248.137"

                except (KeyError, IndexError):
                    pass
        return None

    def connect_wifi(self, ssid, password) -> None:
        global current_wifi
        if (ssid != current_wifi):
                subprocess.check_output( \
                    shlex.split(f"nmcli device wifi connect {ssid} password {password}") \
                        )
                self.current_wifi = ssid