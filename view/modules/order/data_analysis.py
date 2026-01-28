from controllers.date_control import *
import pandas as pd

from pathlib import PureWindowsPath


class OrderAnalysis():

    def __init__(self, period:int):
        self.period = period
        self.path_db = PureWindowsPath('C:/Users/marketing/Downloads/V4/FSYS_DB.db')
        self.__dbOrder = pd.read_sql_table("orderV2", f"sqlite:///{self.path_db}")
        self.__dbProduct = pd.read_sql_table("order_product", f"sqlite:///{self.path_db}")


    def total_sales(self, channel:str=None, fild_date:bool=False):
        """ Returns total sales in a given period. """
        if fild_date == True:
            self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_dateImport"]).dt.date
        else:
            self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS >  total_sales() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')
            self.count_data = query_channel["id"].count()
            # print(f'ORDER_ANALYSIS >  total_sales() ==> self.count_data: {self.count_data}') ##DEBUG
            return self.count_data
        else:
            self.count_data = self.filtered["id"].count()
            # print(f'ORDER_ANALYSIS >  total_sales() ==> self.count_data: {self.count_data}') ##DEBUG
            return self.count_data


    def query_sales(self, channel:str=None, limit:int=15, offset:int=0):
        """ Returns the total number of orders to be shipped today. """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_dateImport"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > query_sales() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')
            df = pd.DataFrame(query_channel).sort_index(ascending=False).iloc[offset:limit] if limit != None else pd.DataFrame(query_channel).sort_index(ascending=False)
            return df
        else:
            df = pd.DataFrame(self.filtered).sort_index(ascending=False).iloc[offset:limit] if limit != None else pd.DataFrame(self.filtered).sort_index(ascending=False)
            return df


    def total_weekSales(self, channel:str=None):
        """ Returns the total sales for the week, starting with Sunday as the first day of the week, up to the current day, with Saturday being the last day of the week. """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=date_weekdayCALC())
        # print(f'ORDER_ANALYSIS > total_weekSales() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')["id"].count()
            # print(f'ORDER_ANALYSIS > total_weekSales() ==> query_channel: {query_channel}') ##DEBUG
            return query_channel
        else:
            self.count_data = self.filtered["id"].count()
            # print(f'ORDER_ANALYSIS > total_weekSales() ==> self.count_data: {self.count_data}') ##DEBUG
            return self.count_data


    # def total_by_channel(self, channel:str=None):
    #     """ Returns total sales per channel in a given period """
    #     self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
    #     calc_period = date_differenceCALC(days=self.period)
    #     # print(f'ORDER_ANALYSIS > total_by_channel() ==> calc_period: {calc_period}') ##DEBUG
    #     filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
    #     self.filtered = self.__dbOrder.loc[filter_period]
    #     if channel != None:
    #         query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby("order_channel")["order_channel"].count()
    #         # print(f'ORDER_ANALYSIS > total_by_channel() ==> query_channel: {query_channel}') ##DEBUG
    #         df = pd.DataFrame(query_channel)
    #         return df
    #     else:
    #         self.count_data = self.filtered.groupby("order_channel")["order_channel"].count().sort_values()
    #         # print(f'ORDER_ANALYSIS > total_by_channel() ==> self.count_data: {self.count_data}') ##DEBUG
    #         df = pd.DataFrame(self.count_data)
    #         return df


    def total_by_channel(self, channel:str=None):
        """ Returns total sales per channel in a given period """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > total_by_channel() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby(["order_channel", "order_company"])["order_channel"].count()
            # print(f'ORDER_ANALYSIS > total_by_channel() ==> query_channel: {query_channel}') ##DEBUG
            df = pd.DataFrame(query_channel)
            return df
        else:
            self.count_data = self.filtered.groupby(["order_channel", "order_company"])["order_channel"].count().sort_values()
            # print(f'ORDER_ANALYSIS > total_by_channel() ==> self.count_data: {self.count_data}') ##DEBUG
            df = pd.DataFrame(self.count_data)
            return df



    def total_by_user(self, channel:str=None):
        """ Returns the total sales per customer service user. """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > total_by_user() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby("order_userSystem")["order_userSystem"].count().sort_values()
            # print(f'ORDER_ANALYSIS > total_by_user() ==> query_channel: {query_channel}') ##DEBUG
            df = pd.DataFrame(query_channel)
            return df
        else:
            self.count_data = self.filtered.groupby("order_userSystem")["order_userSystem"].count().sort_values()
            # print(f'ORDER_ANALYSIS > total_by_user() ==> self.count_data: {self.count_data}') ##DEBUG
            df = pd.DataFrame(self.count_data)
            return df


    def total_shippingDay(self, channel:str=None, last_day:bool=False):
        """ Returns the total number of orders to be shipped today. """
        # self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_shippingDate"])
        self.__dbOrder['order_shippingDateMKP'] = pd.to_datetime(self.__dbOrder["order_shippingDateMKP"])
        calc_period = date_today() if not last_day else date_today(1)
        # print(f'\nDATA_ANALISYS > total_shippingDay() ==> PERIOD: {calc_period}\n') ##DEBUG
        filter_period = (self.__dbOrder['order_shippingDateMKP'] <= calc_period["final"]) & (self.__dbOrder['order_shippingDateMKP'] >= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]

        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')
            self.count_data = query_channel["id"].count()
            # print(f'\nDATA_ANALISYS > total_shippingDay() ==> COUNT CHANNEL: {self.count_data}\n') ##DEBUG
            return self.count_data
        else:
            self.count_data = self.filtered["id"].count()
            # print(f'DATA_ANALISYS > total_shippingDay() ==> COUNT: {self.count_data}\n') ##DEBUG
            return self.count_data


    def query_shippingDay(self, channel:str=None, day:int=None):
        """ Returns the total number of orders to be shipped today. """
        # self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_shippingDate"])
        self.__dbOrder['order_shippingDateMKP'] = pd.to_datetime(self.__dbOrder["order_shippingDateMKP"])
        calc_period = date_today() if day == None else date_today(day)
        # print(f'\nDATA_ANALISYS > total_shippingDay() ==> PERIOD: {calc_period}\n') ##DEBUG
        filter_period = (self.__dbOrder['order_shippingDateMKP'] <= calc_period["final"]) & (self.__dbOrder['order_shippingDateMKP'] >= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        self.filtered.sort_values(by='order_shippingDateMKP', inplace=True)
        # print(f'\nDATA_ANALISYS > total_shippingDay() ==> SELF.FILTERED: {self.filtered}\n') ##DEBUG
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')
            df = pd.DataFrame(query_channel)
            return df
        else:
            df = pd.DataFrame(self.filtered)
            return df


    def query_orderStatus(self, status:str=None, channel:str=None):
        """ Returns the total number of orders to be shipped today. """

        filter_status = self.__dbOrder.query('order_status!="Cancelado" and order_status!="Importado"') if status==None else self.__dbOrder.query(f'order_status=="{status}"')
        if filter_status.empty:
            print("\n❌ DATA_ANALYSIS > query_orderStatus() ==> FILTER_STATUS: Não encontrado pedidos com status de pendência.\n") ##DEBUG
            return None

        if channel != None:
            filter_channel = filter_status.query(f'order_channel=="{channel}"')
            if filter_channel.empty:
                print(f"\n❌ DATA_ANALYSIS > query_orderStatus() ==> FILTER_CHANNER: Não encontrado pedidos com status de pendência para o canal de venda {channel}.\n") ##DEBUG
                return None

            df = pd.DataFrame(filter_channel)
            return df

        else:
            df = pd.DataFrame(filter_status)
            return df


    def query_duplicate(self, channel:str=None):
        """ Returns orders duplicate. """
        # self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_dateImport"]).dt.date
        # calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > query_sales() ==> calc_period: {calc_period}') ##DEBUG
        # filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        # self.filtered = self.__dbOrder.loc[filter_period]        

        if channel != None:
            filter_channel = self.__dbOrder.query(f'order_channel=="{channel}"')
            if filter_channel.empty:
                print(f"\n❌ DATA_ANALYSIS > query_duplicate() ==> FILTER_CHANNER: Não encontrado pedidos duplicados para o canal de venda {channel}.\n") ##DEBUG
                return None

            df = pd.DataFrame(filter_channel.order_number.value_counts())
            return df

        else:
            df = pd.DataFrame(self.__dbOrder.order_number.value_counts())
            return df


    def evolution_by_channel(self, channel:str=None):
        """ Returns the evolution of sales by channel within a specified period. """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby(["order_channel", 'date_formatted'])["order_channel"].count()
            # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> query_channel: {query_channel}') ##DEBUG
            df = pd.DataFrame(query_channel)
            return df
        else:
            self.count_data = self.filtered.groupby(["order_channel", 'date_formatted'])["order_channel"].count()
            # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> self.count_data: {self.count_data}') ##DEBUG
            df = pd.DataFrame(self.count_data)
            return df


    ## EVOLUÇÃO SEPARADO POR CONTA DE MARKETPLACE
    # def evolution_by_channel(self, channel:str=None):
    #     """ Returns the evolution of sales by channel within a specified period. """
    #     self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
    #     calc_period = date_differenceCALC(days=self.period)
    #     # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> calc_period: {calc_period}') ##DEBUG
    #     filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
    #     self.filtered = self.__dbOrder.loc[filter_period]
    #     if channel != None:
    #         query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby(["order_channel", "order_company", 'date_formatted'])["order_channel"].count()
    #         # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> query_channel: {query_channel}') ##DEBUG
    #         df = pd.DataFrame(query_channel)
    #         return df
    #     else:
    #         self.count_data = self.filtered.groupby(["order_channel", "order_company", 'date_formatted'])["order_channel"].count()
    #         # print(f'ORDER_ANALYSIS > evolution_by_channel() ==> self.count_data: {self.count_data}') ##DEBUG
    #         df = pd.DataFrame(self.count_data)
    #         return df



    def moda_product(self, channel:str=None):
        """ ------- """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > moda_product() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"')
            # print(f'ORDER_ANALYSIS > moda_product() ==> query_channel: {query_channel}') ##DEBUG
            df_order = pd.DataFrame(query_channel)
        else:
            df_order = pd.DataFrame(self.filtered)

        df_product = pd.DataFrame(self.__dbProduct)
        merge_orderProduct = pd.merge(
            left=df_order,
            right=df_product,
            how="left",
            on=["order_number"]
        )
        mode_products = pd.pivot_table(merge_orderProduct,index=['sku'], values='qty', aggfunc='sum').sort_values(ascending=False,by='qty')[:100]
        df_mode = pd.DataFrame(mode_products)
        return df_mode


    def moda_buyer(self, channel:str=None):
        """ ------ """
        self.__dbOrder['date_formatted'] = pd.to_datetime(self.__dbOrder["order_date"]).dt.date
        calc_period = date_differenceCALC(days=self.period)
        # print(f'ORDER_ANALYSIS > moda_buyer() ==> calc_period: {calc_period}') ##DEBUG
        filter_period = (self.__dbOrder['date_formatted'] >= calc_period["final"]) & (self.__dbOrder['date_formatted'] <= calc_period["initial"])
        self.filtered = self.__dbOrder.loc[filter_period]
        if channel != None:
            query_channel = self.filtered.query(f'order_channel=="{channel}"').groupby("order_customer")["order_customer"].count().sort_values(ascending=False)[:10]
            # print(f'ORDER_ANALYSIS > moda_product() ==> query_channel: {query_channel}') ##DEBUG
            df = pd.DataFrame(query_channel)
            return df
        else:        
            self.count_data = self.filtered.groupby("order_customer")["order_customer"].count().sort_values(ascending=False)[:10]
            df_buyer = pd.DataFrame(self.count_data)
            return df_buyer
