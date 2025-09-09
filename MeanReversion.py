import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import matplotlib.dates as mdates

plt.ion()

print("Seleccione el activo para analizar:")
print("1. Dow Jones [US30/DJ30] (^DJI)")
print("2. NASDAQ [US100/NAS100] (^NDX)")
print("3. S&P500 [US500/SP500] (^GSPC)")
print("4. GER30 [GER30/DAX40] (^DE30)")
print("Ingrese una opcion (1-4):")

response = input()
loop = True
while loop:
    if response not in ["1", "2", "3", "4"]:
        print("Opcion invalida, intente de nuevo (1-4):")
        response = input()
    else: loop = False

global asset

if response == "1":
    asset = "^DJI"
elif response == "2":
    asset = "^NDX"
elif response == "3":
    asset = "^GSPC"
elif response == "4":
    asset = "^GDAXI"

window_rolling = 50
interval = '5m'
period = '5d'
time_zone = "Europe/Madrid"

# Descargar 1 semana de datos a 5m
df = yf.download(asset, interval=interval, period=period)

# Convertir directamente a tu zona local
df.index = df.index.tz_convert(time_zone)

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
fig, ax = plt.subplots(figsize=(12, 5))
plt.plot(df['log_ret'], label='Log Return', color='orange')
plt.plot(df['upper'], linestyle='--', color='red', label='Upper Threshold')
plt.plot(df['lower'], linestyle='--', color='green', label='Lower Threshold')
plt.axhline(0, linestyle='--', color='gray', linewidth=1)

# Añadir puntos de eventos
plt.scatter(eventos.index, eventos['log_ret'], c=eventos['color'], s=60)

# --- Anotaciones arriba/abajo, robustas con itertuples ---
for idx, evento, log_ret in eventos[['evento', 'log_ret']].itertuples(index=True, name=None):
    if evento == 'Por encima (+2σ)':
        offset = (0, 10)   # arriba
        va = 'bottom'
    else:  # 'Por debajo (-2σ)'
        offset = (0, -15)  # abajo
        va = 'top'

    plt.annotate(idx.strftime('%H:%M'),
                 (idx, log_ret),
                 textcoords="offset points", xytext=offset,
                 ha='center', va=va,
                 fontsize=8, backgroundcolor='yellow')

# Eje X con fechas legibles
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45)

plt.title(f"{asset} | Intervalo: {interval} & Periodo: {period} | Zona Horaria: {time_zone} - Anomalias en Retornos Logarítmicos")
plt.xlabel("Fecha")
plt.ylabel("Log Return")
plt.legend()
plt.grid(True)
plt.show()

# Tu código se ejecuta aquí
input("El programa ha terminado.")
