import gspread
from google.oauth2.service_account import Credentials
import plotext
import numpy as np
import time

"""
the app is connected via API to google sheets for easy access to
the old data. Secondly for a data control perspective to find back the data
in case of an audit. it is split in 3 sheets to easily see
each manipulation of the data.
"""

# How to check if the values
# Plot parameters - scatterplot
x_axes = "Wavenumbers (1/cm)"
y_axes = "Absorbance"

# Integration limit variable
int_limit1 = 1018.856
int_limit2 = 1302.502
int_limit3 = 1418.276
int_limit4 = 1501.247
int_limit5 = 1688.416
int_limit6 = 1896.809

# how to set your limit variables to get the requested comments
high_limit = 2
low_limit = 0
high_value = 0.75
low_value = 0.3
medium_value = 0.5

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


def raw_data_plot_generation(title, xlabel, ylabel):

    """
    This function will take the Raw Data values and plot
    them in graph to give a visual representation.

    """
    input_text = "The plot is generating, it will generate"\
        "in a couple of seconds...\n"

    print(input_text)
    integration_data = SHEET.worksheet("Raw_Data").get_all_values()

    data_after = {e[0]: e[1:] for e in integration_data}
    # turn data form string to float
    xdata = data_after['Wavenumbers']
    xdata = [s.replace(',', '') for s in xdata]
    xdata = [float(i) for i in xdata]
    ydata = data_after[title]
    ydata = [s.replace(',', '') for s in ydata]
    ydata = [float(i) for i in ydata]
    # plot the raw spectrum
    plotext.scatter(xdata, ydata)
    plotext.title(f"Spectrum of {title}")
    plotext.xlabel(xlabel)
    plotext.ylabel(ylabel)
    plotext.show()
    plotext.clear_figure()

    return integration_data


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully\n")


def calculate_integration_area(
        raw_data, sample, int1, int2, int3, int4, int5,
        int6):
    """
    Calculates the area under the graph for entire region and calculations

    the numpy library uses the composite trapezoidal rule
    The composite trapezoidal rule is a method for
    approximating a definite integral
    by evaluating the integrand at n points.
    Let [a,b] be the interval of integration with a partition a=x0<x1<…<xn=b.
    more info: https://planetmath.org/compositetrapezoidalrule
    """
    print("Calculating integration data...\n")
    integration_data = raw_data
    # convert into floats
    data_after = {e[0]: e[1:] for e in integration_data}
    xdata = data_after['Wavenumbers']
    xdata = [s.replace(',', '') for s in xdata]

    ydata = data_after[sample]
    ydata = [s.replace(',', '') for s in ydata]
    xdata = [float(i) for i in xdata]
    ydata = [float(i) for i in ydata]

    # search for the integration index
    # the selected values for partial integration
    integration_border_One = xdata.index(int1)
    integration_border_Two = xdata.index(int2)
    integration_border_Three = xdata.index(int3)
    integration_border_Four = xdata.index(int4)
    integration_border_Five = xdata.index(int5)
    integration_border_Six = xdata.index(int6)

    integration_row = []

    total_int = np.trapz(ydata, xdata)
    # integrate the entire data-set
    integration_row.append(total_int)
    # integrate hydroxyl group
    xdata_int_1 = xdata[integration_border_One:integration_border_Two]
    ydata_int_1 = ydata[integration_border_One:integration_border_Two]
    partial_int = np.trapz(ydata_int_1, xdata_int_1)

    integration_row.append(partial_int)
    # integrate CH3 group
    xdata_int_2 = xdata[integration_border_Two:integration_border_Three]
    ydata_int_2 = ydata[integration_border_Two:integration_border_Three]
    partial_int_2 = np.trapz(ydata_int_2, xdata_int_2)

    integration_row.append(partial_int_2)
    # integrate CH2 group
    xdata_int_3 = xdata[integration_border_Three:integration_border_Four]
    ydata_int_3 = ydata[integration_border_Three:integration_border_Four]
    partial_int_3 = np.trapz(ydata_int_3, xdata_int_3)

    integration_row.append(partial_int_3)
    # integrate Carbonyl group
    xdata_int_4 = xdata[integration_border_Five:integration_border_Six]
    ydata_int_4 = ydata[integration_border_Five:integration_border_Six]
    partial_int_4 = np.trapz(ydata_int_4, xdata_int_4)

    integration_row.append(partial_int_4)

    return integration_row


def calculate_ratio(integrated_data, Sample):
    """
    Calculate the ratio index for each item type.
    getting the integration values from google sheet
    calculated by the previous function
    Use of division and addition
    """

    int1 = float(integrated_data[0])
    int2 = float(integrated_data[1])
    int3 = float(integrated_data[2])
    int4 = float(integrated_data[3])
    int5 = float(integrated_data[4])

    Calculated_index = []
    Calculated_index.append(Sample)
    # Carbonyl index
    Ratio1 = int5/(int4+int3)
    Calculated_index.append(Ratio1)
    # Branching index
    Ratio2 = int3/(int3+int4)
    Calculated_index.append(Ratio2)
    # hydroxyl index
    Ratio3 = int2/int1
    Calculated_index.append(Ratio3)

    return Calculated_index


def ratio_evaluation(
        data, Sample, High_Lim, Low_Lim, High_ind, Medium_ind,
        Low_ind):

    """
    it takes the calculated data afterwards it give
    comments on this ratio and give recommendation or if
    the Data is not possible repeats the programma
    """

    Ratio_data = SHEET.worksheet("Calculation_index")

    headers = []
    for ind in range(1, 5):
        column = Ratio_data.col_values(ind)
        headers.append(column[0])

    # get the headers for the table
    head = headers[0]
    head1 = headers[1]
    head2 = headers[2]
    head3 = headers[3]

    ratio1 = float(data[1])
    ratio2 = float(data[2])
    ratio3 = float(data[3])

    x1 = round(ratio1, 3)
    x2 = round(ratio2, 3)
    x3 = round(ratio3, 3)

    print("Calculated Data Table:\n")
    # the date table
    print("{:<15} {:<15} {:<15} {:<15}".format(head, head1, head2, head3))
    print("{:<15} {:<15} {:<15} {:<15}".format(Sample, x1, x2, x3))

    print("")
    print("Data Interpretation:")
    # comments to each ratio regarding the set limits
    if ratio1 > High_Lim:
        print(f"{head1} seems to be outside the expected range\n")
    elif ratio1 > High_ind:
        print(f"{head1} seems to be quite high\n")
    elif ratio1 > Medium_ind:
        print(f"{head1} seems to be quite normal\n")
    elif ratio1 > Low_ind:
        print(f"{head1} seems to be quite low\n")
    elif ratio1 < Low_ind:
        print(f"{head1} seems to be Very low\n")
    elif ratio1 < Low_Lim:
        print(f"{head1} is negative please remeasure\n")
        launch_raw_data()
    else:
        print("oops something went wrong")
        launch_raw_data()

    if ratio2 > High_Lim:
        print(f"{head2} seems to be outside the expected range\n")
    elif ratio2 > High_ind:
        print(f"{head2} seems to be quite high\n")
    elif ratio2 > Medium_ind:
        print(f"{head2} seems to be quite normal\n")
    elif ratio2 > Low_ind:
        print(f"{head2} seems to be quite low\n")
    elif ratio2 < Low_ind:
        print(f"{head2} seems to be Very low\n")
    elif ratio2 < Low_Lim:
        print(f"{head2} is negative please remeasure\n")
        launch_raw_data()
    else:
        print("oops something went wrong")
        launch_raw_data()

    if ratio3 > High_Lim:
        print(f"{head3} seems to be outside the expected range\n")
    elif ratio3 > High_ind:
        print(f"{head3} seems to be quite high\n")
    elif ratio3 > Medium_ind:
        print(f"{head3} seems to be quite normal\n")
    elif ratio3 > Low_ind:
        print(f"{head3} seems to be quite low\n")
    elif ratio3 < Low_ind:
        print(f"{head3} seems to be Very low\n")
    elif ratio3 < Low_Lim:
        print(f"{head3} is negative please remeasure")
        launch_raw_data()
    else:
        print("oops something went wrong")
        launch_raw_data()

    return head1, head2, head3


def get_last_5_entires_ratio_values():
    """
    Collect columns of data from calculation worksheet.
    Get the last 5 entries for each sample and return the data
    as a list of lists.
    """

    Ratio_data = SHEET.worksheet("Calculation_index")

    Ratio_data_array = []
    for ind in range(1, 5):
        column = Ratio_data.col_values(ind)
        Ratio_data_array.append(column[-5:])

    Data_list_1 = []
    for ind in range(0, 5):
        column = Ratio_data_array[0][ind]
        Data_list_1.append(column)
    Data_list_2 = []
    for ind in range(0, 5):
        column = Ratio_data_array[1][ind]
        Data_list_2.append(column)
    Data_list_3 = []
    for ind in range(0, 5):
        column = Ratio_data_array[2][ind]
        Data_list_3.append(column)
    Data_list_4 = []
    for ind in range(0, 5):
        column = Ratio_data_array[3][ind]
        Data_list_4.append(column)
    return Data_list_1, Data_list_2, Data_list_3, Data_list_4


def plot_barchart(samples, data, ratio):

    """
    take al the Data and combine them to make the plot of the last
    5 entries to see the evolution of trends
    """
    print(f"{ratio} is being generated\n")
    # clean up the Data
    data_replace = [s.replace(',', '.') for s in data]
    # Determine y limits
    ymax = float(max(data_replace))
    ymin = round(float(min(data_replace))*0.98, 2)
    data_barchart = list(map(float, data_replace))
    plotext.ylim(ymin, ymax)
    plotext.plotsize(100, 30)
    plotext.bar(samples, data_barchart)
    plotext.title(ratio)
    plotext.show()
    plotext.clear_figure()


def get_sample_name(ind):
    """
    get the name of the sample taht is being calculated.
    """

    Sample_Name = SHEET.worksheet("Raw_Data")
    sample_column = Sample_Name.col_values(1)
    sample = sample_column[-abs(ind)]
    return sample


def loop_data():
    """
    This code is used to check the Raw_Data sheet if the data input is correct.
    it checks if new data was added compared to the already existing data.
    Secondly it will check if the length of data input is correct of each row.
    this Data is also used for the value and
    Sample input value to know where to start.
    """
    raw_data = SHEET.worksheet("Raw_Data").get_all_values()
    integration_data = SHEET.worksheet("Integrated_Data").get_all_values()
    new_data = len(raw_data)
    old_data_rows = len(integration_data)
    range_data = int(new_data) + 1
    loop = new_data - old_data_rows

    return old_data_rows, new_data, range_data, loop


def Test_Data():
    """
        the Data was tested using https://www.integral-calculator.com/
        and integration by hand. this function is made to quickly check
        and compared the values using a set
        of know values using the trap integration from the numpy library.
    """
    # linear function Data
    xdata1 = [
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300,
        1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500,
        2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500
            ]
    ydata1 = [
        20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130,
        140, 150, 160, 170, 180, 190, 200, 210,
        220, 230, 240, 250, 260, 270, 280, 290, 300,
        310, 320, 330, 340, 350, 360
            ]
    # exponential function Data
    xdata2 = [
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200,
        1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000
         ]
    ydata2 = [
        2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192,
        16384, 32768, 65536, 131072, 262144, 524288, 1048576
        ]
    int_test1 = np.trapz(ydata1, xdata1)
    int_test2 = np.trapz(ydata2, xdata2)
    deviation = int_test2/151144859
    Low_Limit = 0.95
    High_Limit = 1.05
    if (int_test1 == 646000):
        # exponential function Data instead of a absolute value
        # it is ratio that checks that the data doesn't deviate 5%.
        # otherwise it will display a fault message.
        if (deviation > Low_Limit):
            print("the linear integration is the same as the calculated value")
            if (deviation < High_Limit):
                print("the exponential integration is within the range")
        else:
            print("please check the programme and the integration values")
    else:
        print("please check the programme")


def main():
    """
    Run all program functions
    """
    launch_raw_data()
    old_data, new_data, range_data, loop = loop_data()
    x = loop

    for ind in reversed(range(loop)):
        Sample = get_sample_name(x)

        raw_data = raw_data_plot_generation(Sample, x_axes, y_axes)
        # Integration borders can be changed regarding your specifications
        integrated_data = calculate_integration_area(
            raw_data,
            Sample, int_limit1, int_limit2, int_limit3,
            int_limit4, int_limit5, int_limit6
            )
        update_worksheet(integrated_data, "Integrated_Data")
        ratio_data = calculate_ratio(integrated_data, Sample)
        update_worksheet(ratio_data, "Calculation_index")
        # High Limit, low Limit, high value, normal, value, low value
        h1, h2, h3 = ratio_evaluation(
            ratio_data, Sample, high_limit, low_limit,
            high_value, medium_value, low_value
            )
        x = x - 1
        # timer has been put in place not to overload the API
        # it will keep limit possible crashes
        time.sleep(10)

    # title
    # xlabel, ylabel
    bar_sample, bar_r1, bar_r2, bar_r3 = get_last_5_entires_ratio_values()

    # title, xlabel, ylabel
    plot_barchart(bar_sample, bar_r1, h1)
    plot_barchart(bar_sample, bar_r2, h2)
    plot_barchart(bar_sample, bar_r3, h3)


print("Welcome to Spectral Data Automation")

# Test data of integration using the trapz numpy library
# comparing to the classical method
# Test_Data()

# Runs the program
main()
