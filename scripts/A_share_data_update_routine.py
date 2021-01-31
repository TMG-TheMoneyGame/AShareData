import sys

from AShareData import ConstLimitStockFactorCompositor, set_global_config, TDXData, TushareData

if __name__ == '__main__':
    # set_global_config(sys.argv[1])
    set_global_config("config.json")
    tushare_crawler = TushareData()
    tushare_crawler.update_base_info()
    tushare_crawler.get_shibor()

    tushare_crawler.get_ipo_info()
    tushare_crawler.get_company_info()
    tushare_crawler.update_hs_holding()
    tushare_crawler.get_hs_constitute()

    tushare_crawler.update_stock_names()
    tushare_crawler.update_dividend()

    tushare_crawler.update_index_daily()

    tushare_crawler.update_hk_stock_daily()

    tushare_crawler.update_fund_daily()
    tushare_crawler.update_fund_dividend()

    # with WindData() as wind_data:
    #     wind_data.update_stock_daily_data()
    #     wind_data.update_stock_adj_factor()
    #     wind_data.update_stock_units()
    #     wind_data.update_industry()
    #     wind_data.update_pause_stock_info()
    #
    #     wind_data.update_convertible_bond_daily_data()
    #     wind_data.update_future_daily_data()
    #     wind_data.update_stock_option_daily_data()

    # with JQData() as jq_data:
    #     jq_data.update_stock_morning_auction_data()

    with TDXData() as tdx_data:
        tdx_data.update_stock_minute()

    ConstLimitStockFactorCompositor().update()
