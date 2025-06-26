# options_calculator.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from scipy.stats import norm
import math

st.set_page_config(page_title="Options PnL Calculator")
st.title('Options PnL Calculator ')

# таблица стратегий
strategy_data = pd.DataFrame([
    {"Стратегия": "Long Call", "Ожидание": "Рост актива", "Когда использовать": "Заработать на росте, но ограничить риск премией", "Макс. профит": "Неограничен", "Макс. убыток": "Премия", "Характеристика": "Направленная, без ликвидации"},
    {"Стратегия": "Short Call", "Ожидание": "Стабильность или падение", "Когда использовать": "Ожидание боковика/снижения. Заработок на премии", "Макс. профит": "Премия", "Макс. убыток": "Неограничен", "Характеристика": "Рискованная, требует маржи"},
    {"Стратегия": "Long Put", "Ожидание": "Падение актива", "Когда использовать": "Заработать на падении с ограничением риска", "Макс. профит": "Почти до нуля", "Макс. убыток": "Премия", "Характеристика": "Хедж или направленная ставка на падение"},
    {"Стратегия": "Short Put", "Ожидание": "Рост или стабильность", "Когда использовать": "Получить актив по сниженной цене или заработать на премии", "Макс. профит": "Премия", "Макс. убыток": "Страйк – премия", "Характеристика": "Продажа риска, альтернатива лимитному ордеру"}
])
with st.expander("📘 Показать таблицу стратегий"):
    st.dataframe(strategy_data, use_container_width=True)

# параметры
option_type = st.selectbox('Тип опциона', ['Long Call', 'Short Call', 'Long Put', 'Short Put'])

col1, col2 = st.columns(2)
with col1:
    strike_price = st.number_input('Цена страйка', help='Цена, от которой опцион находится в прибыли')
with col2:
    current_price = st.number_input('Текущая цена')

col3, col4 = st.columns(2)
with col3:
    if option_type.startswith('Long'):
        premium_label = 'Оплаченная премия (оплата авансом)'
    else:
        premium_label = 'Полученная премия (заработок авансом)'
    premium = st.number_input(premium_label, help='Премия — это стоимость опциона. Оплата если long, получаете в short')

with col4:
    iv = st.slider('Implied Volatility (IV %)', 1, 300, 80, help='Ожидаемая волатильность') / 100


with st.expander("Что такое Implied Volatility (IV)?"):
    st.markdown("""
Как использовать IV
– IV влияет на то, сколько стоит опцион до экспирации
– чем выше IV — тем дороже опцион, потому что больше шансов, что он “сыграет”  
– для графика: при высоком IV линия "PnL today" будет выше, при низком — ближе к "PnL at expiry"

---

Откуда взять IV
1. На биржах
   – на CEX типа Bybit, Deribit есть IV для каждого страйка  
   – можно просто взять среднее значение 

2. Если IV нет – оринтировочно:
   – BTC/ETH: ~50–80% в спокойном рынке, ~100–150% в новостях  
   – альткойны: часто 150–200%  
   – meme/low cap: можно смело ставить 200–300%+

""")

col5, col6 = st.columns(2)

with col5:
    expiry_date = st.date_input('Дата экспирации', value=date.today(), help='Дата истечения опциона')
with col6:
    today = st.date_input('Сегодняшняя цена', value=date.today())

# расчёт по нажатию
if st.button("🧮 Рассчитать PnL"):
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

        # Цветовые зоны
    break_even = strike_price + premium if 'Call' in option_type else strike_price - premium

    if 'Call' in option_type:
        fig.add_vrect(
            x0=break_even,
            x1=price_max,
            fillcolor="green",
            opacity=0.1,
            line_width=0,
            annotation_text="Profit Zone",
            annotation_position="top left"
        )
        fig.add_vrect(
            x0=strike_price - premium,
            x1=break_even,
            fillcolor="yellow",
            opacity=0.1,
            line_width=0,
            annotation_text="Breakeven Zone",
            annotation_position="top left"
        )
        fig.add_vrect(
            x0=price_min,
            x1=strike_price - premium,
            fillcolor="red",
            opacity=0.1,
            line_width=0,
            annotation_text="Loss Zone",
            annotation_position="top left"
        )
    else:
        fig.add_vrect(
            x0=price_min,
            x1=break_even,
            fillcolor="green",
            opacity=0.1,
            line_width=0,
            annotation_text="Profit Zone",
            annotation_position="top left"
        )
        fig.add_vrect(
            x0=break_even,
            x1=strike_price + premium,
            fillcolor="yellow",
            opacity=0.1,
            line_width=0,
            annotation_text="Breakeven Zone",
            annotation_position="top left"
        )
        fig.add_vrect(
            x0=strike_price + premium,
            x1=price_max,
            fillcolor="red",
            opacity=0.1,
            line_width=0,
            annotation_text="Loss Zone",
            annotation_position="top left"
        )

    st.plotly_chart(fig, use_container_width=True)
