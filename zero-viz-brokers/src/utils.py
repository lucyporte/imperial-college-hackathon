import streamlit as st 
import asyncio
import time 
import numpy as np 
from dataclasses import dataclass
from hashlib import sha256
from st_supabase_connection import SupabaseConnection



@dataclass
class Order:
    name: str
    item: str
    price: float
    quantity: int
    type: str = 'buy'
    is_active: bool = True

conn = st.connection("supabase",type=SupabaseConnection, ttl=1)


# @st.cache_resource(ttl=0)
def fetch_current_active_orders()->dict[int, Order]:
    '''Fetches all active orders from the database'''
    response = conn.table("orders").select("*").filter("is_active", "eq", True).order("created_at", desc=True).execute().data
    return {c['id']: c for c in response}

def add_new_order(order):
    '''Adds an order to the database'''
    conn.table("orders").insert([order.__dict__]).execute()


def clear_specific_order(order_id):
    conn.table("orders").update({"is_active": False}).eq("id", order_id).execute()

def match_orders()->list[dict]:

    sb = st.sidebar
    import polars as pl
    r = conn.table("orders").select("*").filter("is_active", "eq", True).order("created_at", desc=True).execute()
    df_active_orders = pl.DataFrame(r.data)

    df_buyers = df_active_orders.filter(type='buy').with_columns(buyer_price = 'price').sort(by='created_at', descending=False)
    df_sellers = df_active_orders.filter(type='sell').with_columns(seller_price = 'price').sort(by='created_at', descending=False)

    match_all = []
    for it in df_active_orders.select('item').unique().select(pl.col('item').implode()).item():
        matches = (df_buyers.filter(item=it)
                    .join_where(
                        df_sellers.filter(item=it),
                        pl.col('buyer_price').ge(pl.col('seller_price')), suffix='_seller')
                    .with_columns(transaction_price = pl.mean_horizontal(pl.col('buyer_price'), pl.col('seller_price')))
                    .select('transaction_price','item',buyer_id='id', seller_id='id_seller', buyer_name='name', seller_name='name_seller')
                    .filter(pl.col('seller_name')!=pl.col('buyer_name'))

                    .unique(['seller_name', 'buyer_name', 'item'], keep='first')
                    .unique(['seller_id'], keep='first')
                    .unique(['buyer_id'], keep='first')
                    .select(pl.struct(pl.all()).implode()).item()
        )

        # with st.sidebar:
        print(f'# {it}')
        print(matches)

        matches = list(matches)

        match_all += matches


    return match_all