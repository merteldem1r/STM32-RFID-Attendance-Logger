from time import *

time_in_secs = time()
current_time_full_day = ctime(time_in_secs)
current_day = strftime("%d", gmtime(time_in_secs))
current_month = strftime("%b", gmtime(time_in_secs))
current_year = strftime("%Y", gmtime(time_in_secs))

full_date = f"{current_day}" + "-" + f"{current_month}" + "-" + f"{current_year}" 


print(current_time_full_day)
print(full_date)