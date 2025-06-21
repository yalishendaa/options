import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title('Options PnL Calculator')

# Ввод параметров опциона
option_type = st.selectbox('Option Type', ['Long Call', 'Short Call', 'Long Put', 'Short Put'])
strike_price = st.number_input('Strike Price', value=100000)
current_price = st.number_input('Current Price', value=104000)
premium = st.number_input('Premium Paid/Received', value=2000)
price_min = st.number_input('Min Underlying Price', value=88000)
price_max = st.number_input('Max Underlying Price', value=114000)
steps = st.slider('Steps', min_value=100, max_value=1000, value=500)

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
