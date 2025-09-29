import re
from typing import Dict, Optional, List
from datetime import datetime


class TextProcessor:

    @staticmethod
    def create_wifi_qr_text(
        ssid: str, password: str, security: str = "WPA", hidden: bool = False
    ) -> str:

        ssid_escaped = TextProcessor._escape_wifi_special_chars(ssid)
        password_escaped = (
            TextProcessor._escape_wifi_special_chars(password) if password else ""
        )

        return f"WIFI:T:{security};S:{ssid_escaped};P:{password_escaped};H:{'true' if hidden else 'false'};;"

    @staticmethod
    def create_contact_qr_text(
        name: str,
        phone: str = "",
        email: str = "",
        organization: str = "",
        url: str = "",
        note: str = "",
    ) -> str:
        vcard_lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]

        if phone:

            clean_phone = re.sub(r"[^\d+\-\(\)\s]", "", phone)
            vcard_lines.append(f"TEL:{clean_phone}")

        if email:
            vcard_lines.append(f"EMAIL:{email}")

        if organization:
            vcard_lines.append(f"ORG:{organization}")

        if url:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            vcard_lines.append(f"URL:{url}")

        if note:
            vcard_lines.append(f"NOTE:{note}")

        vcard_lines.append("END:VCARD")

        return "\n".join(vcard_lines)

    @staticmethod
    def create_sms_qr_text(phone: str, message: str = "") -> str:
        clean_phone = re.sub(r"[^\d+]", "", phone)
        if message:
            return f"smsto:{clean_phone}:{message}"
        return f"sms:{clean_phone}"

    @staticmethod
    def create_email_qr_text(email: str, subject: str = "", body: str = "") -> str:
        mailto = f"mailto:{email}"

        params = []
        if subject:
            params.append(f"subject={TextProcessor._url_encode(subject)}")
        if body:
            params.append(f"body={TextProcessor._url_encode(body)}")

        if params:
            mailto += "?" + "&".join(params)

        return mailto

    @staticmethod
    def create_geo_qr_text(
        latitude: float, longitude: float, altitude: float = None
    ) -> str:
        if altitude is not None:
            return f"geo:{latitude},{longitude},{altitude}"
        return f"geo:{latitude},{longitude}"

    @staticmethod
    def create_event_qr_text(
        title: str,
        start_date: datetime,
        end_date: datetime = None,
        location: str = "",
        description: str = "",
    ) -> str:
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "BEGIN:VEVENT",
            f"SUMMARY:{title}",
            f"DTSTART:{start_date.strftime('%Y%m%dT%H%M%S')}",
        ]

        if end_date:
            lines.append(f"DTEND:{end_date.strftime('%Y%m%dT%H%M%S')}")

        if location:
            lines.append(f"LOCATION:{location}")

        if description:
            lines.append(f"DESCRIPTION:{description}")

        lines.extend(["END:VEVENT", "END:VCALENDAR"])

        return "\n".join(lines)

    @staticmethod
    def create_crypto_payment_qr(
        address: str,
        amount: float = None,
        label: str = "",
        message: str = "",
        crypto_type: str = "bitcoin",
    ) -> str:
        if crypto_type.lower() == "bitcoin":
            uri = f"bitcoin:{address}"
        elif crypto_type.lower() == "ethereum":
            uri = f"ethereum:{address}"
        else:
            return address

        params = []
        if amount:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={TextProcessor._url_encode(label)}")
        if message:
            params.append(f"message={TextProcessor._url_encode(message)}")

        if params:
            uri += "?" + "&".join(params)

        return uri

    @staticmethod
    def parse_wifi_qr_text(wifi_text: str) -> Optional[Dict[str, str]]:
        if not wifi_text.upper().startswith("WIFI:"):
            return None

        pattern = r"WIFI:T:([^;]*);S:([^;]*);P:([^;]*);H:([^;]*);?;?"
        match = re.match(pattern, wifi_text, re.IGNORECASE)

        if match:
            return {
                "security": match.group(1),
                "ssid": TextProcessor._unescape_wifi_special_chars(match.group(2)),
                "password": TextProcessor._unescape_wifi_special_chars(match.group(3)),
                "hidden": match.group(4).lower() == "true",
            }
        return None

    @staticmethod
    def extract_contact_info(vcard_text: str) -> Optional[Dict[str, str]]:
        if not vcard_text.startswith("BEGIN:VCARD"):
            return None

        info = {}
        lines = vcard_text.split("\n")

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                if key == "FN":
                    info["name"] = value
                elif key == "TEL":
                    info["phone"] = value
                elif key == "EMAIL":
                    info["email"] = value
                elif key == "ORG":
                    info["organization"] = value
                elif key == "URL":
                    info["url"] = value
                elif key == "NOTE":
                    info["note"] = value

        return info if info else None

    @staticmethod
    def generate_qr_text_preview(text: str, max_length: int = 50) -> str:
        if len(text) <= max_length:
            return text

        return text[: max_length - 3] + "..."

    @staticmethod
    def _escape_wifi_special_chars(text: str) -> str:

        replacements = {'"': '\\"', ";": "\\;", ",": "\\,", ":": "\\:", "\\": "\\\\"}

        for char, escaped in replacements.items():
            text = text.replace(char, escaped)

        return text

    @staticmethod
    def _unescape_wifi_special_chars(text: str) -> str:
        replacements = {'\\"': '"', "\\;": ";", "\\,": ",", "\\:": ":", "\\\\": "\\"}

        for escaped, char in replacements.items():
            text = text.replace(escaped, char)

        return text

    @staticmethod
    def _url_encode(text: str) -> str:
        import urllib.parse

        return urllib.parse.quote(text)


class QRTextAnalyzer:

    @staticmethod
    def analyze_text_complexity(text: str) -> Dict[str, any]:
        return {
            "length": len(text),
            "complexity": QRTextAnalyzer._calculate_complexity(text),
            "estimated_size": QRTextAnalyzer._estimate_qr_size(text),
            "character_types": QRTextAnalyzer._analyze_character_types(text),
        }

    @staticmethod
    def _calculate_complexity(text: str) -> str:
        length = len(text)

        if length < 50:
            return "Низька"
        elif length < 200:
            return "Середня"
        elif length < 500:
            return "Висока"
        else:
            return "Дуже висока"

    @staticmethod
    def _estimate_qr_size(text: str) -> str:
        length = len(text)

        if length < 25:
            return "21x21 (версія 1)"
        elif length < 47:
            return "25x25 (версія 2)"
        elif length < 77:
            return "29x29 (версія 3)"
        else:
            return "33x33+ (версія 4+)"

    @staticmethod
    def _analyze_character_types(text: str) -> Dict[str, int]:
        return {
            "digits": sum(1 for c in text if c.isdigit()),
            "letters": sum(1 for c in text if c.isalpha()),
            "special": sum(1 for c in text if not c.isalnum() and not c.isspace()),
            "spaces": sum(1 for c in text if c.isspace()),
        }
