from datetime import date
from Database import Database
import requests
from requests.exceptions import Timeout, ConnectionError
import logging
import json

logger = logging.getLogger("econometrics")

class Fetcher:
    def __init__(self):
        self.data_url = "https://www.forexfactory.com/calendar/graph/"
        self.db = Database()
        self.db.create_cache_table()

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
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; \
                    x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'}
            r = requests.get(url, headers=headers,timeout = 5)
            if r.status_code == 200:
                logger.info("Successfully fetched the data")
                # Caching the data
                self.db.cache_table_insert(url, r.content)
                return self.parse_json_data(r.content)
            else:
                logger.error("Unable to fetch the data")

        except Timeout:
            logger.error("Request timeout")
        except ConnectionError:
            logger.error("Connection Error")
        except requests.exceptions.RequestException as e:
            logger.error(str(e))

        return [],[],[],[],[]
