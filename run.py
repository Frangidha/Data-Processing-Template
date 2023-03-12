import gspread
from google.oauth2.service_account import Credentials

"""
the app is connected via API to google sheets for easy access to
the old data. Secondly for a data control perspective to find back the data
in case of an audit. it is split in 3 sheets to easily see
each manipulation of the data.
"""

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('data_treatment')