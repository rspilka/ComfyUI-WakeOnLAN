import socket
import struct

class WakeOnLanNode:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mac_address": ("STRING", {"default": "00:00:00:00:00:00"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "send_wol"
    CATEGORY = "Network"

    def send_wol(self, mac_address):
        # Bereinige MAC-Adresse
        clean_mac = mac_address.replace(":", "").replace("-", "")
        if len(clean_mac) != 12:
            return (f"Fehler: Ungültige MAC-Adresse {mac_address}",)

        # Magic Packet erstellen
        data = bytes.fromhex('FF' * 6 + clean_mac * 16)
        
        # UDP Broadcast senden
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('255.255.255.255', 9))
        sock.close()
        
        return (f"Magic Packet an {mac_address} gesendet!",)

# Mapping für ComfyUI
NODE_CLASS_MAPPINGS = {
    "WakeOnLanNode": WakeOnLanNode
}
