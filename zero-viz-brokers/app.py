import streamlit as st 
st.set_page_config(page_title='zktrade', page_icon='💰', layout='wide')

import asyncio
import time 
import numpy as np 
from dataclasses import dataclass
from hashlib import sha256
from st_supabase_connection import SupabaseConnection

from streamlit_pills import pills as st_pills

OPTIONS = [
    'Hug', 
    'Handshake',
    'Kiss',
]

PLACEHOLDER_NAMES = [
    'John',
    'Alice',
    'Charlie',
    'Bob'
]

from src.utils import (
    Order,
    fetch_current_active_orders,
    add_new_order,
    clear_specific_order,
    match_orders                      
)

if 'seen' not in st.session_state:
    st.session_state['seen'] = []




st.title("ZK-Trade - The Zero Viz Brokers")

name = st.text_input('Who are you? (THIS IS CONFIDENTIAL UNTIL YOU TRANSACT)')

if not name:
    st.stop()
    
# st.write('''Ask for what you want, it's compleately secret until it happens''')

if 'matched_orders' not in st.session_state:
    st.session_state['matched_orders'] = []
    
def add_random_order():

    name = np.random.choice(PLACEHOLDER_NAMES, 1)[0]

    item = np.random.choice(OPTIONS, 1)[0]
    price = np.random.randint(0,1000)
    quantity = np.random.randint(1,10)
    _type = 'sell' if np.random.randint(0,2) else 'buy'

    _r_o = Order(name=name, item=item, price=price, quantity=quantity, type=_type)
    add_new_order(_r_o)

def my_hash(x):
    return sha256(x.encode()).hexdigest()

def render_secret_order(order):
    st.info(f"""Secret Oder Details ({my_hash(f'''{order}''')})""")


OPTIONS = [
    '🍕 Pizza', 
    '🎂 Cake',
    '🍦 Ice Cream',
    '🍫 Chocolate',
    '🍪 Cookies',
    # '🍿 Popcorn',
]

@st.fragment(run_every=5)
def display_orderbook():

    matched_orders = match_orders()

    for tr in matched_orders:
        if tr['seller_name'] == name or tr['buyer_name'] == name and tr['buyer_name'] != tr['seller_name']:
        
            st.toast(f'''You matched with {tr['seller_name']} and {tr['buyer_name']}
                You are to transact **{tr['item']}** for **{tr['transaction_price']}**
        ''',  icon="🔥")

    # if len(matched_orders) == 0:
    #     matched_orders = match_orders()
    #     st.session_state['matched_orders'] = matched_orders

    orders = fetch_current_active_orders()


    st.write('''🔔 = NEW!!!''')

    c1, c2 = st.columns([1,5])

    for tr in matched_orders:
        for i, order in [(i,v) for (i,v) in orders.items() if i in [tr['seller_id'], tr['buyer_id']]]:
            
            with c1: 
                new = '🔔 ' if i not in st.session_state['seen'] else '  '
                st.session_state['seen'].append(i)
                st.success(f'''{new}Order #{i}''')
                
            with c2:
                if i == tr['seller_id']:
                    st.error(f'''SELLER [{order['name']}]: {order['item']} @{order['price']} - transact at £{tr['transaction_price']:.1f}''') 
                elif i == tr['buyer_id']:
                    st.warning(f'''BUYER [{order['name']}]: {order['item']} @{order['price']} - transact at £{tr['transaction_price']:.1f}''') 

        # time.sleep(1)

        time.sleep(4)
        clear_specific_order(tr['seller_id'])
        clear_specific_order(tr['buyer_id'])

    with st.container(height=900):
        c1, c2 = st.columns([1,5])


        for i, order in [(i,v) for (i,v) in orders.items() if i not in sum([[tr['buyer_id'], tr['seller_id']] for tr in matched_orders],[])]:
            
            with c1: 
                new = '🔔 ' if i not in st.session_state['seen'] else '  '
                st.session_state['seen'].append(i)
                st.warning(f'''{new}Order #{i}''')
            with c2:
                render_secret_order(order)

with st.container():
    st.write('''### Ask for what you want, it's completely secret until it happens''')

    c1, c2 = st.columns([4,2])

    with c1:
        trading_item = st_pills('What do you want to transact?', OPTIONS, index=0)

    with c2:
        is_sale = st_pills('Order type',  ['Sell', 'Buy'], index=0, key='order_type') == 'Sell'
    
    bl = 6 if is_sale else 4

    default = (0 if not is_sale else bl, 10 if is_sale else bl)

    price = st.slider(f'What is the {"lowest" if is_sale else "highest"} averarge price you are happy with?', 
                      0, 10, default, step=1, key=f'RANGE_{is_sale}')

    quantity = 1

    order:Order = Order(
                    name=name,
                    item=trading_item, 
                    type='sell' if is_sale else 'buy',
                    price=min(price) if is_sale else max(price),
                    quantity=quantity
                )
    
    if st.button('Submit', use_container_width=True):
        add_new_order(order)

display_orderbook()
