import numpy as np # библиотека нампи
import pandas as pd # библиотека пандас
import matplotlib.pyplot as plt # библиотека матплотлиб для отрисовки
from IPython.display import clear_output # очистка вывода в ячейке
import datetime # модуль для работы с datetime
import warnings # библиотека сообщений по ошибкам
warnings.filterwarnings("ignore") # игнорировать сообщения ошибок
import  yfinance as yf

import requests # библиотека запросов
import io # библиотека для обработки бинарных данных

# запрос на получения csv файла по веб_адресу
url ="https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"
s = requests.get(url).content
companies_nasdaq = pd.read_csv(io.StringIO(s.decode('utf-8')))

print(companies_nasdaq.shape)
companies_nasdaq.head(10)

symbols = companies_nasdaq['Symbol'].tolist()
print(symbols)

idx = np.random.choice(companies_nasdaq.index)
ticker  = companies_nasdaq.loc[idx].Symbol
company = companies_nasdaq.loc[idx]['Company Name']
print(f'Берем данные по случайному тикеру {ticker} комании - {company}')

days = 1500
interval = "1d"
input_df = yf.download(ticker, period =  f"{days}d", interval=interval)
print(input_df.shape)
input_df.head()