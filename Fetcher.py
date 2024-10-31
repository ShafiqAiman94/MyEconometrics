from seleniumwire import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from datetime import date
from Database import Database
import logging
import json
from ConfigFile import ConfigFile
import subprocess
# Compression library
import brotli
import gzip
import zlib

EDGE = "Microsoft Edge WebDriver"
CHROME = "ChromeDriver"
GECKO = "geckodriver"

logger = logging.getLogger("econometrics")

class Fetcher:
    def __init__(self):
        self.data_url = "https://www.forexfactory.com/calendar/graph/"
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 \
            Safari/537.36'

        self.db = Database()
        self.db.create_cache_table()
        options = None
        service = None
        self.driver = None

        self.config = ConfigFile()
        driver_type = self.get_webdriver_type(self.config.get_webdriver_path())
        logger.info('Using webdriver : ' + driver_type)

        if driver_type == EDGE:
            options = EdgeOptions()
            service = \
            EdgeService(executable_path=self.config.get_webdriver_path())
        elif driver_type == CHROME:
            options = ChromeOptions()
            service = \
                ChromeService(executable_path=self.config.get_webdriver_path())
        elif driver_type == GECKO:
            options = FirefoxOptions()
            service = \
                FirefoxService(executable_path=self.config.get_webdriver_path())

        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        seleniumwire_options = {
            'headers' : {
                'User-Agent': user_agent
            }
        }

        if driver_type == EDGE:
            self.driver = webdriver.Edge(service=service, options=options, \
                                         seleniumwire_options= \
                                         seleniumwire_options)
        elif driver_type == CHROME:
            self.driver = webdriver.Chrome(service=service, options=options, \
                                           seleniumwire_options= \
                                           seleniumwire_options)
        elif driver_type == GECKO:
            self.driver = webdriver.Firefox(service=service, options=options, \
                                            seleniumwire_options= \
                                            seleniumwire_options)

    def __del__(self):
        if self.driver:
            self.driver.close()

    def get_webdriver_type(self, webdriver_path):
        """ Function to get the webdriver path """
        result = subprocess.run([webdriver_path,'--version'], \
                                capture_output=True, text=True)
        if EDGE in result.stdout:
            return EDGE
        elif CHROME in result.stdout:
            return CHROME
        elif GECKO in result.stdout:
            return GECKO
        else:
            return ""

    def parse_json_data(self,response_data):
        date_list = []
        actual_list = []
        actual_format_list = []
        forecast_list = []
        revision_list = []

        data = json.loads(response_data)
        for event in data['data']['events']:
            date_list.append(event['dateline'])
            actual_list.append(event['actual'])
            actual_format_list.append(event['actual_formatted'])
            forecast_list.append(event['forecast'])
            revision_list.append(event['revision'])

        return date_list, actual_list, actual_format_list, forecast_list, \
                revision_list

    def get_number_months(self):
        now = date.today()
        start_date = date(2000,1,1)
        return (now.year - start_date.year) * 12 + now.month - start_date.month

    def request_data(self,code):
        limit = self.get_number_months()
        url = self.data_url + code + "?limit=" + str(limit)
        logger.info("Requesting data from : " + url)
        data = self.db.get_cache_data(url)

        if data:
            logger.info("Data already in cache")
            return self.parse_json_data(data)

        try :
            status_code = 303
            response_body = None
            response_header = None

            self.driver.get(url)
            pat = r'www.forexfactory.com/calendar/graph/'
            self.driver.wait_for_request(pat, timeout=5)
            for request in self.driver.requests:
                if request.response and request.url == url:
                    status_code = request.response.status_code
                    response_body = request.response.body
                    response_header = request.response.headers
                    break

            if status_code == 200:
                data = None

                logger.info('Successfully fetched the data')
                logger.debug(response_header['Content-Encoding'])

                if response_header['Content-Encoding'] == 'br':
                    data = brotli.decompress(response_body)
                elif response_header['Content-Encoding'] == 'gzip':
                    data = gzip.decompress(response_body)
                elif response_header['Content-Encoding'] == 'deflate':
                    data = zlib.decompress(response_body)
                else:
                    logger.info('Encoding cannot be found!')
                    logger.info(response_header['Content-Encoding'])
                    pass

                if data:
                    self.db.cache_table_insert(url, data)
                    return self.parse_json_data(data)
            else:
                logger.error('Unable to fetch the data')

        except Exception as e:
            logger.error(str(e))

        return [],[],[],[],[]
