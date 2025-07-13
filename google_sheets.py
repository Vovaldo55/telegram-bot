import gspread
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '1DuX1My51pRupQjgmU5hDX-ifWOzzfVSC6NfxO-6Ro7A'  # Встав сюди ID таблиці з URL

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def add_booking(name, phone, telegram_username, service, date, time, status="очікує підтвердження"):
    sheet = get_sheet()
    id = len(sheet.get_all_values())  # id = номер рядка
    sheet.append_row([id, name, phone, telegram_username, service, date, time, status])