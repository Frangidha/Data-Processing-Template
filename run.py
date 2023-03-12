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
        
def validate_drive_data(confirmation):
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if strings cannot be converted into int,
    or if there aren't exactly 6 values.
    """
    try:
        # see loop_data function for explanation
        old_data, new_data, range_data, loop = loop_data()
        if confirmation == 'x':
            raw_data = SHEET.worksheet("Raw_Data")
            # checks if new-data is added
            if old_data < new_data:
                data_array = []
                lenght_data = []
                for ind in range(1, range_data):
                    column = raw_data.row_values(ind)
                    data_array.append(column[1:])
                    # checks if the data does not contain any strings
                    data_array = [
                        [str(s).replace(',', '') for s in group]
                        for group in data_array
                        ]
                    data_array = [
                        [float(value) for value in group]
                        for group in data_array
                        ]
                for x in data_array:
                    # add the lenght to the data_array
                    jls_extract_var = lenght_data
                    jls_extract_var.append(len(x))

                high_val = max(lenght_data)
                low_val = min(lenght_data)
                if high_val != lenght_data[0]:
                    raise ValueError(f"too many data points({high_val})")
                elif low_val != lenght_data[0]:
                    raise ValueError(f"not enough data points({low_val})")
            else:
                raise ValueError("did you add new Data?\n")
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True

def main():
    """
    Run all program functions
    """
    launch_raw_data()

print("Welcome to Spectral Data Automation")

main()