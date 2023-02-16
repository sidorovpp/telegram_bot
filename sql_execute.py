import pytds
import pandas as pd
import logging
import traceback


class SQLExecuter:
    def __init__(self, server, database, user, password):
        self.server = server
        self.database = database
        self.user = user
        self.password = password

        self.connection = pytds.connect(self.server, self.database, self.user, self.password, as_dict=True)
        self.connection.cursor().execute("set transaction isolation level read uncommitted;")

    def try_reconnect(self):
        try:
            self.connection = pytds.connect(self.server, self.database, self.user, self.password, as_dict=True)
            self.connection.cursor().execute("set transaction isolation level read uncommitted;")
        except (Exception,):
            logging.error(traceback.format_exc())

    def exec(self, sql):
        logging.info('execute: ' + sql)
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql)
                res = cur.fetchall()
                frame = pd.DataFrame(data=res)
                self.connection.commit()
                return frame
        except (Exception,) as E:
            logging.error(traceback.format_exc())
            self.connection.rollback()
            self.try_reconnect()
            raise E
        # logging.info('execute: ' + sql)
        # try:
        #     frame = pd.read_sql(sql, self.connection)
        #     self.connection.commit()
        #     return frame
        # except (Exception,) as E:
        #     logging.error(traceback.format_exc())
        #     self.connection.rollback()
        #     self.try_reconnect()
        #     raise E

    def exec_empty(self, sql):
        logging.info('execute: ' + sql)
        try:
            self.connection.cursor().execute(sql)
            self.connection.commit()
        except (Exception,) as E:
            logging.error(traceback.format_exc())
            self.connection.rollback()
            self.try_reconnect()
            raise E
