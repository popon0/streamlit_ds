import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import streamlit as st

hours_df = pd.read_csv("hour.csv", delimiter=",")
days_df = pd.read_csv("day.csv", delimiter=",")

datetime_columns = ["dteday"]

for column in datetime_columns:
  hours_df[column] = pd.to_datetime(hours_df[column])
  days_df[column] = pd.to_datetime(days_df[column])

hours_df['time_segment'] = pd.cut(
    hours_df['hr'],
    bins=[-1, 5, 9, 15, 17, 18, 23],
    labels=['Midnight', 'Early Morning', 'Day', 'Afternoon', 'Evening', 'Night']
)
min_hours_df = hours_df[['instant', 'dteday', 'hr', 'workingday', 'casual', 'registered', 'time_segment']]
df_workdays = min_hours_df[min_hours_df['workingday'] == 1]

avg_casual = min_hours_df.groupby(by="time_segment").agg({
    'casual': ['mean']
})
avg_registered = min_hours_df.groupby(by="time_segment").agg({
    'registered': ['mean']
})

average_per_hour = pd.concat([avg_casual, avg_registered], axis=1)
average_per_hour.columns = ['casual', 'registered']

print(average_per_hour)

min_days_df = days_df[['instant', 'dteday', 'season', 'casual', 'registered']]
seasonal_casual_data = min_days_df.groupby('season')['casual'].sum()
seasonal_registered_data = min_days_df.groupby('season')['registered'].sum()

total_seasonal_data = seasonal_casual_data + seasonal_registered_data
percent_casual = (seasonal_casual_data / total_seasonal_data) * 100
percent_registered = (seasonal_registered_data / total_seasonal_data) * 100


st.title('Proyek Analisis Data')
st.header('Dataset bike sharing')

st.text("""
\n
Dashboard ini berisikan hasil project analisis data, menggunakan dataset 
bike sharing yang dimana penjelasannya adalah sebagai berikut:

"Bike Sharing merupakan inovasi terkini dalam dunia penyewaan sepeda, 
di mana semua proses mulai dari mendaftar, menyewa, hingga mengembalikan sepeda
dilakukan secara otomatis. Dengan lebih dari 500 program berbagi sepeda diseluruh
dunia dan lebih dari 500 ribu sepeda, sistem ini semakin diminati karena perannya
yang penting dalam mengatasi masalah lalu lintas, keberlanjutan lingkungan, 
dan kesehatan. Selain aplikasi praktis dalam kehidupan sehari-hari, data yang 
dihasilkan oleh sistem ini juga menarik untuk diteliti, membentuk jaringan 
sensor virtual yang membantu memantau mobilitas di kota. Dengan pencatatan 
durasi perjalanan, posisi awal, dan posisi akhir secara gamblang, sistem berbagi
sepeda menjadi alat efektif dalam mendeteksi peristiwa penting di kota."

Source: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
""")

st.text("""
Proses dimulai dari menentukan pertanyaan bisnis, memproses data dan pada 
akhirnya memvisualisasi data sehingga menghasilkan kesimpulan dari pertanyaan
bisnis yang dituang dalam bentuk  dashboard dengan streamlit, agar terlihat lebih
rapi dan terstruktur.
""")

st.text("""
Berikut adalah 2 pertanyaan beserta tujuan yang diajukan:
""")

st.subheader("""
Pertanyaan 1
""")

st.text("""
Dalam rentang waktu hari kerja, berapa rata-rata dari penguna casual 
dan pengguna registered pada setiap kelompok waktu (Midnight, Early Morning, 
Day, Afternoon, Evening, Night) dari data awal tahun 01-01-2011 sampai akhir 
tahun 31-12-2012 ?

Tujuan: Menjawab persoalan bisnis mengenai rata-rata operasional rental 
sepeda setiap jamnya dari pengguna casual dan registered pada hari kerja, 
untuk mengetahui berapa pengguna casual dibandingkan dengan pengguna registered,
sehingga stakeholder dapat memutuskan melakukan promosi agar user casual dapat 
menjadi registered user, serta mengetahui jam dengan rata-rata pengguna terendah
untuk menentukan waktu maintenance sepeda, sehingga tidak menggangu 
jam operasional sepeda.
""")

st.subheader("""
Pertanyaan 2
""")

st.text("""
- Apa pengaruh pergantian musim terhadap persentase pengguna rental casual 
dan registered dalam rentang awal tahun 01-01-2011 
sampai akhir tahun 31-12-2012 ?

Tujuan:  Menjawab persoalan bisnis mengenai pengaruh musim terhadap 
profit yang dihasilkan dari total pengguna rental, sehingga memungkinkan 
stakeholder memutuskan berapa banyak sepeda yang dapat beroperasional 
setiap musimnya dan disimpan, sehingga dapat menghemat 
biaya maintenance sepeda.
""")

st.text("""Untuk menjawab pertanyaan diatas maka dilakukan beberapa hal yang pada 
akhirnya menjawab pertannyaan dan menghasilkan kesimpulan dan saran, proses 
dimulai dari data wrangling lalu exploratory data analysis, yang ada dibawah ini. 
""")

proc1, proc2 = st.tabs(["Data Wrangling", "Exploratory Data Analysis (EDA)"])

with proc1:

    st.header('Step 1. Gathering and Assessing Data')

    st.text("""Mengambil data dari 2 dataset dengan format csv dibaca menggunakan 
function read_csv dari library pandas, dataset diperlakukan secara berbeda 
untuk memenuhi jawaban dari pertanyaan bisnis, sehingga tidak ada penyatuan 
pada kedua dataset""")

    code1 = """hours_df = pd.read_csv("hour.csv", delimiter=",")
days_df = pd.read_csv("day.csv", delimiter=",")"""
    st.code(code1, language='python')
    st.text("""Saat dilakukan pengecekan menghasilkan temuan bahwa pada kedua dataset 
ditemukan data pada column "dteday" bertype object, yang seharusnya adalah 
datetime, dengan output dipersingkat sebagai berikut:
    
""")

    txt1 = """<class 'pandas.core.frame.DataFrame'>
RangeIndex: 17379 entries, 0 to 17378
Data columns (total 17 columns):
 #   Column      Non-Null Count  Dtype  
---  ------      --------------  -----  
 0   instant     17379 non-null  int64  
 1   dteday      17379 non-null  object 
 ... 
 16  cnt         17379 non-null  int64  
dtypes: float64(4), int64(12), object(1)
memory usage: 2.3+ MB"""
    st.code(txt1, language='markdown')

    st.subheader("Assessing Summary")
    st.text("""1. Melakukan Pengecekan Apakah Ada Data Kosong 
Pada Kedua Dataset, dan hasil menunjukkan tidak ada missing value dari Dataset.

2. Melakukan Pengecekan Invalid Value pada Dataset,
Temuan: Pada Kedua Dataset ditemukan Bahwa Data Pada Column "dteday" bertype 
object, yang seharusnya adalah datetime.

3. Melakukan Pengecekan Duplicate Data,
Temuan: Tidak Ada Duplicate Data Dari Kedua Dataset.
""")

    st.header('Step 2. Cleaning Data')
    st.text("""Dari temuan sebelumnya ada sebuah masalah mengenai tipe data 
dari column "dteday" yang seharusnya adalah datetime, maka akan dilakukan 
perubahan, dengan kode berikut ini:
""")
    code2 = """datetime_columns = ["dteday"]

for column in datetime_columns:
  hours_df[column] = pd.to_datetime(hours_df[column])
  days_df[column] = pd.to_datetime(days_df[column])"""

    st.code(code2, language='python')
    st.text("""Sehingga saat diperiksa ulang akan "dteday" menghasikan output 
seperti berikut:""")
    txt2 = """<class 'pandas.core.series.Series'>
RangeIndex: 17379 entries, 0 to 17378
Series name: dteday
Non-Null Count  Dtype         
--------------  -----         
17379 non-null  datetime64[ns]
dtypes: datetime64[ns](1)
memory usage: 135.9 KB"""
    st.code(txt2, language='markdown')
    st.text("""Maka untuk proses awal sudah selesai dan akan dilanjutkan 
dengan proses EDA (Exploratory Data Analysis)""")

with proc2:
    st.header('Exploratory Data Analysis')
    st.text("""Membuat kelompok waktu, untuk mengelompokkan waktu 0 sampai 23 
dengan persyaratan sebagai berikut:
    
    00 - 05 (Midnight)
    05 - 09 (Early Morning)
    09 - 15 (Day)
    15 - 17 (Afternoon)
    17 - 18 (Evening)
    18 - 23 (Night)

Dengan menggunakan kode dibawah ini:
""")

    codeEDA1 = """hours_df['time_segment'] = pd.cut(
    hours_df['hr'],
    bins=[-1, 5, 9, 15, 17, 18, 23],
    labels=['Midnight', 'Early Morning', 'Day', 'Afternoon', 'Evening', 'Night']
)"""
    st.code(codeEDA1, language='python')
    st.text("""Lalu menyederhanakan "hours_df" menjadi "min_hours_df", untuk 
dataframe yang lebih ringkas, lalu menentukan tanggal yang dimana workingday 
sama dengan 1, yang berarti adalah hari kerja, dengan membuat variabel baru
sebagai penampung data seperti dibawah ini:
""")
    codeEDA2 = """min_hours_df = hours_df[['instant', 'dteday', 'hr', 'workingday', 'casual', 'registered', 'time_segment']]
df_workdays = min_hours_df[min_hours_df['workingday'] == 1]"""
    st.code(codeEDA2, language='python')

    st.text("""
Lalu mencari rata-rata setiap kelompok waktu dari 2 pengguna sepeda yaitu 
registered dan casual, dan menyatukannya menjadi satu tabel, untuk dapat 
menjawab pertanyaan pertama.
    """)
    codeEDA3 = """avg_casual = min_hours_df.groupby(by="time_segment").agg({
    'casual': ['mean']
})
avg_registered = min_hours_df.groupby(by="time_segment").agg({
    'registered': ['mean']
})
average_per_hour = pd.concat([avg_casual, avg_registered], axis=1)
average_per_hour.columns = ['casual', 'registered']"""
    st.code(codeEDA3, language='python')

    st.text("""
Variabel average_per_hour akan menghasilkan output sebagai berikut:

                    casual  registered
    time_segment                        
    Midnight        4.507717   20.400842
    Early Morning  16.955609  199.748451
    Day            66.193866  163.998627
    Afternoon      74.009589  312.708219
    Evening        61.120879  364.390110
    Night          30.142308  155.664560

    """)

    st.text("""
Menyederhanakan bentuk dari dataframe "days_df", menjadi "min_days_df"
    """)
    codeEDA4 = """min_days_df = days_df[['instant', 'dteday', 'season', 'casual', 'registered']]"""
    st.code(codeEDA4, language='python')

    st.text("""
Mengelompokkan dan menjumlahkan data pada pengguna casual dan 
registered berdasarkan kolom season
    """)
    codeEDA5 = """seasonal_casual_data = min_days_df.groupby('season')['casual'].sum()
seasonal_registered_data = min_days_df.groupby('season')['registered'].sum()"""
    st.code(codeEDA5, language='python')

    st.text("""
Mencari berapa jumlah total pengguna registered dan casual untuk setiap musimnya, 
agar dapat membantu ekplorasi dari perbandingan pengguna
    """)
    
    codeEDA6 = """print("Casual Data")
print(seasonal_casual_data)
print("Registered Data")
print(seasonal_registered_data)
print("Sum Of Both Registered and Casual")
print(seasonal_registered_data + seasonal_casual_data)"""
    st.code(codeEDA6, language='python')

    st.text("""Dengan output kode sebagai berikut: 
    
    Casual Data
    1     60622
    2    203522
    3    226091
    4    129782
    Name: casual, dtype: int64

    Registered Data
    1    410726
    2    715067
    3    835038
    4    711831
    Name: registered, dtype: int64

    Sum Of Both Registered and Casual
    1     471348
    2     918589
    3    1061129
    4     841613
    dtype: int64
""")
    st.text("""Lalu mengonversi data dalam bentuk persentase 0%-100%, dengan 
menjumlahkan total data dan membaginya pada setiap pengguna yaitu casual, 
registered. Lalu dikali dengan 10.
""")

    codeEDA7 = """total_seasonal_data = seasonal_casual_data + seasonal_registered_data
percent_casual = (seasonal_casual_data / total_seasonal_data) * 100
percent_registered = (seasonal_registered_data / total_seasonal_data) * 100"""
    st.code(codeEDA7, language='python')

with st.sidebar:    
    st.header('Hello there 	:sparkles:')
    st.subheader("I'm Teuku Hafiez Ramadhan")

st.text("""

Dari segala proses yang sudah dilewati maka saatnya untuk membuat visualisasi
dari data yang telah diproses, melalui visualisasi dan penjelasan yang pada
akhirnya menghasilkan sebuah kesimpulan, yang ada pada tab berikut:

""")

tab1, tab2 = st.tabs(["Pertanyaan 1", "Pertanyaan 2"])



with tab1:
    st.subheader('\n\nVisualisasi Pertanyaan 1')
    st.text("""

    Dari pertanyaan:
    Dalam rentang waktu hari kerja, berapa rata-rata dari penguna casual dan pengguna 
    registered pada setiap kelompok waktu (Midnight, Early Morning, Day, Afternoon, 
    Evening, Night) dari data awal tahun 01-01-2011 sampai akhir tahun 31-12-2012 ?

    Menghasilkan kriteria yang dibutuhkan jawaban berupa visualisasi dalam bentuk 
    grafik plot dikarenakan data adalah bentuk dari timeline peminjaman, jadi 
    menggambarkan rata-rata pada setiap kelompok waktu.

    Dataset yang digunakan adalah variabel "average_per_hour" yang sudah 
    menghitung rata-rata dari pengguna casual dan registered setiap jam lalu 
    mengelompokkannya, dan dibawah ini adalah visualisasinya.
    """)

    fig, ax = plt.subplots(figsize=(12, 8))
    casual_line = ax.plot(average_per_hour['casual'], label='Casual', marker='o', color='skyblue', linewidth=2)

    registered_line = ax.plot(average_per_hour['registered'], label='Registered', marker='o', color='orange', linewidth=2)

    ax.set_title('Rata-rata Pengguna Casual dan Registered Pada Setiap Kelompok Waktu Pada Hari Kerja', fontsize=16)

    ax.set_xlabel('Time Cluster', fontsize=12)
    ax.set_ylabel('Rata-rata Peminjaman Sepeda', fontsize=12)

    ax.set_xticks(range(6))

    ax.legend(loc='upper right')

    # Sebagai informasi tambahan mengenai range waktu
    legend_text = """
    Time Cluster

    00:00 - 05:00 (Midnight)
    05:00 - 09:00 (Early Morning)
    09:00 - 15:00 (Day)
    15:00 - 17:00 (Afternoon)
    17:00 - 18:00 (Evening)
    18:00 - 23:59 (Night)"""

    legend_patch = mpatches.Patch(color='none', label=legend_text)
    ax.legend(handles=[legend_patch], loc='upper left', frameon=False)

    ax.grid(True, linestyle='--', alpha=0.7)

    # Memberi tanda pada data rata-rata tertinggi casual
    casual_max_index = average_per_hour['casual'].idxmax()
    casual_max_value = average_per_hour['casual'].max()
    ax.scatter(casual_max_index, casual_max_value, s=1000, color='skyblue')

    # Memberi tanda pada data rata-rata tertinggi registered
    registered_max_index = average_per_hour['registered'].idxmax()
    registered_max_value = average_per_hour['registered'].max()
    ax.scatter(registered_max_index, registered_max_value, s=900, color='orange')

    ax.text(casual_max_index, casual_max_value, f'{casual_max_value:.0f}', ha='center', va='center', color='black', fontsize=10)
    ax.text(registered_max_index, registered_max_value, f'{registered_max_value:.0f}', ha='center', va='center', color='black', fontsize=10)

    fig.suptitle('Analisis Data Awal Tahun 2011 sampai Akhir Tahun 2012', y=0.95, fontsize=14)
    plt.ylim(0, 400)
    st.pyplot(fig)

    ##########################################
    st.text("""

    Dari yang ditemukan dari grafik, rata-rata peminjaman sepeda tertinggi pengguna 
    "registered" adalah 364 peminjam sepeda direntang waktu "Evening" dan 74 peminjam 
    sepeda casual di rentang waktu "Afternoon".

    Jumlah peminjam sepeda registered lebih banyak dibandingkan pengguna casual
    dari grafik menimbulkan beberapa kemungkinan:

    1. Sebagian besar dari pengguna registered kemungkinan adalah pengguna yang 
    aktif bekerja, terlihat bahwa adanya kenaikan pada kelompok waktu "Early Morning" 
    (saat berangkat bekerja), lalu adanya kenaikan saat kelompok waktu "Evening" 
    (saat pulang dari bekerja).
    2. Sebagian besar dari pengguna casual kemungkinan adalah yang sekedar untuk 
    aktifitas jalan-jalan sore dan pagi hari, terlihat bahwa ada kenaikan pada 
    kelompok waktu "Day" dan "Afternoon".

    Dan, perusahaan juga dapat membatasi jumlah sepeda yang digunakan di waktu-waktu 
    tertentu, untuk dapat membuat waktu maintenance tidak mengganggu operasional 
    peminjaman sepeda, waktu yang paling optimal adalah "Midnight".

    Saat kelompok waktu "Afternoon" dan "Evening (Puncak)", dapat mendeploy sepeda 
    lebih banyak untuk mendukung operasional dan men-cover semua peminjam sepeda.

    """)

with tab2:

    st.subheader('\n\nVisualisasi Pertanyaan 2')

    st.text("""

    Dari pertanyaan: 
    Apa pengaruh pergantian musim terhadap persentase total pengguna rental casual 
    dan registered dalam rentang awal tahun 01-01-2011 
    sampai akhir tahun 31-12-2012 ?

    Dalam hal ini berarti akan ada 2 data yang ditampilkan dalam bentuk persentase 
    yaitu pengguna casual dan registered, dalam hal ini bentuk visual yang cocok 
    adalah grafik batang yang akan menampilkan kedua data dengan 
    seluruh musim yang ada.

    Maka akan menghasilkan bentuk visual sebagai berikut:

    """)

    ###########################################

    # Data contoh
    seasonal_casual_data = pd.Series([60622, 203522, 226091, 129782], index=[1, 2, 3, 4], name='casual')
    seasonal_registered_data = pd.Series([410726, 715067, 835038, 711831], index=[1, 2, 3, 4], name='registered')

    # Buat plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    season_labels = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    colors = ['skyblue', 'lightcoral']

    bar_positions = np.arange(len(seasonal_casual_data))

    bar2 = ax.bar(bar_positions + bar_width/2, percent_registered, bar_width, label='Registered', color='lightcoral', alpha=0.7)
    bar1 = ax.bar(bar_positions - bar_width/2, percent_casual, bar_width, label='Casual', color='skyblue', alpha=0.7)

    # Menambahkan judul dan label
    ax.set_title('Persentase Pengguna Casual dan Registered untuk Setiap Musim', fontsize=16)
    ax.set_xlabel('Musim', fontsize=12)
    ax.set_ylabel('Persentase Total Pengguna (%)', fontsize=12)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0.95), fancybox=True, shadow=True, ncol=2, mode='expand')

    # Menampilkan persentase langsung di atas bar
    for bars in [bar1, bar2]:
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, min(yval + 0.1, 100), f'{yval:.1f}%', ha='center', va='bottom', fontsize=10, color='black')

    # Menambahkan data dari variabel seasonal_casual_data dan seasonal_registered_data di dalam bar
    for season in seasonal_casual_data.index:
        casual_value = seasonal_casual_data[season]
        registered_value = seasonal_registered_data[season]
        total_value = casual_value + registered_value
        casual_percent = (casual_value / total_value) * 100
        registered_percent = (registered_value / total_value) * 100

        ax.text(bar_positions[season - 1] - bar_width/2, casual_percent / 2, f'{casual_value:,.0f}', ha='center', va='center', fontsize=10, color='black')
        ax.text(bar_positions[season - 1] + bar_width/2, 100 - (registered_percent / 2), f'{registered_value:,.0f}', ha='center', va='center', fontsize=10, color='black')

    ax.grid(True, linestyle='--', alpha=0.7)

    # Menambahkan label musim pada posisi yang benar
    ax.set_xticks(bar_positions)
    ax.set_xticklabels([season_labels[season] for season in seasonal_casual_data.index])

    # Memastikan nilai sumbu y tidak melebihi 100%
    ax.set_ylim(0, 100)

    # Menampilkan grafik di Streamlit
    st.pyplot(fig)

    st.text("""

    Dari visual grafik batang diatas, terlihat bahwa persentase pengguna registered 
    lebih banyak dari pengguna Casual, hal ini juga dibuktikan dari pertanyaan 1.

    Untuk jumlah pengguna terbanyak dalam 1 musim adalah "Fall" atau musim gugur 
    yang dimana informasi sebelumnya didapatkan dari EDA dari total penjumlahan 
    data pengguna casual dan registered disetiap musim, yaitu sebagai berikut:
    Spring (471.348), Summer (918.589), **Fall (1.061.129)**, Winter (841.613). 
    Lalu, rata-rata pengguna terendah ada di musim "Spring".

    Sehingga data ini dapat mendukung agar perusahaan bisa mengalokasikan 
    sepeda yang bisa beroperasi dengan tepat, untuk menghasilkan 
    profit yang lebih maksimal.
    """)


st.header('Konklusi')

st.header('Konklusi Pertanyaan 1')

st.text("""
Dari analisis grafik, terdapat temuan menarik terkait peminjaman sepeda:

1. Peminjaman Tertinggi Registered: Rata-rata peminjaman sepeda tertinggi 
oleh pengguna "registered" terjadi pada waktu "Evening" dengan jumlah 364 
peminjam, sedangkan pengguna "casual" tertinggi terjadi pada waktu "Afternoon" 
dengan 74 peminjam.

2. Jumlah Peminjam Registered vs. Casual: Jumlah peminjam sepeda yang terdaftar 
lebih banyak daripada pengguna casual. Temuan ini memunculkan dua kemungkinan 
interpretasi:
    - Sebagian besar pengguna terdaftar kemungkinan adalah pekerja, 
    terlihat dari kenaikan peminjaman pada waktu "Early Morning" 
    dan "Evening" yang sesuai dengan jam pulang-pergi bekerja.
    - Sebagian besar pengguna casual kemungkinan hanya menggunakan 
    sepeda untuk aktivitas rekreasi, terlihat dari kenaikan peminjaman 
    pada waktu "Day" dan "Afternoon".

Catatan: Untuk kesimpulan yang lebih akurat, diperlukan data lebih 
lanjut seperti informasi usia pengguna dan status pekerjaan.

Selain itu, perusahaan dapat mengambil langkah-langkah sebagai berikut:

1. Batasan Jumlah Sepeda: Perusahaan dapat mempertimbangkan untuk 
membatasi jumlah sepeda yang tersedia pada waktu-waktu tertentu 
untuk menghindari gangguan operasional selama waktu pemeliharaan. 
Waktu yang optimal untuk pemeliharaan adalah "Midnight".

2. Deploy Sepeda Lebih Banyak pada Waktu Tertentu: Pada waktu 
"Afternoon" dan "Evening (Puncak)", perusahaan dapat mendeploy sepeda
lebih banyak untuk mendukung operasional dan melayani semua peminjam 
sepeda dengan efektif.
""")

st.header('Konklusi Pertanyaan 2')

st.text("""
Dari visualisasi grafik batang, dapat disimpulkan:

1. Dominasi Pengguna Registered: Persentase pengguna registered lebih 
tinggi daripada pengguna casual, sesuai dengan temuan pada 
pertanyaan sebelumnya.

2. Musim Terfavorit untuk Peminjaman: Jumlah pengguna terbanyak 
terjadi pada musim "Fall" (Gugur) dengan total 1.061.129 peminjam, 
sedangkan musim "Spring" memiliki rata-rata pengguna terendah.

Dengan temuan ini, perusahaan dapat mengambil langkah-langkah berikut:

- Alokasi Sepeda yang Efektif: Menyadari tingginya permintaan pada 
musim "Fall", perusahaan dapat mengalokasikan sepeda dengan lebih efektif
selama musim ini untuk meningkatkan kepuasan pelanggan dan profitabilitas.

- Optimalkan Operasional pada Musim Sibuk: Mengetahui bahwa musim 
"Fall" memiliki jumlah peminjam tertinggi, perusahaan dapat mengoptimalkan
operasional, termasuk pemeliharaan sepeda, pada periode ini untuk mendukung 
lonjakan permintaan.
""")