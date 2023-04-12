import matplotlib.pyplot
import matplotlib.dates

from datetime import datetime

x_values = [datetime(2021, 11, 18, 12), datetime(2021, 11, 18, 14), datetime(2021, 11, 18, 16)]
y_values = [1.0, 3.0, 2.0]

dates = matplotlib.dates.date2num(x_values)
matplotlib.pyplot.plot_date(dates, y_values)

