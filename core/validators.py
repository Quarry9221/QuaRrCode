import re
from typing import Tuple, Optional
from constants import MAX_TEXT_LENGTH

try:
    import validators

    HAS_VALIDATORS = True
except ImportError:
    HAS_VALIDATORS = False


class TextValidator:

    @staticmethod
    def validate_qr_text(text: str) -> Tuple[bool, str]:
        if not text or not text.strip():
            return False, "Текст не може бути порожнім"

        text = text.strip()

        if len(text) > MAX_TEXT_LENGTH:
            return False, f"Текст занадто довгий (максимум {MAX_TEXT_LENGTH} символів)"

        if TextValidator._contains_dangerous_chars(text):
            return False, "Текст містить заборонені символи"

        return True, ""

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        if not url:
            return False, "URL не може бути порожнім"

        if not url.startswith(("http://", "https://", "ftp://")):
            return False, "URL повинен починатися з http://, https:// або ftp://"

        if HAS_VALIDATORS:
            if not validators.url(url):
                return False, "Невірний формат URL"
        else:

            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            if not re.match(url_pattern, url):
                return False, "Невірний формат URL"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        if not email:
            return False, "Email не може бути порожнім"

        if HAS_VALIDATORS:
            if not validators.email(email):
                return False, "Невірний формат email"
        else:

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                return False, "Невірний формат email"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        if not phone:
            return False, "Номер телефону не може бути порожнім"

        clean_phone = re.sub(r"[^\d+]", "", phone)

        if len(clean_phone) < 7 or len(clean_phone) > 16:
            return False, "Номер телефону повинен містити 7-15 цифр"

        phone_pattern = r"^[\+]?[\d\s\-\(\)\.]{7,20}$"
        if not re.match(phone_pattern, phone):
            return False, "Невірний формат номера телефону"

        return True, ""

    @staticmethod
    def validate_wifi_ssid(ssid: str) -> Tuple[bool, str]:
        if not ssid or not ssid.strip():
            return False, "Назва мережі не може бути порожньою"

        ssid = ssid.strip()

        if len(ssid) > 32:
            return False, "Назва мережі занадто довга (максимум 32 символи)"

        if any(ord(char) < 32 or ord(char) == 127 for char in ssid):
            return False, "Назва мережі містить недозволені символи"

        return True, ""

    @staticmethod
    def validate_wifi_password(password: str) -> Tuple[bool, str]:
        if not password:
            return True, ""

        if len(password) < 8:
            return False, "Пароль WiFi повинен містити мінімум 8 символів"

        if len(password) > 63:
            return False, "Пароль WiFi занадто довгий (максимум 63 символи)"

        return True, ""

    @staticmethod
    def _contains_dangerous_chars(text: str) -> bool:

        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"vbscript:",
            r"onload=",
            r"onerror=",
        ]

        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in dangerous_patterns)


class ContentTypeDetector:

    @staticmethod
    def detect_content_type(text: str) -> str:
        text = text.strip()

        if ContentTypeDetector._is_url(text):
            return "🌐 URL"

        if ContentTypeDetector._is_email(text):
            return "📧 Email"

        if ContentTypeDetector._is_phone(text):
            return "📞 Телефон"

        if ContentTypeDetector._is_wifi(text):
            return "📶 WiFi"

        if ContentTypeDetector._is_vcard(text):
            return "👤 Контакт"

        if ContentTypeDetector._is_sms(text):
            return "📱 SMS"

        if ContentTypeDetector._is_coordinates(text):
            return "📍 Координати"

        if ContentTypeDetector._is_crypto_address(text):
            return "₿ Криптоадреса"

        return "📝 Текст"

    @staticmethod
    def _is_url(text: str) -> bool:
        if HAS_VALIDATORS:
            return validators.url(text)

        return text.startswith(("http://", "https://", "ftp://"))

    @staticmethod
    def _is_email(text: str) -> bool:
        if HAS_VALIDATORS:
            return validators.email(text)

        return "@" in text and "." in text.split("@")[-1]

    @staticmethod
    def _is_phone(text: str) -> bool:

        clean = re.sub(r"[^\d+]", "", text)
        return len(clean) >= 7 and re.match(r"^\+?[\d\s\-\(\)\.]+$", text)

    @staticmethod
    def _is_wifi(text: str) -> bool:
        return text.upper().startswith("WIFI:")

    @staticmethod
    def _is_vcard(text: str) -> bool:
        return text.startswith("BEGIN:VCARD") and "END:VCARD" in text

    @staticmethod
    def _is_sms(text: str) -> bool:
        return text.startswith("sms:") or text.startswith("smsto:")

    @staticmethod
    def _is_coordinates(text: str) -> bool:
        patterns = [
            r"^geo:[-+]?[0-9]*\.?[0-9]+,[-+]?[0-9]*\.?[0-9]+",
            r"^[-+]?[0-9]*\.?[0-9]+,\s*[-+]?[0-9]*\.?[0-9]+$",
        ]
        return any(re.match(pattern, text) for pattern in patterns)

    @staticmethod
    def _is_crypto_address(text: str) -> bool:

        if re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", text):
            return True

        if re.match(r"^bc1[a-z0-9]{39,59}$", text):
            return True

        if re.match(r"^0x[a-fA-F0-9]{40}$", text):
            return True

        return False
