import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id' : 'nunique',
        'price' : 'sum'
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        'order_id' : 'order_count',
        'price' : 'revenue'
    }, inplace=True)

    return daily_orders_df

def create_best_worst_products_df(df):
    best_worst_products_df = df.groupby(by='product_category_name_english').agg({
        'order_id' : 'nunique',
        'product_id' : 'count',
        'price' : 'sum'
    })

    best_worst_products_df.rename(columns={
        'order_id' : 'order_count'
    }, inplace=True)

    return best_worst_products_df

def create_best_worst_sellers_df(df):
    best_worst_sellers_df = df.groupby(by= 'seller_id', as_index=False).agg({
        'order_id' : 'nunique',
        'price' : 'sum',
        'review_score' : 'mean'
    })

    best_worst_sellers_df.rename(columns={
        'order_id' : 'order_count',
        'price' : 'revenue',
    }, inplace=True)

    return best_worst_sellers_df

def create_sellers_city_df(df):

    sellers_city_df = df.groupby('seller_city', as_index=False).agg({
        'seller_id' : 'nunique'
    })
    sellers_city_df.rename(columns={
        'seller_id' : 'seller_count'
    }, inplace=True)

    return sellers_city_df

def create_customers_city_df(df):
    customers_city_df = df.groupby(by='customer_city', as_index=False).agg({
        'customer_id' : 'nunique'
    })
    customers_city_df.rename(columns={
        'customer_id' : 'customer_count'
    }, inplace=True)

    return customers_city_df

def create_rfm_df(df):
    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        'order_purchase_timestamp' : 'max',
        'order_id' : 'nunique',
        'price' : 'sum'
    })

    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']

    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = df['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)

    rfm_df.drop(['max_order_timestamp'], axis=1, inplace=True)

    return rfm_df

st.set_page_config(
    page_title="E-Commerce Public Dashboard",
    page_icon="dashboard\web_icon.png",
    layout="centered",
    initial_sidebar_state="auto",
)

all_df = pd.read_csv('D:/Muhammad Feryansyah/submission/dashboard/all_df.csv')

all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)

all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    st.image("D:/Muhammad Feryansyah/submission/dashboard/web_icon.png")
    st.header('Filter')

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) &
                (all_df['order_purchase_timestamp'] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
best_worst_products_df = create_best_worst_products_df(main_df)
best_worst_sellers_df = create_best_worst_sellers_df(main_df)
sellers_city_df = create_sellers_city_df(main_df)
customers_city_df = create_customers_city_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('E-Commerce Public Dashboard')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df['order_count'].sum()
    st.metric(label='Total Orders', value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df['revenue'].sum(), 'USD', locale='es_CO')
    st.metric(label='Total Revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16,8))

ax.plot(
    daily_orders_df['order_purchase_timestamp'],
    daily_orders_df['order_count'],
    marker='o',
    linewidth=2,
    color='#387F39'
)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader('Best & Worst Performing Products')

colors = ['#387F39', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74']

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(
    data=best_worst_products_df.sort_values(by='order_count', ascending=False).head(5),
    y='product_category_name_english',
    x='order_count',
    ax=ax[0],
    orient='h',
    palette=colors
)
ax[0].set_title('Best Performing Products', loc='center', fontsize=50)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(
    data=best_worst_products_df.sort_values(by='order_count', ascending=True).head(5),
    y='product_category_name_english',
    x='order_count',
    ax=ax[1],
    orient='h',
    palette=colors
)
ax[1].set_title('Worst Performing Products', loc='center', fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].yaxis.set_label_position('right')
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Best & Worst Performing Sellers')


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(
    data=best_worst_sellers_df.sort_values(by='order_count', ascending=False).head(5),
    y='seller_id',
    x='order_count',
    ax=ax[0],
    orient='h',
    palette=colors
)
ax[0].set_title('Best Performing Sellers', loc='center', fontsize=50)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(
    data=best_worst_sellers_df.sort_values(by='order_count', ascending=True).head(5),
    y='seller_id',
    x='order_count',
    ax=ax[1],
    orient='h',
    palette=colors
)
ax[1].set_title('Worst Performing Sellers', loc='center', fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].yaxis.set_label_position('right')
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Sellers & Customers Demography')

colors_ = ['#387F39', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74']


fig, ax = plt.subplots(figsize=(35,15))

sns.barplot(
    data=sellers_city_df.sort_values(by='seller_count', ascending=False).head(10),
    x='seller_count',
    y='seller_city',
    ax=ax,
    orient='h',
    palette=colors_
)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title('Number of Sellers by City', loc='center', fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)


fig, ax = plt.subplots(figsize=(35,15))

sns.barplot(
    data=customers_city_df.sort_values(by='customer_count', ascending=False).head(10),
    x='customer_count',
    y='customer_city',
    orient='h',
    ax=ax,
    palette=colors_
)
ax.set_title('Number Of Customers by City', loc='center', fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Best Customers Based On RFM Parameters')

col1, col2, col3 = st.columns(3)

with col1:
    average_recency = round(rfm_df.recency.mean(), 2)
    st.metric('Average Recency (days)', value=average_recency)

with col2:
    average_frequency = rfm_df.frequency.mean()
    st.metric('Average Frequency', value=average_frequency)

with col3:
    average_monetary = format_currency(rfm_df.monetary.mean(), 'USD', locale='es_CO')
    st.metric('Average Monetary', value=average_monetary)

fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(16,12))

sns.barplot(
    data=rfm_df.sort_values(by='recency', ascending=True).head(5),
    y='customer_id',
    x='recency',
    ax=ax[0],
    palette=['#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74'],
    orient='h'
)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title('By Recency', loc='center', fontsize=20)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].tick_params(axis='x', labelsize=12)

sns.barplot(
    data=rfm_df.sort_values(by='frequency', ascending=False).head(5),
    y='customer_id',
    x='frequency',
    ax=ax[1],
    palette=['#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74'],
    orient='h'
)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title('By Frequency', loc='center', fontsize=20)
ax[1].tick_params(axis='y',  labelsize=15)
ax[1].tick_params(axis='x', labelsize=12)

sns.barplot(
    data=rfm_df.sort_values(by='monetary', ascending=False).head(5),
    y='customer_id',
    x='monetary',
    ax=ax[2],
    palette=['#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74', '#BEDC74'],
    orient='h'
)
ax[2].set_xlabel(None)
ax[2].set_ylabel(None)
ax[2].set_title('By Recency', loc='center', fontsize=20)
ax[2].tick_params(axis='y', labelsize=15)
ax[2].tick_params(axis='x', labelsize=12)

fig.tight_layout(pad=4)
st.pyplot(fig)