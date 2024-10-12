import json
import logging

logger = logging.getLogger("econometrics")

class ConfigFile:
    def __init__(self):
        self.file_name = "Config.json"
        json_file = open(self.file_name,'r')
        self.data = json.load(json_file)
        json_file.close()

    def get_chart_configs(self, key):
        """ Get the list of chart configs in the data file """
        chart_configs = []

        for chart in self.data['Charts'][key]:
            chart_configs.append(chart)

        return chart_configs

    def get_chart_configs_type(self,key):
        """ Get the type of a chart config in the data file """
        return self.data[key]

    def get_chart_type(self):
        """ Get the list of chart types in the data file """
        chart_type = []
        for chart in self.data['Charts'].keys():
            chart_type.append(chart)

        return chart_type

    def get_list_of_countries(self):
        """ Get the list of countries in the data file """
        country_list = []
        for country in self.data['Countries'].values():
            country_list.append(country)

        return sorted(country_list)

    def get_list_of_econs(self,country):
        """ Get the list of econs in the data file """
        indie_list = []
        for indie,code in self.data[country].items():
            indie_list.append(indie)

        return sorted(indie_list)

    def get_indicator_code(self,country,indicator_name):
        """ Get the code of an indicator in the data file """
        code = ""
        for indie,indie_code in self.data[country].items():
            if indie == indicator_name:
                code = indie_code
                break

        return code
