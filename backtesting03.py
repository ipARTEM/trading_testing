import numpy as np # библиотека нампи
import pandas as pd # библиотека пандас
from IPython.display import clear_output # очистка вывода в ячейке
import datetime # модуль для работы с datetime
import warnings # библиотека сообщений по ошибкам
warnings.filterwarnings("ignore") # игнорировать сообщения ошибок
import  yfinance as yf

import requests # библиотека запросов
import io # библиотека для обработки бинарных данных

import matplotlib.pyplot as plt     # метод отрисовки в matplotlib
import matplotlib.colors as mcolors # палитра для графика в matplotlib
import matplotlib.dates as mdates  # для отображения дат в matplotlib
import matplotlib.cbook as cbook



class Show_OHCL():
      def __init__(self,
                   figsize=(16, 10),
                   style_plot = 'dark_background'):

           """
           figsize - размер поля для отрисовки графиков
           style_plot - стиль графика, доступные можно проверить
                        через plt.style.available
           """
           self.figsize = figsize
           self.style_plot = style_plot

      def adj_close(self, df):
          """
          typical price
          (df['High'] + df['Low'] + df['Close']) / 3
          """
          return (df['High'] + df['Low'] + df['Close']) / 3


      def geom_close(self, df: pd.DataFrame):
          """
          Построение typical price
          """
          copy = df.copy()
          copy['Geom Close'] =  (copy['High']*copy['Low']*copy['Close'])**(1/3)
          return copy


      def add_bollinger_bands(self, df: pd.DataFrame, n:int, m:float):
          """
          takes dataframe on input
          n = окно сглаживания
          m = количество стандартных отклонений от матожидания
          """
          # try:
             #data = df['Close']
          #except:
             #data = self.adj_close(df)['Close']

          data = self.geom_close(df)['Geom Close']

          # takes one column from dataframe
          B_MA = pd.Series((data.rolling(n).mean()), name='B_MA') #, min_periods=n
          sigma = data.rolling(n).std() # min_periods=n

          BU = pd.Series((B_MA + m * sigma), name='BU')
          BL = pd.Series((B_MA - m * sigma), name='BL')

          # собираем в датафрейм
          df = df.join(B_MA)
          df = df.join(BU)
          df = df.join(BL)

          return df

      def bb_signals(self, df, n, m, frq = 'weekly'):
          '''
          frq = 'weekly' bkb 'daily'
          n = smoothing length
          m = number of standard deviations away from MA
          '''

          df_bb = self.add_bollinger_bands(df, n, m)
          # adds two columns to dataframe with buy and sell signals
          signal_bb = np.zeros(df_bb.shape[0])

          if frq == 'weekly':
             signal_bb[df_bb['High'] > df_bb['BU']] = -1
             signal_bb[df_bb['Low'] < df_bb['BL']] = 1
          # signal  daily
          elif frq == 'daily':
             signal_bb[df_bb['Close'] > df_bb['BU']] = -1
             signal_bb[df_bb['Close']< df_bb['BL']] = 1
          return signal_bb


      def __candlestick__(self, ax, df):
          # "up" dataframe данных будет хранить stock_prices
          # когда цена закрытия акции больше чем или равна начальной цене акций
          up = df[df.Close >= df.Open]

          # "down" dataframe будет хранить stock_prices
          # когда цена закрытия акции меньше, чем цена акций на открытие
          down = df[df.Close < df.Open]

          # Когда цены на акции выросли, то будет представлен свечой зеленого цвета
          col1 = 'green'

          # Когда цены на акции упали, будет представлен свечой красного цвета
          col2 = 'red'

          # Setting width of candlestick elements
          width1, width2 = .9, .12

          # График цен акций
          ax.bar(up.index, abs(up.Close-up.Open), width1, bottom=up.Open, color=col1)
          ax.bar(up.index, abs(up.High-up.Close), width2, bottom=up.Close, color=col1)
          ax.bar(up.index, abs(up.Low-up.Open), width2, bottom=up.Low, color=col1)

          # Построение цены акции вниз
          ax.bar(down.index, abs(down.Close-down.Open), width1, bottom=down.Close, color=col2)
          ax.bar(down.index, abs(down.High-down.Open), width2, bottom=down.Open, color=col2)
          ax.bar(down.index, abs(down.Low-down.Close), width2, bottom=down.Low, color=col2)



      def plot_ohcl(self, df,
                    start_fragment = 0,
                    finish_fragment = None,
                    columns_main = ['Close'],
                    columns_bar = [],
                    columns_plot = [],
                    points = [],
                    bollinger_bands = None,
                    candlestick = False,
                    figsize = None
                    ):
          '''
          df - датафрейм вида ohcl
          columns_main - лист из всех или ччасти -'Open','Low','High','Close'
          points - нампи массивов или pd.Series из диапозона (-1, 1)
          bollinger_bands - None или  (n, m), где:
                    n = smoothing length
                    m = number of standard deviations away from MA

          '''
          if not figsize:
            figsize = self.figsize

          # Стиль графикоф, см вначале
          plt.style.use(self.style_plot)
          # Отображение исходных данных от точки start и длиной length
          start = start_fragment if start_fragment else 0
          length = finish_fragment - start_fragment if \
          finish_fragment else df.shape[0] - start#_fragment

          # если рисуем полюсы болинджера
          if bollinger_bands:
            n = bollinger_bands[0]
            m = bollinger_bands[1]
            df_bb = self.add_bollinger_bands(df, n, m)

          weight_heights = []  # список весов-пропорций размеров окон графиков
          add_plots = 0        # счетчик окон графиков

          # если рисуем основной график
          if columns_main:
             add_plots += 1
             weight_heights += [1]

          # если рисуем дополнительный график
          if columns_plot:
             add_plots += 1
             weight_heights += [0.7] if weight_heights else [1]

          # если рисуем бар график
          if columns_bar:
            add_plots += len(columns_bar)
            if weight_heights:
              # обновляем список весов-пропорций размеров окон графиков
              weight_heights = [[2.7, 1.4][i] for i in range(len(weight_heights))]+[0.7]*len(columns_bar)
            else: weight_heights = [1]*len(columns_bar)

          # создания контейнера окон и учет соотношения окон в weight_heights
          fig, ax = plt.subplots(add_plots, 1, figsize = figsize,
                                gridspec_kw={'height_ratios': weight_heights},
                                constrained_layout=True)

          # обработка случая одного окна для обощения и перево в лист окон
          try: len(ax)
          except: ax = [ax]

          k = 0
          dates = df.index[start:start + length] # даты для отображения
          # основные канала - open, max, min, close до Volume

          for chnl in columns_main:
              # Отрисовка одного канала данных
              # От начальной точки start длиной length
              ax[k].plot(dates, chnl, data = df[start:start + length],label=chnl)
              ax[k].set_ylabel('Цены', fontweight='bold', fontsize=16)


              # точки покупки и продажи из массива сигналов  points
              if len(points) and chnl == 'Close':
                  # От маски  buy и  sell
                  buy = points[start:start + length] > 0
                  sell = points[start:start + length] < 0
                  ax[k].plot(dates[sell], df.Close[start:start + length][sell],
                            'v', ms = 15, color="red", label='Sell')
                  ax[k].plot(dates[buy], df.Close[start:start + length][buy],
                            '^', ms = 15, color="green", label='Buy')

              # если строим полосы Болинджера
              if bollinger_bands and chnl == 'Close':
                ax[k].plot(dates, 'BU', data = df_bb[start:start + length], alpha=0.3)
                ax[k].plot(dates, 'BL', data = df_bb[start:start + length], alpha=0.3)
                ax[k].plot(dates, 'B_MA', data = df_bb[start:start + length], alpha=0.3)
                ax[k].fill_between(dates, df_bb[start:start + length].BU,
                                  df_bb[start:start + length].BL, color='grey',
                                  alpha=0.1)
          if candlestick:
              self.__candlestick__(ax = ax[k], df = df[start:start + length])

          # строим ось Х только на последней оси
          if add_plots > k: ax[k].xaxis.set_ticklabels([])
          ax[k].legend()
          ax[k].grid(True)

          # если нужно построить bar график
          if columns_bar:
              for i, indicator in enumerate(columns_bar):
                  k+=1
                  # случайное задание цвета
                  colors = mcolors.TABLEAU_COLORS.keys()
                  color = np.random.choice(list(colors))
                  # Каналы colums_add
                  ax[k].bar(dates, df[indicator][start:start + length],
                          color = color, label=indicator)
                  # убираем подписе у Х если не последний график
                  if add_plots > k: ax[k].xaxis.set_ticklabels([])
                  ax[k].legend()

          # если нужно построить дополнительных график
          if columns_plot:
             k+=1
             for indicator in columns_plot:
                # Отрисовка одного канала данных
                # От начальной точки start длиной length
                colors = mcolors.TABLEAU_COLORS.keys()
                # случайное задание цвета
                color = np.random.choice(list(colors))
                ax[k].plot(dates, indicator, data = df[start:start + length],
                           color = color, label=indicator)

          # строим ось Х только на последней оси
          if add_plots > k: ax[k].xaxis.set_ticklabels([])
          ax[k].legend()
          ax[k].grid(True)

          # Решение проблем с отображением datatime в составном графике
          # см. https://matplotlib.org/stable/gallery/text_labels_and_annotations/date.html
          ax[-1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
          ax[-1].xaxis.set_minor_locator(mdates.MonthLocator())
          ax[-1].xaxis.set_major_formatter(
              mdates.ConciseDateFormatter(ax[-1].xaxis.get_major_locator()))

          # Text in the x axis will be displayed in 'YYYY-mm' format.
          ax[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
          # Rotates and right-aligns the x labels so they don't crowd each other.
          for label in ax[-1].get_xticklabels(which='major'):
              label.set(rotation=30, horizontalalignment='right')
          plt.xlabel('Время', fontweight='bold', fontsize=16)
          # Фиксация графика
          plt.show()

FIGURESIZE = (16, 10)
# инициализируем класс для отрисовки графиков
sh_ohcl = Show_OHCL(figsize=FIGURESIZE)

# sh_ohcl.plot_ohcl(input_df, columns_main=['Close'], columns_bar=['Volume'])

# sh_ohcl.plot_ohcl(input_df, start_fragment=10, finish_fragment = 270,
#                  figsize = (16, 7),
#                  columns_main=['Open', 'Close'],
#                  candlestick=True)