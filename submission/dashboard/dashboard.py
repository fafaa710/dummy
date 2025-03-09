import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import datetime

#load data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

file_path_day = r"..\dataset\Bike-sharing-dataset\day.csv"
file_path_hour = r"..\dataset\Bike-sharing-dataset\hour.csv"

data_day = load_data(file_path_day)
data_hour = load_data(file_path_hour)

day_df = pd.read_csv(file_path_day)

st.write(
    """
    # Dashboard Peminjaman Sepeda 
    Hello, Selamat datang!
    """
)

# Mengatur rentang tanggal
min_date = datetime.date(2011, 1, 1)
max_date = datetime.date(2012, 12, 1)

# Menyediakan nilai default di antara rentang tanggal
default_date = datetime.date(2011, 1, 1)

# Menampilkan widget date_input
date = st.date_input(label='Tanggal peminjaman', min_value=min_date, max_value=max_date, value=default_date)

# Menampilkan tanggal yang dipilih
st.write('Tanggal peminjaman:', date)

season = st.selectbox(
    label="Season",
    options=('1', '2', '3', '5')
)

st.subheader('Pergerakan Total Peminjaman Sepeda per Hari')
# Membuat dua kolom
col1, col2, col3 = st.columns(3)

# Menampilkan total peminjaman
with col1:
    total_peminjaman = data_day['cnt'].sum()
    st.metric("Total Peminjaman Sepeda", value=total_peminjaman)

# Menampilkan total registered
with col2:
    total_registered = data_day['registered'].sum()
    st.metric("Total Registered", value=total_registered)

# Menampilkan total casual
with col3:
    total_casual = data_day['casual'].sum()
    st.metric("Total Casual", value=total_casual)

# Menampilkan grafik daily jumlah peminjaman
st.line_chart(data_day[['dteday', 'cnt', 'casual', 'registered']].set_index('dteday'))

#baris baru
st.header('Jumlah Peminjaman Sepeda per Bulan (2011-2012)')

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
day_df['year'] = day_df['dteday'].dt.year
day_df_2011_2012 = day_df[day_df['year'].isin([2011, 2012])]
peminjaman_per_bulan = day_df_2011_2012.groupby(['year', 'mnth'])['cnt'].sum().reset_index()


fig2, ax2 = plt.subplots(figsize=(30, 15))
ax2.bar(peminjaman_per_bulan.index, peminjaman_per_bulan['cnt'])
ax2.set_xlabel('Bulan')
ax2.set_ylabel('Jumlah Peminjaman Sepeda')
ax2.set_title('Jumlah Peminjaman Sepeda per Bulan dari tahun 2011 sampai 2012')
ax2.set_xticks(peminjaman_per_bulan.index)
ax2.set_xticklabels(peminjaman_per_bulan['mnth'])
st.pyplot(fig2)


#baris baru
st.header('Jumlah Peminjaman Sepeda per Musim')
peminjaman_per_musim = day_df.groupby('season')['cnt'].sum().reset_index()
colors = ['lightcoral', 'gold', 'lightblue', 'lightgreen']
fig1, ax1 = plt.subplots(figsize=(8, 8))
ax1.pie(peminjaman_per_musim['cnt'], labels=peminjaman_per_musim['season'], colors=colors, autopct='%1.1f%%', startangle=140)
ax1.set_title('Jumlah Peminjaman Sepeda per Musim')
st.pyplot(fig1)


#Baris baru
st.header('Pola Peminjaman Sepeda pada Hari Kerja dan Hari Libur per Jam')
pola_peminjaman_per_jam = data_hour.groupby(['hr', 'workingday', 'holiday'])['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
for i in range(2):  # Loop untuk workingday dan holiday
    subset = pola_peminjaman_per_jam[pola_peminjaman_per_jam['workingday'] == i]
    label = 'Workingday' if i == 1 else 'Holiday'
    ax.plot(subset[subset['holiday'] == 0]['hr'], subset[subset['holiday'] == 0]['cnt'], label=label, marker='o')

ax.set_title('Pola Peminjaman Sepeda pada Hari Kerja dan Hari Libur per Jam')
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah Peminjaman Sepeda')
ax.legend()
ax.grid(True)

# Menampilkan plot di Streamlit
st.pyplot(fig)

#barisbaru
# Pilih variabel untuk clustering
features = ['temp', 'hum', 'windspeed']

# Menentukan jumlah cluster yang diinginkan
n_clusters = 3

# Memilih data yang akan digunakan untuk clustering
X = day_df[features]

# Melakukan proses clustering dengan K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
day_df['cluster'] = kmeans.fit_predict(X)

# Hitung jumlah peminjaman sepeda harian per cluster
peminjaman_per_cluster = day_df.groupby(['dteday', 'cluster'])['cnt'].sum().reset_index()

# Streamlit App
st.title('Analisis Peminjaman Sepeda dengan K-Means Clustering')

# Tampilkan hasil clustering
st.subheader('Hasil Clustering')
st.write(day_df[['dteday', 'temp', 'hum', 'windspeed', 'cluster']])

# Visualisasi hasil clustering
st.subheader('Visualisasi Hasil Clustering')
fig, ax = plt.subplots(figsize=(8, 8))
scatter = ax.scatter(X['temp'], X['hum'], c=day_df['cluster'], cmap='viridis', s=50)
ax.set_xlabel('Temperature')
ax.set_ylabel('Humidity')
ax.set_title('Clustering Result')
legend = ax.legend(*scatter.legend_elements(), title='Cluster')
ax.add_artist(legend)
st.pyplot(fig)

# Visualisasi pola peminjaman sepeda per cluster
st.subheader('Pola Peminjaman Sepeda per Cluster')

# Buat objek gambar Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))

# Menampilkan plot untuk setiap cluster dalam satu gambar
for cluster in range(n_clusters):
    cluster_data = peminjaman_per_cluster[peminjaman_per_cluster['cluster'] == cluster]
    ax.plot(cluster_data['dteday'], cluster_data['cnt'], label=f'Cluster {cluster}')

ax.set_xlabel('Tanggal')
ax.set_ylabel('Jumlah Peminjaman Sepeda')
ax.set_title('Pola Peminjaman Sepeda per Cluster')
ax.legend()

# Menampilkan gambar Matplotlib ke dalam Streamlit
st.pyplot(fig)

