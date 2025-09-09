import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import yfinance as yf

plt.ion()  # Activar modo interactivo de matplotlib

ticker = 'EURUSD=X'
window_rolling = 50
update_interval = 300  # 5 minutos = 300 segundos

while True:
    # Descargar datos recientes
    df = yf.download(ticker, interval="5m", period="1d")
    df.index = df.index.tz_localize(None)

    # Calcular retornos logarítmicos y suavizado
    df['log_ret'] = np.log(df['Close'] / df['Close'].shift(1))
    df['log_ret_smooth'] = df['log_ret'].rolling(window=5).mean()

    # Media y desviación estándar móviles
    media = df['log_ret_smooth'].rolling(window=window_rolling).mean()
    std = df['log_ret_smooth'].rolling(window=window_rolling).std()
    df['upper'] = media + 2 * std
    df['lower'] = media - 2 * std

    # Señales de reversión
    df['above_upper'] = df['log_ret_smooth'] > df['upper']
    df['below_lower'] = df['log_ret_smooth'] < df['lower']
    df['evento'] = pd.Series(index=df.index, dtype='object')
    df.loc[(df['above_upper'].rolling(2).sum() == 2) & (df['log_ret_smooth'] > 0.0008), 'evento'] = 'Reversión (+2σ)'
    df.loc[(df['below_lower'].rolling(2).sum() == 2) & (df['log_ret_smooth'] < -0.0008), 'evento'] = 'Reversión (-2σ)'

    # Filtrar últimos 20 minutos (4 velas de 5m)
    ultimo = df.index.max()
    inicio = ultimo - pd.Timedelta(minutes=20)
    ventana = df.loc[inicio:ultimo]

    # Preparar evento visual
    if 'evento' in ventana.columns:
        eventos = ventana.dropna(subset=['evento'])
        eventos_pos = eventos[eventos['evento'] == 'Reversión (+2σ)']
        eventos_neg = eventos[eventos['evento'] == 'Reversión (-2σ)']

        plt.scatter(eventos_pos.index, eventos_pos['log_ret_smooth'], color='red', label='Reversión (+2σ)', s=60)
        plt.scatter(eventos_neg.index, eventos_neg['log_ret_smooth'], color='green', label='Reversión (-2σ)', s=60)


    # Graficar
    plt.clf()
    plt.plot(ventana['log_ret_smooth'], label='Log Ret (suavizado)', color='orange')
    plt.plot(ventana['upper'], linestyle='--', color='red', label='+2σ')
    plt.plot(ventana['lower'], linestyle='--', color='green', label='-2σ')
    plt.axhline(0, linestyle='--', color='gray', linewidth=1)

    plt.scatter(eventos_pos.index, eventos_pos['log_ret_smooth'], color='red', label='Reversión (+2σ)', s=60)
    plt.scatter(eventos_neg.index, eventos_neg['log_ret_smooth'], color='green', label='Reversión (-2σ)', s=60)

    plt.title("EUR/USD (5m) - Reversión en Tiempo Real (últimos 20 min)")
    plt.xlabel("Fecha")
    plt.ylabel("Log Return")
    plt.legend()
    plt.grid(True)
    plt.pause(1)  # Mostrar actualización

    print(f"[{pd.Timestamp.now()}] Actualizado. Próxima actualización en 5 minutos...\n")
    time.sleep(update_interval)
