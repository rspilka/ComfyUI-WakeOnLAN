import socket
import subprocess
import platform
import time
import re

class WakeOnLanNode:
    _executed_macs = set()

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mac_addresses": ("STRING", {"multiline": True, "default": "00:11:22:33:44:55"}),
                "mode": (["once_per_session", "always"], {"default": "once_per_session"}),
                "resolve_ips": (["no", "yes"], {"default": "no"}),
                "check_online": (["no", "yes_via_ping"], {"default": "no"}),
                "ip_for_ping": ("STRING", {"default": "192.168.1.100"}),
                "timeout_seconds": ("INT", {"default": 60, "min": 5, "max": 300}),
            },
            "optional": {
                "advanced_settings": (["disabled", "enabled"], {"default": "disabled"}),
                "reset_cache": (["no", "yes_clear_now"], {"default": "no"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("wol_status", "online_status", "discovered_ips")
    FUNCTION = "execute_wol"
    CATEGORY = "Network"
    
    color = "#224488"
    bgcolor = "#3366cc"

    def get_ip_from_mac(self, target_mac):
        clean_target = target_mac.replace(":", "-").lower()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(b"", ("255.255.255.255", 9))
            sock.close()
            time.sleep(0.5)
            
            output = subprocess.check_output(["arp", "-a"]).decode("ascii", errors="ignore")
            for line in output.splitlines():
                if clean_target in line.replace(":", "-").lower():
                    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if ip_match: return ip_match.group(1)
        except: pass
        return None

    def execute_wol(self, mac_addresses, mode, resolve_ips, check_online, ip_for_ping, timeout_seconds, advanced_settings="disabled", reset_cache="no"):
        if advanced_settings == "enabled" and reset_cache == "yes_clear_now":
            WakeOnLanNode._executed_macs.clear()

        mac_list = [m.strip() for m in mac_addresses.replace('\n', ',').replace(';', ',').split(',') if m.strip()]
        wol_results = []
        ip_results = []
        
        # 1. WOL & Status Generation
        for mac in mac_list:
            clean_mac = mac.replace(":", "").replace("-", "").replace(" " , "")
            if len(clean_mac) != 12:
                raise RuntimeError(f"WOL Node: Invalid MAC: {mac}")

            is_new_send = False
            if mode == "always" or clean_mac not in WakeOnLanNode._executed_macs:
                try:
                    data = bytes.fromhex('FF' * 6 + clean_mac * 16)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(data, ('255.255.255.255', 9))
                    sock.close()
                    WakeOnLanNode._executed_macs.add(clean_mac)
                    is_new_send = True
                except Exception as e:
                    raise RuntimeError(f"WOL Node: Send Error {mac}: {e}")

            status_icon = "✅" if is_new_send else "ℹ️"
            wol_results.append(f"{status_icon} {mac} (Sent)" if is_new_send else f"{status_icon} {mac} (Already Active)")

            # 2. IP Resolution (if enabled)
            if resolve_ips == "yes":
                ip = self.get_ip_from_mac(mac)
                if ip:
                    ip_results.append(f"✅ {mac} -> {ip}")
                else:
                    ip_results.append(f"❌ {mac} -> Not found")

        # 3. Online Check
        online_msg = "Check disabled"
        if check_online == "yes_via_ping":
            start_time = time.time()
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            is_online = False
            while (time.time() - start_time) < timeout_seconds:
                if subprocess.call(['ping', param, '1', '-w', '1000', ip_for_ping], stdout=subprocess.DEVNULL) == 0:
                    online_msg = f"✅ {ip_for_ping} is ONLINE!"
                    is_online = True
                    break
                time.sleep(2)
            
            if not is_online:
                raise RuntimeError(f"WOL Node: TIMEOUT! {ip_for_ping} not reachable.")

        return ("\n".join(wol_results), online_msg, "\n".join(ip_results) if ip_results else "None")

NODE_CLASS_MAPPINGS = {"WakeOnLanNode": WakeOnLanNode}
NODE_DISPLAY_NAME_MAPPINGS = {"WakeOnLanNode": "🌐 Wake on LAN Pro"}
