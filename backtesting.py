import numpy as np # библиотека нампи
import pandas as pd # библиотека пандас
import matplotlib.pyplot as plt # библиотека матплотлиб для отрисовки
from IPython.display import clear_output # очистка вывода в ячейке
import datetime # модуль для работы с datetime
import warnings # библиотека сообщений по ошибкам
warnings.filterwarnings("ignore") # игнорировать сообщения ошибок
import  yfinance as yf

clear_output()
amzn = yf.Ticker("AMZN")

# можно получить данные минутные данные, но за последние 7 дней только
now = datetime.datetime.now()
past = datetime.datetime.now() - datetime.timedelta(days=5)
amzn_1_minute = amzn.history(start=past.strftime('%Y-%m-%d'),
                             end=now.strftime('%Y-%m-%d'),
                             interval="1m") # 1 минута
amzn_1_minute.head(5)

# можно ввести текущий день с помощь datetime
end_date = datetime.datetime.now().strftime('%Y-%m-%d')
amzn.history(start="2022-11-15", end= end_date, interval="1h") # 1 час

# можно получить и максимальные данные
amzn.history(period="max").head(5)

# можно отключить дивиденды
amzn.history(period="max", actions=False).head(5)

# dividends, splits
print(amzn.actions)

# show dividends
print(amzn.dividends)

# show splits
print(amzn.splits)

amzn.major_holders

amzn.institutional_holders

# yf.download()

data = yf.download("AMZN AAPL GOOG", start="2017-01-01", end="2017-04-30")
data.head()

# можно сгруппирввать по акции
data = yf.download("AMZN AAPL GOOG", start="2017-01-01",
                    end="2017-04-30", group_by='tickers')
data.head()

# получаем данные  за 60 дней с интервалом 15 минут
df_amzn = amzn.history(interval='15m', period='60d')

# далее агрегируем эти данные в 45-минутные бары:
df_45min = df_amzn.groupby(pd.Grouper(freq='45Min')).agg({"Open": "first",
                                                          "High": "max",
                                                          "Low": "min",
                                                          "Close": "last",
                                                          "Volume": "sum"})

df_45min.head()

# далее агрегируем эти данные в 20ти-минутные бары:
df_20min = df_amzn.groupby(pd.Grouper(freq='20Min')).agg({"Open": "first",
                                                      "High": "max",
                                                      "Low": "min",
                                                      "Close": "min",
                                                      "Volume": "sum"})

df_20min.head()

df_wiki = pd.read_html("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
df_wiki.head(10)

idx = np.random.choice(df_wiki.index) # берем случайный индекс
tiker  = df_wiki.loc[idx].Symbol # берем тикер по индексу
company = df_wiki.loc[idx].Security   # наодим по тиеру компанию
print(f'Берем данные по случайному тикеру {tiker} комании - {company}')


days = 700
# грузим датасет выбранного тикера
sample_df = yf.download(tiker, period =  f"{days}d", interval="1h", actions=False)
sample_df.head()