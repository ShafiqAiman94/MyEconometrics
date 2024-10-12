import matplotlib.pyplot as plt
import numpy as np
import mplcursors
from datetime import datetime
import matplotlib.dates as mdates
import logging

logger = logging.getLogger("econometrics")

class Plotter:
    def __init__(self):
        plt.rcParams['toolbar'] = 'None'
        plt.style.use('dark_background')
    
    def annotate(self, sel):
        xvalue = mdates.num2date(sel.target[0]).strftime('%Y-%m-%d')
        yvalue = "{:.2f}".format(sel.target[1])
        sel.annotation.set_text(f'Date : {xvalue} Value : {yvalue}')
        sel.annotation.arrow_patch.set(arrowstyle='simple', fc='white', \
                alpha=.5)

    def is_bond_data(self,indie):
        if 'Bond' in indie:
            return True
        else:
            return False
    
    def get_upward_sigma_count(self, mean, std, max_val):
        unmean = 0
        if max_val > mean:
            unmean = max_val - mean
        else:
            return 0
        count = unmean // std + 2
        return int(count)
    
    def convert_to_color(self, a):
        return "#" + str(hex(a)).lstrip("0x")
        
    def increase_color_code(self, color, increment):
        return color + (0x10 * increment)

    def get_downward_sigma_count(self, mean, std, min_val):
        unmean = 0
        if min_val < 0:
            min_val = min_val * -1
        else:
            return 0

        if min_val > mean:
            unmean = min_val - mean
        else:
            return 0

        count = unmean // std + 2
        return int(count)

    def draw_upward_std_line(self, subplot, mean, std, count, color):
        if count < 1:
            return

        for i in range(1,count):
            new_color_hex = self.increase_color_code(color, i)
            subplot.axhline(mean + std * i, \
                    color=self.convert_to_color(new_color_hex), \
                    linestyle='dashed', linewidth=0.5)
    
    def draw_downward_std_line(self, subplot, mean, std, count, color):
        if count < 1:
            return

        for i in range(1,count):
            new_color_hex = self.increase_color_code(color, i)
            subplot.axhline(mean - std * i, \
                    color=self.convert_to_color(new_color_hex), \
                    linestyle='dashed', linewidth=0.5)

    def line_chart_template(self, title1, title2, xlabel, ylabel, x_series, \
            y_series, look_back, std_en, y2_label = "", y2_series = []):
        y2_series_changes = []
        ax3 = None
        line1 = None
        line2 = None

        raw_dates = np.array(x_series)
        dates = np.datetime64('1970-01-01') + \
                raw_dates.astype('timedelta64[s]')
        # Calculate the changes
        y_series_changes = diff = [j - i for i, j in zip(y_series[:-1], \
                y_series[1:])]
        y_series_changes.insert(0,0)

        if y2_series:
            y2_series_changes = diff = [j - i for i, j in zip(y2_series[:-1], \
                    y2_series[1:])]
            y2_series_changes.insert(0,0)

        fig, (ax1, ax2) = plt.subplots(2, 1, \
                gridspec_kw={'height_ratios':[2, 1]}, figsize=(10, 8))
        # Calculate the mean and standard deviation
        y_series_mean = np.empty((1,))
        y_series_std = np.empty((1,))
        y_changes_mean = np.empty((1,))
        y_changes_std = np.empty((1,))
        y2_series_mean = np.empty((1,))
        y2_series_std = np.empty((1,))

        if std_en == 'on':
            y_series_mean = np.mean(y_series)
            y_series_std = np.std(y_series)
            y_changes_mean = np.mean(y_series_changes)
            y_changes_std = np.std(y_series_changes)
            if y2_series:
                y2_series_mean = np.mean(y2_series)
                y_series_std = np.std(y2_series)

        # Line chart
        if int(look_back) > 0:
            dates = dates[int(look_back) * -1:]
            y_series = y_series[int(look_back) * -1:]
            y2_series = y2_series[int(look_back) * -1:]
            y_series_changes = y_series_changes[int(look_back) * -1:]
        
        line1, = ax1.plot(dates, y_series, label=ylabel, color='#236cc4')

        # Two scales line plot
        if self.is_bond_data(title1):
            ax3 = ax1.twinx()
            ax3.set_ylabel(y2_label)
            line2, = ax3.plot(dates, y2_series, label=y2_label, \
                    color='#40d9db')

        if std_en == 'on':
            color = 0x616e12
            y_series_up_std_count = self.get_upward_sigma_count( \
                    y_series_mean, y_series_std, max(y_series))
            
            y_series_down_std_count = self.get_downward_sigma_count( \
                    y_series_mean, y_series_std, min(y_series))

            # Draw the mean line
            ax1.axhline(y_series_mean, color=self.convert_to_color(color), \
                    linestyle='dashed', linewidth=0.9, label='Mean')

            # Draw upward standard deviation
            self.draw_upward_std_line(ax1, y_series_mean, y_series_std, \
                    y_series_up_std_count, color)
            
            # Draw downward standard deviation
            self.draw_downward_std_line(ax1, y_series_mean, y_series_std, \
                    y_series_down_std_count, color)

        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.set_title(title1)

        if ax3:
            ax1.legend(handles=[line1,line2], loc='upper left')
        else:
            ax1.legend(loc='upper left')

        # Average changes chart
        ax2.plot(dates, y_series_changes, label=ylabel + " average changes", \
                color='#236cc4')

        if std_en == 'on':
            color = 0x616e12
            y_changes_up_std_count = self.get_upward_sigma_count( \
                    y_changes_mean, y_changes_std, max(y_series_changes))
            
            y_changes_down_std_count = self.get_downward_sigma_count( \
                    y_changes_mean, y_changes_std, min(y_series_changes))

            # Draw the mean line
            ax2.axhline(y_changes_mean, color=self.convert_to_color(color), \
                    linestyle='dashed', linewidth=0.9, label='Mean')

            # Draw upward standard deviation
            self.draw_upward_std_line(ax2, y_changes_mean, y_changes_std, \
                    y_changes_up_std_count, color)
            
            # Draw downward standard deviation
            self.draw_downward_std_line(ax2, y_changes_mean, y_changes_std, \
                    y_changes_down_std_count, color)

        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)
        ax2.set_title(title2)
        ax2.legend(loc='upper left')
        
        cursor1 = mplcursors.cursor(ax1, hover=True)
        cursor2 = mplcursors.cursor(ax2, hover=True)
        cursor1.connect("add", self.annotate)
        cursor2.connect("add", self.annotate)

        plt.tight_layout()
        plt.show()

    def seasonality_template(self, title, xlabel, ylabel, x_series, \
            y1_series, y2_series):
        # List for plotting
        y3_same_as_forecast_list = []
        y2_less_than_forecast_list = []
        y1_more_than_forecast_list = []
        x_month_list = []

        month_list = []
        for i in range(1, 13):
            new_dict = {
                        'month':i, \
                        'More than forecast':0, \
                        'Less than forecast':0, \
                        'Same as forecast':0 }
            month_list.append(new_dict)

        for idx, unix_date in enumerate(x_series):
            dt_obj = datetime.fromtimestamp(unix_date)
            month = dt_obj.month

            for j in month_list:
                if j['month'] == month:
                    # In case the data is null
                    if not y2_series[idx] or not y1_series[idx]:
                        continue

                    if y2_series[idx] > y1_series[idx]:
                        tmp_val = j.get('More than forecast')
                        j['More than forecast'] = tmp_val + 1
                        break
                    elif y2_series[idx] < y1_series[idx]: 
                        tmp_val = j.get('Less than forecast')
                        j['Less than forecast'] = tmp_val + 1
                        break
                    elif y2_series[idx] == y1_series[idx]: 
                        tmp_val = j.get('Same as forecast')
                        j['Same as forecast'] = tmp_val + 1
                        break
                    else:
                        pass

        for i in month_list:
            x_month_list.append(i['month'])
            y1_more_than_forecast_list.append(i['More than forecast'])
            y2_less_than_forecast_list.append(i['Less than forecast'])
            y3_same_as_forecast_list.append(i['Same as forecast'])

        # Plot the chart
        barwidth = 0.25

        r1 = np.arange(len(x_month_list))
        r2 = [x + barwidth for x in r1]
        r3 = [x + barwidth for x in r2]

        plt.figure(figsize=(10, 6))

        plt.bar(r1, y1_more_than_forecast_list, width=barwidth, \
                label='More than forecast', color='#005cf0')
        plt.bar(r2, y2_less_than_forecast_list, width=barwidth, \
                label='Less than forecast', color='#1ed665')
        plt.bar(r3, y3_same_as_forecast_list, width=barwidth, \
                label='Same as forecast', color='#f53d0f')

        plt.title(title, fontweight='bold')
        plt.xlabel(xlabel, fontweight='bold')
        plt.ylabel(ylabel, fontweight='bold')
        plt.legend(loc='upper left')
        plt.xticks(r2, x_month_list)

        cursor = mplcursors.cursor(hover=True)
        cursor.connect("add", self.annotate)

        plt.show()

