#!/usr/bin/python3

import re
import curses
import curses.textpad
import logging
from Fetcher import Fetcher
from ConfigFile import ConfigFile
from Fetcher import Fetcher
from Plotter import Plotter
from Database import Database

logger = logging.getLogger("econometrics")

class Dashboard:
    def __init__(self):
        # Instantiate the database class
        self.db = Database()
        self.db.create_config_table()
        curses.wrapper(self.dashboard)

    # Check the input only number or hyphen
    def is_digit(self,n):
        pattern = re.compile('[\d]')
        if pattern.match(n):
            return True
        return False

    # Check the input is alphanumerics
    def is_alphanum(self,n):
        pattern = re.compile('[\w]')
        if pattern.match(n):
            return True
        return False

    # Find the first match index
    def find_first_match(self, strings, pattern):
        compiled_pattern = re.compile(pattern)
        for string in strings:
            if compiled_pattern.match(string):
                return strings.index(string)
        return -1

    def enter_choice(self, plotter, config, fetcher, choice, sub_choice, \
            chart_choice):
        country_list = config.get_list_of_countries()
        chart_type_list = config.get_chart_type()
        indie_list = config.get_list_of_econs(country_list[choice])
        indie_code = config.get_indicator_code(country_list[choice], \
                indie_list[sub_choice])
        config_list = config.get_chart_configs(chart_type_list[chart_choice])

        date, actual, actual_format, forecast, revision =  \
                fetcher.request_data(indie_code)
        if chart_type_list[chart_choice] == "Seasonality": 
            if date and actual and forecast:
                title = country_list[choice] + " : " \
                        + indie_list[sub_choice] \
                        + " Seasonality"
                xlabel = "Month"
                ylabel = "Frequency"
                plotter.seasonality_template(title, xlabel, ylabel, date, \
                        forecast, actual)
        elif chart_type_list[chart_choice] == "Line":
            if date and actual:
                title1 = country_list[choice] + " : " \
                        + indie_list[sub_choice]
                title2 = title1 + " Average changes"
                xlabel = "Date"
                ylabel = indie_list[sub_choice]

                look_back_db = self.db.get_config_value(country_list[choice], \
                        indie_list[sub_choice], 'Plot data', \
                        chart_type_list[chart_choice])
                std_dev = self.db.get_config_value(country_list[choice], \
                        indie_list[sub_choice], 'Std. Dev.', \
                        chart_type_list[chart_choice])

                look_back = look_back_db if look_back_db != '' else '0'
                std_en = std_dev if std_dev != '' else 'off'

                if plotter.is_bond_data(indie_list[sub_choice]):
                    ir_list = []
                    btc_list = []

                    for i in actual_format:
                        if i:
                            rate,bid = i.split('|')
                            ir_list.append(float(rate))
                            btc_list.append(float(bid))
                        else:
                            ir_list.append(0.0)
                            btc_list.append(0.0)

                    ylabel = 'Bid-To-Cover ratio'
                    y2label = 'Interest Rate'

                    plotter.line_chart_template(title1, title2, xlabel, \
                            ylabel, date, btc_list, look_back, std_en, \
                            y2label, ir_list)
                else:
                    plotter.line_chart_template(title1, title2, xlabel, \
                            ylabel, date, actual, look_back, std_en)
        else:
            pass

    def draw_main_menu(self, window, color, title_pos, title, countries, \
            choice):
        window.border(0)
        window.addstr(0,title_pos,title)

        for i in range(len(countries)):
            if i == choice:
                window.attron(color)
                window.addstr(i + 1,2,countries[i])
                window.attroff(color)
            else:
                window.addstr(i + 1,2,countries[i])

    def draw_indi_menu(self, window, color, countries, indies, choice, \
            indi_choice):
        start_pos = 0
        end_pos = 0
        win_h, win_w = window.getmaxyx()
        max_indi = win_h - choice - 10

        if len(indies) > max_indi:
            end_pos = max_indi
        else:
            end_pos = len(indies)

        if indi_choice > max_indi - 1:
            start_pos = indi_choice - max_indi + 1
            end_pos = end_pos + start_pos

        for idx in range(start_pos, end_pos):
            x_pos = len(countries[choice]) + 3
            y_pos = choice + idx + 1 - start_pos
            if idx == indi_choice:
                window.attron(color)
                window.addstr(y_pos, x_pos, indies[idx])
                window.attroff(color)
            else:
                window.addstr(y_pos, x_pos, indies[idx])


    def draw_chart_menu(self, window, color, countries, indies, charts, \
            choice, indi_choice, chart_choice):
        win_h, win_w = window.getmaxyx() 
        max_indi = win_h - choice - 10

        # Draw the available chart type
        for ct_idx,c_type in enumerate(charts):
            chart_menu_x_pos = len(countries[choice]) + \
                    len(indies[indi_choice]) + 4

            chart_menu_y_pos = choice + indi_choice + ct_idx + 1
            if indi_choice > max_indi:
                chart_menu_y_pos = choice + max_indi + ct_idx

            if ct_idx == chart_choice:
                window.attron(color)
                window.addstr(chart_menu_y_pos,chart_menu_x_pos,c_type)
                window.attroff(color)
            else:
                window.addstr(chart_menu_y_pos,chart_menu_x_pos,c_type)

    def draw_configs_menu(self, window, title, color, width, height, braces, \
            config, config_list, config_tmp_list, configs_idx):
        
        title_pos = (width - len(title)) // 2
        window.border(0)
        window.addstr(0, title_pos, title)
        for i,cfg in enumerate(config_tmp_list):
            if i == configs_idx:
                window.addstr(i + 1, 1, cfg)
                window.attron(color)
                window.addstr(i + 1, width - len(braces) - 1, braces)
                window.addstr(i + 1, width - len(braces), config_tmp_list[cfg])
                window.attroff(color)
            else:
                window.addstr(i + 1, 1, cfg)
                window.addstr(i + 1, width - len(braces) - 1,braces)
                window.addstr(i + 1, width - len(braces), config_tmp_list[cfg])

        window.addstr(height - 4, 1, "'S' to save")
        window.addstr(height - 3, 1, "'R' to reset")
        window.addstr(height - 2, 1, "'Esc' to exit")

    def dashboard(self,stdscr):
        config = ConfigFile()
        fetcher = Fetcher()
        plotter = Plotter()

        choice_idx = 0
        subchoice_idx = 0
        chart_type_idx = 0
        configs_menu_idx = 0
        open_sub_menu = False
        select_chart_type = False
        configuration_menu = False
        box_width = 100
        box_height = 30

        # Initialize configuration menu
        config_menu_width = 22
        config_menu_height = 10
        config_menu_y_pos = (box_height - config_menu_height) // 2
        config_menu_x_pos = (box_width - config_menu_width) // 2 
        config_title = 'Configurations'
        config_title_pos = (config_menu_width - len(config_title)) // 2
        config_input_placeholder = '[   ]'
        off_text = 'off'
        on_text = 'on'
        input_text = ''
        input_toggle = ''

        # Clear screen
        stdscr.clear()
        curses.curs_set(False)
 
        # Initialize color pair
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)

        # Main menu box
        win1 = curses.newwin(box_height,box_width,0,0)
        win1.box()

        # Create a new for configuration box
        config_win = curses.newwin(config_menu_height, config_menu_width, \
                config_menu_y_pos, config_menu_x_pos)
        config_win.keypad(True)
        # Draw a box around the window
        config_win.box()

        # Set title
        title = "My Econometrics Dashboard"
        start_x_title = int((box_width - len(title)) // 2)

        country_list = config.get_list_of_countries()
        self.draw_main_menu(win1, curses.color_pair(1), start_x_title, title, \
                country_list,choice_idx)
        win1.refresh()

        stdscr.nodelay(True)
        win1.keypad(True)

        while True:
            # Wait for user input
            key = stdscr.getch()

            # Process user input
            if key == curses.KEY_UP and choice_idx > 0:
                choice_idx -= 1
            elif key == curses.KEY_DOWN and choice_idx < len(country_list) - 1:
                choice_idx += 1
            elif key == 27:
                break
            elif key == curses.KEY_RIGHT:
                sub_choice_idx = 0
                open_sub_menu = True
            else:
                pass
 
            search_text = ''
            while open_sub_menu:
                win1.clear()
                self.draw_main_menu(win1, curses.color_pair(1), \
                        start_x_title, title, country_list, \
                        choice_idx)

                indie_list = config.get_list_of_econs(country_list[choice_idx])
                # Draw the available economics indicator
                self.draw_indi_menu(win1, curses.color_pair(3), country_list, \
                        indie_list, choice_idx, sub_choice_idx)
                win1.refresh()
                c = win1.getch()

                if c == -1:
                    continue
                elif c == curses.KEY_UP and sub_choice_idx > 0:
                    sub_choice_idx -= 1
                    search_text = ''
                    continue
                elif c == curses.KEY_DOWN and \
                        sub_choice_idx < len(indie_list) - 1:
                    sub_choice_idx += 1
                    search_text = ''
                    continue
                elif c == curses.KEY_LEFT:
                    open_sub_menu = False
                    break
                elif c == curses.KEY_RIGHT:
                    select_chart_type = True
                    chart_type_idx = 0
                    search_text = ''
                elif c == 8 and len(search_text) > 0:
                    search_text = search_text[:-1]
                else:
                    if self.is_alphanum(chr(c)):
                        search_text += chr(c)
                        logger.info("Searching text : " + search_text)
                        # Search for the pattern in the indicator list
                        search_idx = self.find_first_match(indie_list, \
                                search_text)
                        if search_idx != -1:
                            sub_choice_idx = search_idx
                    continue

                while select_chart_type:
                    chart_type_list = config.get_chart_type()
                    # Draw the available chart type 
                    self.draw_chart_menu(win1, curses.color_pair(3), \
                            country_list, indie_list, chart_type_list, \
                            choice_idx, sub_choice_idx, chart_type_idx)
                    win1.refresh()
                    chart_key = win1.getch()

                    if chart_key == -1:
                        continue
                    elif chart_key == curses.KEY_UP and chart_type_idx > 0:
                        chart_type_idx -= 1
                        continue
                    elif chart_key == curses.KEY_DOWN and \
                            chart_type_idx < len(chart_type_list) - 1:
                        chart_type_idx += 1
                        continue
                    elif chart_key == ord('c'):
                        configuration_menu = True
                        configs_menu_idx = 0
                    elif chart_key == curses.KEY_LEFT:
                        select_chart_type = False
                        # Clear and redraw
                        win1.clear()
                        self.draw_main_menu(win1, curses.color_pair(1), \
                                start_x_title, title, country_list, choice_idx)
                        win1.refresh()
                        break
                    elif chart_key == curses.KEY_ENTER or chart_key == 10 or \
                            chart_key == 13:
                        self.enter_choice(plotter, config, fetcher, \
                                choice_idx, sub_choice_idx, chart_type_idx)
                        continue
                    else:
                        continue
                    
                    # Create an empty dictionary for storing the value
                    tmp_config = {}
                    while configuration_menu:
                        chart_list = config.get_chart_type()
                        config_list = config.get_chart_configs(chart_list[ \
                                chart_type_idx])
                        config_db_list = self.db.get_configs( \
                                country_list[choice_idx], \
                                indie_list[sub_choice_idx], \
                                chart_list[chart_type_idx])

                        if not tmp_config:
                            for i in config_list:
                                key_type = config.get_chart_configs_type(i)
                                if key_type == 'int':
                                    tmp_config[i] = '0'
                                elif key_type == 'toggle':
                                    tmp_config[i] = 'off'
                                else:
                                    tmp_config[i] = ''

                            for i in config_db_list:
                                for j in tmp_config:
                                    if i[0] == j:
                                        tmp_config[j] = i[1]

                            configs_menu_idx = 0

                        self.draw_configs_menu(config_win, config_title, \
                                curses.color_pair(3), config_menu_width, \
                                config_menu_height, config_input_placeholder, \
                                config, config_list, tmp_config, \
                                configs_menu_idx)
                        
                        config_win.refresh()
                        config_key = config_win.getch()

                        if config_key == -1 or config_key == curses.KEY_LEFT or \
                                config_key == curses.KEY_RIGHT:
                            continue
                        elif config_key == curses.KEY_UP:
                            if configs_menu_idx > 0:
                                configs_menu_idx -= 1
                            continue
                        elif config_key == curses.KEY_DOWN:
                            if configs_menu_idx < len(config_list) - 1:
                                configs_menu_idx += 1
                            continue
                        elif config_key in [ord('R'), ord('r')]:
                            self.db.remove_data(country_list[choice_idx], \
                                    indie_list[sub_choice_idx])
                            continue
                        elif config_key == 27:
                            configuration_menu = False
                            config_win.clear()
                            win1.clear()
                            self.draw_main_menu(win1, curses.color_pair(1), \
                                    start_x_title, title, country_list, \
                                    choice_idx)
                            self.draw_indi_menu(win1, curses.color_pair(3), \
                                    country_list, indie_list, choice_idx, \
                                    sub_choice_idx)
                            win1.refresh()
                            break
                        elif config_key == ord(' '):
                            input_cfg = \
                                    tmp_config[config_list[configs_menu_idx]]
                            if config.get_chart_configs_type( \
                                    config_list[configs_menu_idx]) == 'toggle':
                                if input_cfg == off_text:
                                    input_cfg = on_text
                                elif input_cfg == on_text:
                                    input_cfg = off_text
                                else:
                                    pass
                                tmp_config[config_list[configs_menu_idx]] = \
                                        input_cfg
                            else:
                                continue
                        elif config_key == ord('S'):
                            for i in tmp_config:
                                db_value = self.db.get_config_value( \
                                        country_list[choice_idx], \
                                        indie_list[sub_choice_idx], i, \
                                        chart_list[chart_type_idx])
                                if not db_value:
                                    self.db.config_table_insert( \
                                            country_list[choice_idx], \
                                            indie_list[sub_choice_idx], \
                                            chart_list[chart_type_idx], i, \
                                            tmp_config[i])
                                elif tmp_config[i] != db_value:
                                    self.db.update_config_value( \
                                            country_list[choice_idx], \
                                            indie_list[sub_choice_idx], \
                                            chart_list[chart_type_idx], \
                                            i, tmp_config[i])
                                else:
                                    pass
                        else:
                            if config.get_chart_configs_type( \
                                    config_list[configs_menu_idx]) == 'toggle':
                                continue
                            input_cfg = \
                                    tmp_config[config_list[configs_menu_idx]]
                            if self.is_digit(chr(config_key)) and \
                                    len(input_cfg) < 3:
                                input_cfg += chr(config_key)
                            elif config_key == 8:
                                input_cfg = input_cfg[:-1]
                            else:
                                pass

                            tmp_config[config_list[configs_menu_idx]] = \
                                    input_cfg
            
            # Clear and redraw
            win1.clear()
            self.draw_main_menu(win1, curses.color_pair(1), start_x_title, \
                    title, country_list, choice_idx)
            win1.refresh()
