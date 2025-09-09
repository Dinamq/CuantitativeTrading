import yfinance as yf
import pandas as pd

# Descargar datos del par EUR/USD
ticker = yf.Ticker("EURUSD=X")
df = ticker.history(interval="5m", period="7d")

# Eliminar la zona horaria del índice de tiempo
df.index = df.index.tz_localize(None)

# Guardar en Excel
df.to_excel("eurusd_5m_7dias.xlsx")
