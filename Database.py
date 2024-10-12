#!/usr/bin/python3

import sqlite3
import logging

logger = logging.getLogger('econometrics')

class Database:
    def __init__(self):
        db_path = 'local.db'
        self.con = sqlite3.connect(db_path)
        self.cache = sqlite3.connect(':memory:')

    def __del__(self):
        if self.con is not None:
            self.con.close()

        if self.cache is not None:
            self.cache.close()

    # Create cache database on RAM
    def create_cache_table(self):
        cur = self.cache.cursor()
        res = cur.execute('CREATE TABLE IF NOT EXISTS \
        cache_table(id integer primary key, url, data)')
        self.cache.commit()

    # Insert data into cache_table
    def cache_table_insert(self, url, data):
        cur = self.cache.cursor()
        cur.execute('INSERT INTO cache_table(url, data) VALUES(?, ?)', \
                (url, data,))
        self.cache.commit()

    # Get data from cache_table
    def get_cache_data(self, url):
        cur = self.cache.cursor()
        res = cur.execute('SELECT data FROM cache_table WHERE url = ?', \
                (url,))
        result = res.fetchone()
        if result:
            return result[0]

        return ''

    # Create configuration table if not exists
    def create_config_table(self):
        cur = self.con.cursor()
        res = cur.execute('CREATE TABLE IF NOT EXISTS \
        configs_table(id integer primary key, country, indicator, \
                chart_type, chart_config, value)')
        self.con.commit()
 
    # Insert data into config_table
    def config_table_insert(self, country, indicator, chart_type, config, \
            value):
        cur = self.con.cursor()
        cur.execute('INSERT INTO configs_table(country, indicator, \
                chart_type, chart_config, value) VALUES(?, ?, ?, ?, ?)', \
                (country, indicator, chart_type, config, value,))
        self.con.commit()

    # Get config by country and indicator
    def get_configs(self, country, indicator, chart_type):
        configs_list = []
        cur = self.con.cursor()
        res = cur.execute('SELECT chart_config, value FROM configs_table \
                WHERE country = ? AND indicator = ? AND chart_type = ?', \
                (country, indicator, chart_type,))
        for i in res.fetchall():
            tmp_tuple = (i[0], i[1],)
            configs_list.append(tmp_tuple)

        return configs_list

    # Get config value by country, indicator and chart_config
    def get_config_value(self, country, indicator, chart_config, chart_type):
        cur = self.con.cursor()
        res = cur.execute('SELECT value FROM configs_table WHERE country = ? \
                AND indicator = ? AND chart_config = ? AND chart_type = ?', \
                (country, indicator, chart_config, chart_type,))
        result = res.fetchone()
        if result:
            return result[0]

        return ''

    # Update config value
    def update_config_value(self, country, indicator, chart_type, \
            chart_config, data):
        cur = self.con.cursor()
        cur.execute('UPDATE configs_table SET value = ? WHERE country = ? \
                AND indicator = ? AND chart_config = ? AND chart_type = ?', \
                (data, country, indicator, chart_config, chart_type,))
        self.con.commit()

    # Remove the data from the config_table
    def remove_data(self, country, indicator):
        cur = self.con.cursor()
        cur.execute('DELETE FROM configs_table WHERE country = ? AND \
                indicator = ?',(country, indicator,))
        self.con.commit()
