# options_calculator.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from scipy.stats import norm
import math

st.set_page_config(page_title="Options PnL Calculator", layout="wide")
st.title('Options PnL Calculator ')

# таблица стратегий
strategy_data = pd.DataFrame([
    {"Стратегия": "Long Call", "Ожидание": "Рост актива", "Когда использовать": "Хочешь заработать на росте, но ограничить риск премией", "Макс. профит": "Неограничен", "Макс. убыток": "Премия", "Характеристика": "Направленная, без ликвидации"},
    {"Стратегия": "Short Call", "Ожидание": "Стабильность или падение", "Когда использовать": "Ожидаешь боковик/снижение и хочешь заработать на премии", "Макс. профит": "Премия", "Макс. убыток": "Неограничен", "Характеристика": "Рискованная, требует маржи"},
    {"Стратегия": "Long Put", "Ожидание": "Падение актива", "Когда использовать": "Хочешь заработать на падении с ограничением риска", "Макс. профит": "Почти до нуля", "Макс. убыток": "Премия", "Характеристика": "Хедж или направленная ставка на падение"},
    {"Стратегия": "Short Put", "Ожидание": "Рост или стабильность", "Когда использовать": "Хочешь получить актив по сниженной цене или заработать на премии", "Макс. профит": "Премия", "Макс. убыток": "Страйк – премия", "Характеристика": "Продажа риска, альтернатива лимитному ордеру"}
])
with st.expander("📘 Показать таблицу стратегий"):
    st.dataframe(strategy_data, use_container_width=True)

# параметры
option_type = st.selectbox('Тип опциона', ['Long Call', 'Short Call', 'Long Put', 'Short Put'])
strike_price = st.number_input('Strike Price', value=2200.0)
current_price = st.number_input('Current Price', value=2400.0)
premium = st.number_input('Premium Paid/Received', value=100.0)
iv = st.slider('Implied Volatility (IV %)', 1, 300, 80) / 100
expiry_date = st.date_input('Expiration Date', value=date.today())
today = st.date_input('Today\'s Date', value=date.today())

# расчёт по нажатию
if st.button("🔄 Рассчитать PnL"):
    days_to_expiry = max((expiry_date - today).days, 0)
    T = days_to_expiry / 365
    r = 0.0

    # диапазон цен
    low = min(strike_price, current_price)
    high = max(strike_price, current_price)
    price_min = int(low * 0.5) if "Put" in option_type else int(low * 0.9)
    price_max = int(high * 1.1) if "Put" in option_type else int(high * 1.5)
    price_range = np.linspace(price_min, price_max, 500)

    def black_scholes_price(S, K, T, r, sigma, option_type='call'):
        if T == 0:
            return max(0.0, S - K) if option_type == 'call' else max(0.0, K - S)
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type == 'call':
            return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        else:
            return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    pnl_today = []
    pnl_expiry = []

    for price in price_range:
        opt_type = 'call' if 'Call' in option_type else 'put'
        theo = black_scholes_price(price, strike_price, T, r, iv, opt_type)
        if option_type.startswith('Long'):
            pnl_t = theo - premium
        else:
            pnl_t = premium - theo
        pnl_today.append(pnl_t)

        payoff = max(price - strike_price, 0) if 'Call' in option_type else max(strike_price - price, 0)
        pnl_e = payoff - premium if option_type.startswith('Long') else premium - payoff
        pnl_expiry.append(pnl_e)

    # график
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_range, y=pnl_today, mode='lines', name='PnL Today'))
    fig.add_trace(go.Scatter(x=price_range, y=pnl_expiry, mode='lines', name='PnL at Expiry', line=dict(dash='dot')))
    fig.add_vline(x=strike_price, line=dict(color='gray', dash='dash'), annotation_text='Strike')
    fig.add_vline(x=current_price, line=dict(color='green', dash='dash'), annotation_text='Current Price')

    fig.update_layout(
        title=f'{option_type} – PnL Curve',
        xaxis_title='Underlying Price',
        yaxis_title='Profit / Loss',
        template='plotly_dark',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)
