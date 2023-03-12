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

def launch_raw_data():
    """
    Get Raw figures input from the user.
    Run a while loop to collect a valid data from the user
    via the API in google sheets, which must be a string of x numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:
        text_input = "have you put in your data"\
                    "data please confirm by typing 'x':"
        link = "https://docs.google.com/spreadsheets/d/"\
            "1cEWBDHZ35fzQ320SUUwLCcgsBtijk0C3keXW9kgA0Uc/edit#gid=0\n"\
            "/edit?usp=sharing"
        linkUser = "https://docs.google.com/document/d/"\
            "15TESpf-30ibR4NBzRKcN6XyxgjuNqkzDge-6oaH0oxI"\
            "/edit?usp=sharing"

        print("Please enter raw data in the google drive form.\n")
        print("questions how to input the data?")
        print("You can alsways consult the user guide\n")
        print(linkUser)
        print("Data should be the same range as the other samples\n")
        print("Put the Data in the googe sheets using this file: ")
        print(link)
        print("Example:")
        print(
            "{:<10}{:<10}{:<10}{:<10}{:<10}"
            .format("A", "B", "C", "D", "...")
            )
        print(
            "{:<10}{:<10}{:<10}{:<10}{:<10}"
            .format("Sample", 10, 20, 30, "...\n")
            )
        confirmation = input(text_input)

        if validate_drive_data(confirmation):
            print("Data is valid!")
            break


print("Welcome to Spectral Data Automation")

main()