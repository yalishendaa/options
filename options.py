import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

st.title('Options PnL Calculator')

# Таблица стратегий
strategy_data = pd.DataFrame([
    {
        "Стратегия": "Long Call",
        "Ожидание": "Рост актива",
        "Когда использовать": "Хочешь заработать на росте, но ограничить риск премией",
        "Макс. профит": "Неограничен",
        "Макс. убыток": "Премия",
        "Характеристика": "Направленная, без ликвидации"
    },
    {
        "Стратегия": "Short Call",
        "Ожидание": "Стабильность или падение",
        "Когда использовать": "Ожидаешь боковик/снижение и хочешь заработать на премии",
        "Макс. профит": "Премия",
        "Макс. убыток": "Неограничен",
        "Характеристика": "Рискованная, требует маржи"
    },
    {
        "Стратегия": "Long Put",
        "Ожидание": "Падение актива",
        "Когда использовать": "Хочешь заработать на падении с ограничением риска",
        "Макс. профит": "Почти до нуля",
        "Макс. убыток": "Премия",
        "Характеристика": "Хедж или направленная ставка на падение"
    },
    {
        "Стратегия": "Short Put",
        "Ожидание": "Рост или стабильность",
        "Когда использовать": "Хочешь получить актив по сниженной цене или заработать на премии",
        "Макс. профит": "Премия",
        "Макс. убыток": "Страйк – премия (если цена упадёт до нуля)",
        "Характеристика": "Продажа риска, часто как замена лимитному ордеру на покупку"
    }
])

with st.expander("Показать таблицу стратегий"):
    st.dataframe(strategy_data, use_container_width=True)


# Ввод параметров опциона
option_type = st.selectbox('Option Type', ['Long Call', 'Short Call', 'Long Put', 'Short Put'])
strike_price = st.number_input('Strike Price', value=None)
current_price = st.number_input('Current Price', value=None)
premium = st.number_input('Premium Paid/Received', value=None)
low = min(strike, current_price)
high = max(strike, current_price)

# логика по типу опциона
if "Call" in option_type:
    price_min = int(low * 0.9)
    price_max = int(high * 1.5)
elif "Put" in option_type:
    price_min = int(low * 0.5)
    price_max = int(high * 1.1)
else:
    price_min = int(low * 0.75)
    price_max = int(high * 1.25)

st.markdown(f"📉 Диапазон цены: от {price_min} до {price_max}")
steps = 500

# Диапазон цен
price_range = np.linspace(price_min, price_max, steps)

# Расчет PnL
if option_type == 'Long Call':
    payoff = np.maximum(price_range - strike_price, 0)
    pnl = payoff - premium
elif option_type == 'Short Call':
    payoff = np.maximum(price_range - strike_price, 0)
    pnl = premium - payoff
elif option_type == 'Long Put':
    payoff = np.maximum(strike_price - price_range, 0)
    pnl = payoff - premium
elif option_type == 'Short Put':
    payoff = np.maximum(strike_price - price_range, 0)
    pnl = premium - payoff

# Построение графика
fig = go.Figure()
fig.add_trace(go.Scatter(x=price_range, y=pnl, mode='lines', name='P&L'))

fig.add_vline(x=strike_price, line=dict(color='gray', dash='dash'), annotation_text='Strike Price')
fig.add_vline(x=current_price, line=dict(color='green', dash='dash'), annotation_text='Current Price')

fig.update_layout(
    title=f'{option_type} – Payoff at Expiry',
    xaxis_title='Underlying Price at Expiry',
    yaxis_title='Profit / Loss',
    template='plotly_dark',
    hovermode='x unified'
)

st.plotly_chart(fig)
