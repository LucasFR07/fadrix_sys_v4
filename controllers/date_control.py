from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone


def date_create():
    """
    Padroniza a criação de datas em (Datetime) dentro fuso horário definido.
    Para exibir a data em formato padrão BR usar a função string = .strftime('%d/%m/%Y %H:%M:%S')
    """

    date_now = datetime.now()
    date_timezone = timezone('America/Sao_Paulo')
    date_create = date_now.astimezone(date_timezone)
    return date_create


def date_differenceCALC(days:int) -> datetime:
    today = date.today()
    calc = today - relativedelta(days=days)
    return {"initial": today, "final": calc}


def date_differenceCALC_30D():
    today = date.today()
    calc1 = today - relativedelta(days=15)
    calc2 = calc1 - relativedelta(days=15)
    return [{'start': today, 'end': calc1}, {'start': calc1, 'end': calc2}]


def date_today(lastday:int=0) -> datetime:
    today = datetime.today()
    today_init = today - relativedelta(days=lastday, hour=0, minute=0, second=0, microsecond=0)
    today_final = today + relativedelta(days=-lastday, hour=23, minute=59, second=59, microsecond=0)
    return {"initial": today_init, "final": today_final}


def date_weekdayCALC():
    today = date.today()
    weekDay = date.weekday(today)
    calc = weekDay+2
    return int(calc)


def date_subtractdaysCALC(days:int):
    today = date.today()
    calc = [today - timedelta(days=idx) for idx in range(days)]
    return calc
    # return {"initial": calc[0], "final": calc[len(calc)-1]}


def date_differenceCALC_SHOPEE():

    """ Retorna um intervalo de datas (de/para) dentro de uma faixa de 15 dias até chegar no dia atual. """

    today = date.today()
    list_interval = list()

    for day in range(1, today.day, 14):
        list_interval.append(today - relativedelta(day=day))

    qty_interval = len(list_interval)
    if list_interval[qty_interval-1].day != today.day:
        list_interval.append(list_interval[qty_interval-1] + relativedelta(days=1))
        list_interval.append(today + relativedelta(days=1))

    return list_interval


def date_range_60D():
    """ Calculo de datas num intervalo de 60 dias. """

    setp = 4
    today = date.today()
    list_range = list()
    list_range.append(today)

    for _ in range(1, setp):

        if len(list_range) == 0:
            calc = today - relativedelta(days=15)
            list_range.append(calc)
        
        else:
            calc = list_range[len(list_range)-1] - relativedelta(days=15)
            list_range.append(calc)        


    print(list_range)
