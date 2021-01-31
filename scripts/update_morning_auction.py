import datetime as dt
import sys

# from DingTalkMessageBot import DingTalkMessageBot

from AShareData import set_global_config, TushareData

if __name__ == '__main__':
    config_loc = sys.argv[1]
    set_global_config(config_loc)

    tushare_crawler = TushareData()
    tushare_crawler.get_ipo_info()

    # messenger = DingTalkMessageBot.from_config(config_loc, '自闭')
    # try:
    #     with JQData() as jq_data:
    #         date = dt.date.today()
    #         jq_data.stock_open_auction_data(date)
    #         messenger.send_message(f'{date} 集合竞价数据已下载.')
    # except:
    #     messenger.send_message(f'{date} 集合竞价数据下载失败.')
