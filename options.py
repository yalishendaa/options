# filename: option_pnl_viewer.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Option PnL Viewer", layout="centered")
st.title("📊 Single Option P&L Viewer")

st.markdown("Посмотри, как меняется P&L от цены базового актива при экспирации")

# Параметры
option_type = st.selectbox("Option Type", ["Call", "Put"])
position_type = st.selectbox("Position", ["Long", "Short"])
strike = st.number_input("Strike Price", value=100000.0, step=100.0)
premium = st.number_input("Premium (paid/received)", value=2000.0, step=100.0)
underlying = st.number_input("Current Underlying Price", value=104000.0, step=100.0)

# Расчёт
price_range = np.linspace(underlying * 0.85, underlying * 1.15, 500)

if option_type == "Call":
    intrinsic = np.maximum(price_range - strike, 0)
else:
    intrinsic = np.maximum(strike - price_range, 0)

if position_type == "Long":
    pnl = intrinsic - premium
else:
    pnl = premium - intrinsic

# График
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(price_range, pnl, label="P&L at Expiry", color="blue")
ax.axhline(0, color="red", linestyle="--", linewidth=1)
ax.axvline(strike, color="gray", linestyle="--", label="Strike")
ax.axvline(underlying, color="green", linestyle="--", label="Current Price")

ax.set_title(f"{position_type} {option_type} Option – Payoff at Expiry")
ax.set_xlabel("Underlying Price at Expiry")
ax.set_ylabel("Profit / Loss")
ax.legend()
ax.grid(True)

st.pyplot(fig)
