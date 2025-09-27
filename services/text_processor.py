import re
from typing import Optional

class TextProcessor:
    @staticmethod
    def extract_wifi_info(text: str) -> Optional[dict]:
        """Витягує інформацію про WiFi з тексту"""
        patterns = [
            r'wifi:T:([^;]+);S:([^;]+);P:([^;]+);H:([^;]*);',
            r'WIFI:T:([^;]+);S:([^;]+);P:([^;]+);',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "type": match.group(1),
                    "ssid": match.group(2),
                    "password": match.group(3),
                    "hidden": match.group(4) if len(match.groups()) > 3 else "false"
                }
        return None
    
    @staticmethod
    def create_wifi_qr_text(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> str:
        """Створює текст для WiFi QR коду"""
        return f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
    
    @staticmethod
    def create_contact_qr_text(name: str, phone: str = "", email: str = "", organization: str = "") -> str:
        """Створює vCard для контакту"""
        vcard = "BEGIN:VCARD\nVERSION:3.0\n"
        vcard += f"FN:{name}\n"
        if phone:
            vcard += f"TEL:{phone}\n"
        if email:
            vcard += f"EMAIL:{email}\n"
        if organization:
            vcard += f"ORG:{organization}\n"
        vcard += "END:VCARD"
        return vcard