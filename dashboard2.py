import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pickle
# Fungsi untuk mengambil data dari Flask API dengan berdasarkan filter waktu
def get_sensor_data(start_date=None, end_date=None):
    url = 'http://127.0.0.1:5000/data'
    params = {}
    if start_date:
        params['start_date'] = start_date.isoformat()
    if end_date:
        params['end_date'] = end_date.isoformat()
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Fungsi untuk mengambil data terbaru
def get_latest_data():
    response = requests.get('http://127.0.0.1:5000/latest_data')
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Fungsi untuk membuat data dump di Flask API
def create_data_dump():
    url = 'http://127.0.0.1:5000/create-dump'
    response = requests.post(url)
    return response.json()

# Fungsi untuk membuat gauge
def create_gauge(title, value, min_val, max_val, unit, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
        },
        number = {'suffix': unit}
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=200)
    return fig

# Fungsi utama untuk aplikasi Streamlit
def main():
    st.title("Dashboard Monitoring Kualitas Udara")
    latest_data = get_latest_data()

    model = pickle.load(open("AQI_model.sav", "rb"))
    # Tombol untuk membuat data dump
    if st.button('Buat Data Dump'):
        response = create_data_dump()
        st.write(response)
    
    # Rentang waktu default (30 hari terakhir)
    end_date_default = datetime.today().date()
    start_date_default = end_date_default - timedelta(days=30)
    
    # Pilih rentang waktu
    #st.sidebar.title("Filter Data")
    # Tombol preset waktu
    # preset = st.sidebar.radio(
    #     "Preset waktu",
    #     ('30 Hari Terakhir', '7 Hari Terakhir', '1 Hari Terakhir', 'Custom')
    # )

    # if preset == '30 Hari Terakhir':
    #     start_date = start_date_default
    #     end_date = end_date_default
    # elif preset == '7 Hari Terakhir':
    #     end_date = datetime.today().date()
    #     start_date = end_date - timedelta(days=7)
    # elif preset == '1 Hari Terakhir':
    #     end_date = datetime.today().date()
    #     start_date = end_date - timedelta(days=1)
    # else:
    #     start_date = st.sidebar.date_input("Mulai Tanggal", start_date_default)
    #     end_date = st.sidebar.date_input("Sampai Tanggal", end_date_default)
    
    # # Pilih parameter yang akan ditampilkan
    # st.sidebar.title("Pilih Parameter")
    # show_temperature = st.sidebar.checkbox('Suhu', value=True)
    # show_humidity = st.sidebar.checkbox('Kelembapan', value=True)
    # show_pm25 = st.sidebar.checkbox('PM2.5', value=True)
    # show_mq135 = st.sidebar.checkbox('MQ-135', value=True)
    
    # Ambil data dari Flask API dengan filter waktu
    
    # Debug output untuk memastikan data diterima dengan benar
    #st.write("Data dari API:", data)
    
    
    
    # Menampilkan data terbaru
    if latest_data:
        suhu = latest_data.get('temperature', 0)
        kelembapan = latest_data.get('humidity', 0)
        pm25 = latest_data.get('pm25', 0)
        nh3 = latest_data.get('nh3', 0)
        no2 = latest_data.get('no2', 0)
        co = latest_data.get('co', 0)
    
        new_data = pd.DataFrame({
        'PM2.5': [pm25],
        'NO2': [no2],
        'NH3': [nh3],
        'CO': [co],
        'Temperature': [suhu],
        'Humidity': [kelembapan]
        })
        new_prediction = model.predict(new_data)
    
        if new_prediction[0] == 'Good' or new_prediction[0] == 'Satisfactory':
            st.success(f"Prediksi Kategori AQI: {new_prediction[0]}")
        elif new_prediction[0] == 'Moderate':
            st.info(f"Prediksi Kategori AQI: {new_prediction[0]}")
        elif new_prediction[0] == 'Poor':
            st.warning(f"Prediksi Kategori AQI: {new_prediction[0]}")
        else:
            st.error(f"Prediksi Kategori AQI: {new_prediction[0]}")
        st.subheader("Data Kualitas Udara Terkini")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(create_gauge('Suhu', suhu, 0, 100, '°C', 'green'), use_container_width=True)
        with col2:
            st.plotly_chart(create_gauge('Kelembapan', kelembapan, 0, 100, '%', 'blue'), use_container_width=True)
        with col3:
            st.plotly_chart(create_gauge('Polutan', pm25, 0, 100, 'ug/m3', '#6DCF8D'), use_container_width=True)
        col4, col5, col6 = st.columns(3)
        with col4:
            st.plotly_chart(create_gauge('NH3', nh3, 0, 100, 'ug/m3', 'salmon'), use_container_width=True)
        with col5:
            st.plotly_chart(create_gauge('CO', co, 0, 100, 'mg/m3', 'skyblue'), use_container_width=True)
        with col6:
            st.plotly_chart(create_gauge('NO2', no2, 0, 100, 'ug/m3', 'red'), use_container_width=True)
        
   
    # Menampilkan grafik kualitas udara dari waktu ke waktu
    st.subheader("Grafik Data Kualitas Udara")
    # untuk filtering grafik 
    col1, col2 = st.columns(2)
    with col1 : 
        # Menggunakan radio button untuk memilih preset waktu
        preset = st.radio(
            "Filter berdasarkan waktu",
            ('30 Hari Terakhir', '7 Hari Terakhir', '1 Hari Terakhir', 'Custom')
        )
        # Logika untuk menentukan rentang tanggal berdasarkan preset yang dipilih
        if preset == '30 Hari Terakhir':
            start_date = datetime.today() - timedelta(days=30)
            end_date = datetime.today()

        elif preset == '7 Hari Terakhir':
            start_date = datetime.today() - timedelta(days=7)
            end_date = datetime.today()

        elif preset == '1 Hari Terakhir':
            start_date = datetime.today() - timedelta(days=1)
            end_date = datetime.today()

        else:  # Custom date range
            start_date = st.date_input("Mulai Tanggal", start_date_default)
            end_date = st.date_input("Sampai Tanggal", end_date_default)
    # col1, col2 = st.columns(2)
    # with col1: 
    #     start_date = st.date_input("Mulai Tanggal", start_date)
    # with col2:
    #     end_date = st.date_input("Sampai Tanggal", end_date)
    
    with col2:
        # Pilih parameter yang akan ditampilkan
        st.write("Pilih Parameter")
        col3, col4 = st.columns(2)
        with col3:
            show_temperature = st.checkbox('Suhu', value=True)
            show_humidity = st.checkbox('Kelembapan', value=True)
            show_pm25 = st.checkbox('Polutan', value=True)
        with col4:
        # show_mq135 = st.checkbox('Gas', value=True)
            show_nh3 = st.checkbox('NH3', value=True)
            show_co = st.checkbox('CO', value=True)
            show_no2 = st.checkbox('NO2', value=True)
            
    data = get_sensor_data(start_date=start_date, end_date=end_date)
    
    if preset == '30 Hari Terakhir':
            start_date = datetime.today() - timedelta(days=30)
            end_date = datetime.today()
            st.write(f"Filter by 30 days: {start_date} to {end_date}")

    elif preset == '7 Hari Terakhir':
        st.write(f"Filter by 7 days: {start_date} to {end_date}")

    elif preset == '1 Hari Terakhir':
        st.write(f"Filter by 1 day: {start_date} to {end_date}")

    else:  # Custom date range
        if start_date < end_date:
            st.write(f"Filter by custom date range: {start_date} to {end_date}")
        else:
            st.error('Error: Tanggal akhir harus setelah tanggal awal.')
    
    # Konversi data ke DataFrame
    if data:
        df = pd.DataFrame(data)
        
        # Debug output untuk memastikan kolom yang ada dalam DataFrame
        #st.write("Kolom dalam DataFrame:", df.columns)
        
        # Konversi kolom timestamp ke datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Tampilkan data dalam tabel
            #st.write(df)

            # kolom yang akan ditampilkan dalam grafik
            columns_to_plot = {}
            if show_temperature:
                columns_to_plot['temperature'] = 'Suhu'
            if show_humidity:
                columns_to_plot['humidity'] = 'Kelembapan'
            if show_pm25:
                columns_to_plot['pm25'] = 'Polutan'
            # if show_mq135:
            #     columns_to_plot['mq135'] = 'Gas'
            if show_nh3:
                columns_to_plot['nh3'] = 'NH3'
            if show_no2:
                columns_to_plot['no2'] = 'NO2'
            if show_co:
                columns_to_plot['co'] = 'CO'
            # Mengganti nama kolom sesuai dengan label baru
            df.rename(columns=columns_to_plot, inplace=True)
            # Tampilkan data dalam grafik
            if columns_to_plot:
                st.line_chart(df.set_index('timestamp')[list(columns_to_plot.values())])
            else:
                st.write("Pilih setidaknya satu parameter untuk ditampilkan dalam grafik.")
        else:
            st.write("Kolom 'timestamp' tidak ditemukan dalam data.")
    else:
        st.write("Tidak ada data yang tersedia untuk rentang waktu yang dipilih.")
    
if __name__ == "__main__":
    main()
