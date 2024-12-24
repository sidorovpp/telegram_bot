import pytds
import pandas as pd
import logging
import traceback
import concurrent.futures
import asyncio


class SQLExecuter:
    def __init__(self, server, database, user, password):
        self.server = server
        self.database = database
        self.user = user
        self.password = password

        self.connection = pytds.connect(self.server, self.database, self.user, self.password, as_dict=True)
        self.connection.cursor().execute("set transaction isolation level read uncommitted;")

    def get_connect(self):
        connection = pytds.connect(self.server, self.database, self.user, self.password, as_dict=True)
        connection.cursor().execute("set transaction isolation level read uncommitted;")
        return connection

    def get_result(self, sql, exec_empty):
        logging.info('execute: ' + sql)
        # with self.connection.cursor() as cur:
        with self.get_connect() as connection:
            # выполняем sql
            try:
                cursor = connection.cursor()
                cursor.execute(sql)
                # если пустой, то выходим
                if exec_empty:
                    connection.commit()
                    return None
                else:
                    res = cursor.fetchall()
                    connection.commit()

                return res
            except (Exception,) as E:
                logging.error(traceback.format_exc())
                connection.rollback()
                raise E

    async def exec(self, sql):
        logging.info('execute: ' + sql)
        # получаем данные асинхронно
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_result, sql, exec_empty=False)
            res = await asyncio.wrap_future(future)
        frame = pd.DataFrame(data=res)
        return frame

    async def exec_empty(self, sql):
        logging.info('execute: ' + sql)
        # получаем данные асинхронно
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_result, sql, exec_empty=True)
            await asyncio.wrap_future(future)
