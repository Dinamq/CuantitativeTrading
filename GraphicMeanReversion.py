import sys
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.dates as mdates

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class FinanceApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Detección de anomalías financieras")
        self.resize(1200, 700)

        main_layout = QVBoxLayout()

        # --- Selector arriba ---
        self.label = QLabel("Seleccione el activo para analizar:")
        self.combo = QComboBox()
        self.combo.addItem("Dow Jones [^DJI]", "^DJI")
        self.combo.addItem("NASDAQ [^NDX]", "^NDX")
        self.combo.addItem("S&P500 [^GSPC]", "^GSPC")
        self.combo.addItem("GER30 [^GDAXI]", "^GDAXI")

        self.button = QPushButton("Analizar")
        self.button.clicked.connect(self.run_analysis)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.combo)
        top_layout.addWidget(self.button)

        main_layout.addLayout(top_layout)

        # --- Zona central: gráfico izquierda, historial derecha ---
        center_layout = QHBoxLayout()

        # Lienzo Matplotlib
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        center_layout.addWidget(self.canvas, stretch=3)

        # Historial
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        center_layout.addWidget(self.text, stretch=1)

        main_layout.addLayout(center_layout)

        self.setLayout(main_layout)

    def run_analysis(self):
        asset = self.combo.currentData()

        window_rolling = 50
        interval = '5m'
        period = '5d'
        time_zone = "Europe/Madrid"

        # Descargar datos
        df = yf.download(asset, interval=interval, period=period)
        df.index = df.index.tz_convert(time_zone)

        # Calcular retornos logarítmicos
        df['log_ret'] = np.log(df['Close'] / df['Close'].shift(1))
        media = df['log_ret'].rolling(window=window_rolling).mean()
        std = df['log_ret'].rolling(window=window_rolling).std()
        df['upper'] = media + 2 * std
        df['lower'] = media - 2 * std

        df['evento'] = pd.Series(dtype='object', index=df.index)
        df.loc[df['log_ret'] > df['upper'], 'evento'] = 'Por encima (+2σ)'
        df.loc[df['log_ret'] < df['lower'], 'evento'] = 'Por debajo (-2σ)'

        eventos = df[df['evento'].notna()].copy()
        eventos['color'] = np.where(eventos['evento'] == 'Por encima (+2σ)', 'red', 'green')

        # --- Graficar ---
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(df['log_ret'], label='Log Return', color='grey')
        ax.plot(df['upper'], linestyle='--', color='red', label='Upper Threshold')
        ax.plot(df['lower'], linestyle='--', color='green', label='Lower Threshold')
        ax.axhline(0, linestyle='--', color='gray', linewidth=1)

        ax.scatter(eventos.index, eventos['log_ret'], c=eventos['color'], s=60)

        for idx, evento, log_ret in eventos[['evento', 'log_ret']].itertuples(index=True, name=None):
            if evento == 'Por encima (+2σ)':
                offset, va = (0, 10), 'bottom'
            else:
                offset, va = (0, -15), 'top'

            ax.annotate(idx.strftime('%H:%M'),
                        (idx, log_ret),
                        textcoords="offset points", xytext=offset,
                        ha='center', va=va,
                        fontsize=8, backgroundcolor='yellow')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        for label in ax.get_xticklabels():
            label.set_rotation(45)

        ax.set_title(f"{asset} | Intervalo: {interval} & Periodo: {period} | Zona Horaria: {time_zone}")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Log Return")
        ax.legend()
        ax.grid(True)

        self.canvas.draw()

        # --- Mostrar historial ---
        self.text.clear()
        self.text.append("Historial de anomalías detectadas:\n")
        for idx, evento in eventos.sort_index(ascending=False)[['evento']].itertuples(index=True, name=None):
            self.text.append(f"{idx.strftime('%Y-%m-%d %H:%M')} - {evento}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec_())
