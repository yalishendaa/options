# filename: option_spread_calculator.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Option Payoff Calculator", layout="centered")

st.title("📈 Option Strategy Payoff Calculator")

st.markdown("Configure a bull put spread and see the P&L at expiry")

# Ввод данных
underlying_price = st.number_input("Underlying Price (Current)", value=104000.0, step=100.0)
strike_short_put = st.number_input("Strike – Short Put (Sold)", value=98000.0, step=500.0)
strike_long_put = st.number_input("Strike – Long Put (Bought)", value=93000.0, step=500.0)
net_premium = st.number_input("Net Premium Received", value=2000.0, step=100.0)

# Расчёт диапазона цен и PnL
price_range = np.linspace(underlying_price * 0.85, underlying_price * 1.15, 500)

pnl = np.where(
    price_range < strike_long_put,
    - (strike_short_put - strike_long_put) + net_premium,
    np.where(
        price_range < strike_short_put,
        - (strike_short_put - price_range) + net_premium,
        net_premium
    )
)

# Визуализация
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(price_range, pnl, label="P&L at Expiry", color="orange", linestyle="--")
ax.axhline(0, color="red", linestyle="--", linewidth=1)
ax.axvline(underlying_price, color="green", linestyle="-", linewidth=1)
ax.set_xlabel("Underlying Price at Expiry")
ax.set_ylabel("Profit / Loss")
ax.set_title("Bull Put Spread – Payoff Diagram")
ax.legend()
ax.grid(True)

st.pyplot(fig)
