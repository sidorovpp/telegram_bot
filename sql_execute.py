import pyodbc
import pandas as pd
import logging
import traceback


class SQLExecuter:
    def __init__(self, connect_string):
        pass
        self.connect_string = connect_string
        self.connection = pyodbc.connect(self.connect_string)
        self.connection.execute("set transaction isolation level read uncommitted;")

    def try_reconnect(self):
        try:
            self.connection = pyodbc.connect(self.connect_string)
            self.connection.execute("set transaction isolation level read uncommitted;")
        except (Exception,):
            logging.error(traceback.format_exc())

    def exec(self, sql):
        logging.info('execute: ' + sql)
        try:
            frame = pd.read_sql(sql, self.connection)
            self.connection.commit()
            return frame
        except (Exception,) as E:
            logging.error(traceback.format_exc())
            self.connection.rollback()
            self.try_reconnect()
            raise E

    def exec_empty(self, sql):
        logging.info('execute: ' + sql)
        try:
            self.connection.execute(sql)
            self.connection.commit()
        except (Exception,) as E:
            logging.error(traceback.format_exc())
            self.connection.rollback()
            self.try_reconnect()
            raise E
