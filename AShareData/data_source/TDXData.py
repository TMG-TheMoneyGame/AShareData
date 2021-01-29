import datetime as dt
from collections import OrderedDict

import pandas as pd
from pytdx.hq import TdxHq_API
from tqdm import tqdm

from .DataSource import DataSource
from .. import utils
from ..config import get_global_config
from ..DBInterface import DBInterface
from ..Tickers import StockTickers


class TDXData(DataSource):
    def __init__(self, db_interface: DBInterface = None, host: str = None, port: int = None):
        super().__init__(db_interface)
        if host is None:
            conf = get_global_config()
            host = conf['tdx_server']['host']
            port = conf['tdx_server']['port']
        self.api = TdxHq_API()
        self.host = host
        self.port = port
        self._factor_param = utils.load_param('tdx_param.json')
        self.stock_ticker = StockTickers(db_interface)

    def connect(self):
        self.api.connect(self.host, self.port)

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.disconnect()

    def update_stock_minute(self):
        table_name = '股票分钟行情'
        db_timestamp = self._check_db_timestamp(table_name, dt.datetime(2015, 1, 1))
        start_date = self.calendar.offset(db_timestamp.date(), 1)
        end_date = dt.datetime.today()
        dates = self.calendar.select_dates(start_date, end_date)
        for date in dates:
            self.get_stock_minute(date)

    def get_stock_minute(self, date: dt.datetime) -> None:
        minute_data = self._get_stock_minute(date)
        auction_time = date + dt.timedelta(hours=9, minutes=25)
        auction_db_data = self.db_interface.read_table('股票集合竞价数据', columns=['成交价', '成交量', '成交额'], dates=[auction_time])
        df = self.left_shift_minute_data(minute_data=minute_data, auction_db_data=auction_db_data)

        self.db_interface.insert_df(df, '股票分钟行情')

    def _get_stock_minute(self, date: dt.datetime) -> pd.DataFrame:
        num_days = self.calendar.days_count(date, dt.date.today())
        start_index = num_days * 60 * 4
        tickers = self.stock_ticker.ticker(date)

        storage = []
        with tqdm(tickers) as pbar:
            for ticker in tickers:
                pbar.set_description(f'下载 {ticker} 在 {date} 的分钟数据')
                code, market = self._split_ticker(ticker)
                data = self.api.get_security_bars(category=8, market=market, code=code, start=start_index, count=240)
                data = self._formatting_data(data, ticker)
                storage.append(data)
                pbar.update()

        df = pd.concat(storage)
        return df

    def _formatting_data(self, info: OrderedDict, ticker: str) -> pd.DataFrame:
        df = pd.DataFrame(info)
        df['datetime'] = df['datetime'].apply(self.str2datetime)
        df = df.drop(['year', 'month', 'day', 'hour', 'minute'], axis=1).rename(self._factor_param['行情数据'], axis=1)
        df['ID'] = ticker

        df = df.set_index(['DateTime', 'ID'], drop=True)
        return df

    @staticmethod
    def _split_ticker(ticker: str) -> [str, int]:
        code, market_str = ticker.split('.')
        market = 0 if market_str == 'SZ' else 1
        return code, market

    @staticmethod
    def str2datetime(date: str) -> dt.datetime:
        return dt.datetime.strptime(date, '%Y-%m-%d %H:%M')
