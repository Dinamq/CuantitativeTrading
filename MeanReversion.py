import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import matplotlib.dates as mdates

plt.ion()

ticker = '^GSPC'
window_rolling = 50

# Descargar 1 semana de datos a 5m
df = yf.download(ticker, interval="5m", period="5d")
df.index = df.index.tz_localize(None)

# Calcular retornos logarítmicos
df['log_ret'] = np.log(df['Close'] / df['Close'].shift(1))

# Bandas ±2σ
media = df['log_ret'].rolling(window=window_rolling).mean()
std = df['log_ret'].rolling(window=window_rolling).std()
df['upper'] = media + 2 * std
df['lower'] = media - 2 * std

# Crear columna evento como object
df['evento'] = pd.Series(dtype='object', index=df.index)
df.loc[df['log_ret'] > df['upper'], 'evento'] = 'Por encima (+2σ)'
df.loc[df['log_ret'] < df['lower'], 'evento'] = 'Por debajo (-2σ)'

# Filtrar eventos
eventos = df[df['evento'].notna()].copy()
eventos['color'] = np.where(eventos['evento'] == 'Por encima (+2σ)', 'red', 'green')

# Graficar
plt.clf()
plt.plot(df['log_ret'], label='Log Return', color='orange')
plt.plot(df['upper'], linestyle='--', color='red', label='Upper Threshold')
plt.plot(df['lower'], linestyle='--', color='green', label='Lower Threshold')
plt.axhline(0, linestyle='--', color='gray', linewidth=1)

# Añadir puntos de eventos
plt.scatter(eventos.index, eventos['log_ret'], c=eventos['color'], s=60)

# Añadir etiquetas con hora en los eventos
for idx, log_ret in zip(eventos.index, eventos['log_ret']):
    plt.annotate(idx.strftime('%H:%M'),
                 (idx, log_ret),
                 textcoords="offset points", xytext=(0, 10), ha='center',
                 fontsize=8, backgroundcolor='yellow')

# Eje X con fechas legibles
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45)

plt.title(f"{ticker} (5m) - Ruptura de Umbrales")
plt.xlabel("Fecha")
plt.ylabel("Log Return")
plt.legend()
plt.grid(True)
plt.show()

plt.pause(60)
