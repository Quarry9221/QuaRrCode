import re
from typing import Tuple, Optional
from constants import MAX_TEXT_LENGTH

try:
    import validators
    HAS_VALIDATORS = True
except ImportError:
    HAS_VALIDATORS = False

class TextValidator:
    """Валідація тексту для QR кодів"""
    
    @staticmethod
    def validate_qr_text(text: str) -> Tuple[bool, str]:
        """
        Основна валідація тексту для QR коду
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Текст не може бути порожнім"
        
        text = text.strip()
        
        if len(text) > MAX_TEXT_LENGTH:
            return False, f"Текст занадто довгий (максимум {MAX_TEXT_LENGTH} символів)"
        
        # Перевірка на небезпечні символи
        if TextValidator._contains_dangerous_chars(text):
            return False, "Текст містить заборонені символи"
        
        return True, ""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Валідація URL"""
        if not url:
            return False, "URL не може бути порожнім"
        
        # Базова перевірка протоколу
        if not url.startswith(('http://', 'https://', 'ftp://')):
            return False, "URL повинен починатися з http://, https:// або ftp://"
        
        # Якщо є бібліотека validators - використовуємо її
        if HAS_VALIDATORS:
            if not validators.url(url):
                return False, "Невірний формат URL"
        else:
            # Базова regex перевірка
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, url):
                return False, "Невірний формат URL"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Валідація email"""
        if not email:
            return False, "Email не може бути порожнім"
        
        if HAS_VALIDATORS:
            if not validators.email(email):
                return False, "Невірний формат email"
        else:
            # Базова regex для email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "Невірний формат email"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Валідація номера телефону"""
        if not phone:
            return False, "Номер телефону не може бути порожнім"
        
        # Видаляємо всі пробіли та спеціальні символи для перевірки
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Перевірка довжини (7-15 цифр + можливий +)
        if len(clean_phone) < 7 or len(clean_phone) > 16:
            return False, "Номер телефону повинен містити 7-15 цифр"
        
        # Перевірка формату
        phone_pattern = r'^[\+]?[\d\s\-\(\)\.]{7,20}$'
        if not re.match(phone_pattern, phone):
            return False, "Невірний формат номера телефону"
        
        return True, ""
    
    @staticmethod
    def validate_wifi_ssid(ssid: str) -> Tuple[bool, str]:
        """Валідація назви WiFi мережі"""
        if not ssid or not ssid.strip():
            return False, "Назва мережі не може бути порожньою"
        
        ssid = ssid.strip()
        
        if len(ssid) > 32:
            return False, "Назва мережі занадто довга (максимум 32 символи)"
        
        # Перевірка на недозволені символи для SSID
        if any(ord(char) < 32 or ord(char) == 127 for char in ssid):
            return False, "Назва мережі містить недозволені символи"
        
        return True, ""
    
    @staticmethod
    def validate_wifi_password(password: str) -> Tuple[bool, str]:
        """Валідація паролю WiFi"""
        if not password:
            return True, ""  # Пароль може бути порожнім для відкритих мереж
        
        if len(password) < 8:
            return False, "Пароль WiFi повинен містити мінімум 8 символів"
        
        if len(password) > 63:
            return False, "Пароль WiFi занадто довгий (максимум 63 символи)"
        
        return True, ""
    
    @staticmethod
    def _contains_dangerous_chars(text: str) -> bool:
        """Перевірка на небезпечні символи"""
        # Список потенційно небезпечних символів/паттернів
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in dangerous_patterns)

class ContentTypeDetector:
    """Детектор типу контенту"""
    
    @staticmethod
    def detect_content_type(text: str) -> str:
        """
        Визначає тип контенту
        
        Returns:
            str: Емодзі + тип контенту
        """
        text = text.strip()
        
        # URL
        if ContentTypeDetector._is_url(text):
            return "🌐 URL"
        
        # Email
        if ContentTypeDetector._is_email(text):
            return "📧 Email"
        
        # Телефон
        if ContentTypeDetector._is_phone(text):
            return "📞 Телефон"
        
        # WiFi
        if ContentTypeDetector._is_wifi(text):
            return "📶 WiFi"
        
        # vCard (контакт)
        if ContentTypeDetector._is_vcard(text):
            return "👤 Контакт"
        
        # SMS
        if ContentTypeDetector._is_sms(text):
            return "📱 SMS"
        
        # Coordinates
        if ContentTypeDetector._is_coordinates(text):
            return "📍 Координати"
        
        # Cryptocurrency
        if ContentTypeDetector._is_crypto_address(text):
            return "₿ Криптоадреса"
        
        # Звичайний текст
        return "📝 Текст"
    
    @staticmethod
    def _is_url(text: str) -> bool:
        """Перевірка чи текст є URL"""
        if HAS_VALIDATORS:
            return validators.url(text)
        
        return text.startswith(('http://', 'https://', 'ftp://'))
    
    @staticmethod
    def _is_email(text: str) -> bool:
        """Перевірка чи текст є email"""
        if HAS_VALIDATORS:
            return validators.email(text)
        
        return '@' in text and '.' in text.split('@')[-1]
    
    @staticmethod
    def _is_phone(text: str) -> bool:
        """Перевірка чи текст є телефоном"""
        # Видаляємо все окрім цифр і +
        clean = re.sub(r'[^\d+]', '', text)
        return len(clean) >= 7 and re.match(r'^\+?[\d\s\-\(\)\.]+$', text)
    
    @staticmethod
    def _is_wifi(text: str) -> bool:
        """Перевірка чи текст є WiFi конфігурацією"""
        return text.upper().startswith('WIFI:')
    
    @staticmethod
    def _is_vcard(text: str) -> bool:
        """Перевірка чи текст є vCard"""
        return text.startswith('BEGIN:VCARD') and 'END:VCARD' in text
    
    @staticmethod
    def _is_sms(text: str) -> bool:
        """Перевірка чи текст є SMS"""
        return text.startswith('sms:') or text.startswith('smsto:')
    
    @staticmethod
    def _is_coordinates(text: str) -> bool:
        """Перевірка чи текст є координатами"""
        patterns = [
            r'^geo:[-+]?[0-9]*\.?[0-9]+,[-+]?[0-9]*\.?[0-9]+',
            r'^[-+]?[0-9]*\.?[0-9]+,\s*[-+]?[0-9]*\.?[0-9]+$'
        ]
        return any(re.match(pattern, text) for pattern in patterns)
    
    @staticmethod
    def _is_crypto_address(text: str) -> bool:
        """Перевірка чи текст є криптоадресою"""
        # Bitcoin
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', text):
            return True
        # Bitcoin (новий формат)
        if re.match(r'^bc1[a-z0-9]{39,59}$', text):
            return True
        # Ethereum
        if re.match(r'^0x[a-fA-F0-9]{40}$', text):
            return True
        
        return False