import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

# input data information to download.
curr_out_dir = input("Enter out directory: ")
start_year, start_month, start_day = input("Enter start date in format\x1B[3m year month day \x1B[0m: ").split()
end_year, end_month, end_day = input("Enter end date in format\x1B[3m year month day \x1B[0m: ").split()

# number which means None in dataset.
none_number = 99999.9
data_file_name = "data"

# add title to data file.
f = open(curr_out_dir + "/" + data_file_name + ".text", "a")
f.write("YYYY MM DD HH MM SS     KEV_X    KEV_Y    KEV_Z\n")
f.close()

start_time = datetime.strptime(start_year + start_month + start_day, '%Y%m%d')
end_time = datetime.strptime(end_year + end_month + end_day, '%Y%m%d')

date_list = [datetime.strftime(end_time - relativedelta(days=x), "%Y%m%d")
             for x in range(0, (end_time - start_time).days, 10)]


def load_data(current_time, out_dir):
    """
    Function for loading magnetometer data files from site IMAGE. Event length is equal to 10 days.

    :param current_time: example: 20180305
    :param out_dir: output directory for loaded file.
    """

    os.system(
        f"wget -q \"https://space.fmi.fi/image/www/data_download.php?starttime={current_time}"
        f"&length=14400&format=text&sample_rate=3600&stations=KEV\""
        f" -O {out_dir}/{current_time}.text")

    # write data from downloaded file to main data file.
    current_filepath = out_dir + "/" + current_time + ".text"
    fin = open(current_filepath, "r+")
    data = fin.read().splitlines(True)
    fin.close()
    fout = open(curr_out_dir + "/" + data_file_name + ".text", "a")
    fout.writelines(data[2:])
    fout.close()
    # check if no data is available on current date.
    if not data or data[0] == 'No data for specified stations on given date.' or \
            data[0] == 'Event across the change of the sample rate from 20 to 10 s (01 Nov 1992 00:00 UT)' or \
            "No data for specified date" in data[0]:
        fin = open(current_filepath, "r+")

        current_time = datetime(year=int(current_time[:4]), month=int(current_time[4:6]), day=int(current_time[6:8]),
                                hour=0, minute=0, second=0)

        # iterate each hour from 10 days.
        # create dates with corresponding NaN values.
        for i in range(0, 10 * 24):
            fin.write(datetime.strftime(current_time, "%Y %m %d %H %M %S ") + str(none_number) + " " +
                      str(none_number) + " " + str(none_number) + "\n")
            current_time = current_time + relativedelta(hours=1)

        fin.close()
        fin = open(current_filepath, "r+")
        data = fin.read().splitlines(True)
        fout = open(curr_out_dir + "/" + data_file_name + ".text", "a")
        fout.writelines(data[1:])
        fout.close()
        fin.close()

    os.remove(current_filepath)


for current_date in tqdm(date_list[::-1]):
    # load file for each date.
    load_data(current_time=current_date, out_dir=curr_out_dir)
