from enum import Enum

class BotState(Enum):
    MAIN_MENU = "main_menu"
    WAITING_TEXT = "waiting_text"
    WAITING_WIFI_SSID = "waiting_wifi_ssid"
    WAITING_WIFI_PASSWORD = "waiting_wifi_password"
    WAITING_CONTACT_NAME = "waiting_contact_name"
    WAITING_CONTACT_PHONE = "waiting_contact_phone"
    WAITING_CONTACT_EMAIL = "waiting_contact_email"
    WAITING_CONTACT_ORG = "waiting_contact_org"
    WAITING_EMAIL = "waiting_email"