import pandas as pd
from django.shortcuts import render
from .forms import TwoExcelUploadForm
from datetime import datetime, timedelta
import math

def index(request):
    data_1 = None
    data_2 = None
    sheet_info = []
    table_headers_1 = ["Finish", "Start", "Screen", "Title", "Special", "", "Censor"]
    table_headers_2 = ["Film Title", "Times"]
    error_message = None

    if request.method == 'POST':
        form = TwoExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file_1 = request.FILES['excel_file_1']
            excel_file_2 = request.FILES['excel_file_2']

            try:
                # Read the Excel file into a pandas DataFrame
                df_1 = pd.read_excel(excel_file_1)
                # Convert DataFrame to a list of dictionaries for easy template rendering
                data_1 = df_1.to_dict(orient='records')
                full_list = [] # create temporary list to hold filtered data
                theatre_names = set() # create temporary lis to hold theatre names

                # go through excel file
                for row in data_1:
                    act_list = [] #store required data here
                    # convert dictionary to list
                    temp_list = list(row.values())

                    # append rows required change here if ever the excel file gets changed
                    act_list.append(temp_list[1]) # fnish time
                    act_list.append(temp_list[2]) # temp start times
                    act_list.append(temp_list[4]) # cinema numbers
                    act_list.append(temp_list[5]) # show names
                    if temp_list[6] == "DEFAULT":
                        temp_list[6] = "" # add empty column
                    act_list.append(temp_list[6]) # special show
                    act_list.append("")
                    act_list.append(temp_list[9])
                    full_list.append(act_list)

                    theatre_names.add(temp_list[4]) # add theatre names to names list

                # grab the date the sheet was made
                sheet_info.append(full_list[-1][1].split()[0])

                # remove first and last 2 rows of the list
                full_list = full_list[:-2]
                full_list.pop(0)

                #close and open time diff
                time_diff = timedelta(minutes=30)
                time_format = "%I:%M%p"

                #function to grab time
                def get_time_strings(index):
                    time_strings = []
                    for row in full_list:
                        time_strings.append(row[index])
                    
                    time_list = [datetime.strptime(time_str, time_format) for time_str in time_strings]

                    return time_list

                #get earliest time
                earliest_time = min(get_time_strings(1)) - time_diff
                earliest_time = earliest_time.strftime(time_format)
                sheet_info.append(earliest_time)

                # get latest time
                latest_time = max(get_time_strings(1)) + time_diff
                latest_time = latest_time.strftime(time_format)
                sheet_info.append(latest_time)

                # clean up list so last shows dont show up
                x_count = 0
                first_indexes = []
                last_indexes = []
                for name in theatre_names:
                    temp_list = []
                    x_count = 0
                    for i in range(len(full_list)):
                        if name == full_list[i][2]:
                            x_count = i
                            temp_list.append(x_count)
                            
                    if x_count != 0:
                        first_indexes.append(temp_list) # grab recurring indexes of consequent shows
                        last_indexes.append(x_count) # grab last show of indexes

                # fix show times
                for row in first_indexes:
                    for i in range(len(row)-1):
                        full_list[row[i]][1] = full_list[row[i+1]][1]

                # sort last_indexes to remove them from list
                last_indexes.sort(reverse=True)
                [full_list.pop(index) for index in last_indexes]

                #pass full_list to data_1
                data_1 = full_list

            except Exception as e:
                # Handle errors during file processing (e.g., invalid file format)
                error_message = f"Error processing First Excel file: {e}"
        
            if not error_message: # Only proceed if the first file had no issues, or remove this check if you want independent errors
                try:
                    df_2 = pd.read_excel(excel_file_2)
                    data_2 = df_2.to_dict(orient='records')
                    # appends first cinema title to list
                    data_2.insert(0, {'placeholder': list(data_2[0].keys())[0], '': '', '': '', '': '', '': '', '': '', '': '', '': ''})
                    full_list = []

                    theatre_count = 0
                    for row in data_2:                    
                        temp_list = list(row.values())
                        temp_list = temp_list[0:2]
                        
                        for i in range(2):
                            if type(temp_list[i]) == float:
                                temp_list[i] = ""

                            if "Cinema" in temp_list[i] or "IMAX" in temp_list[i]:
                                theatre_count += 1
                        
                        if temp_list != ['','']:
                            full_list.append(temp_list)
                    
                    # getting half the theatres
                    theatre_name = "Cinema " + str(math.ceil(theatre_count/2))

                    # remove last 2 rows of the list
                    full_list = full_list[:-2]

                    # split theatres in half
                    split_num = 0
                    for i in range(len(full_list)):
                        if theatre_name in full_list[i][0]:
                            split_num = i
                    
                    # pass data 2 to website
                    data_2 = [full_list[:split_num], full_list[split_num:]]

                except Exception as e:
                    error_message = f"Error processing Second Excel file: {e}"
        else:
            # Form is not valid (e.g., no files selected)
            error_message = "Please select both Excel files."
    else:
        form = TwoExcelUploadForm()

    return render(request, 'floorgen/index.html', {
        'form': form,
        'data_1': data_1,
        'data_2' : data_2,
        'table_headers_1': table_headers_1,
        'table_headers_2': table_headers_2,
        'sheet_info': sheet_info,
        'error_message': error_message,
    })