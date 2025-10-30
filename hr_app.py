import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Insight dari Data Pegawai PLN-IP",
    page_icon="📊",
    layout="wide"
)

# Dashboard Title
st.title("📊 Insight dari Data Pegawai PLN-IP")
st.markdown(
    """Melakukan analisis kinerja pegawai dan metrik SDM secara interaktif guna memperoleh wawasan strategis yang dapat ditindaklanjuti."""
)

# Fungsi untuk load data
@st.cache_data
def load_data():
    # Gunakan raw string (r"...") biar backslash tidak bikin error di Windows
    path = r"data\DT_PEG_202506031318_clean.xlsx"
    df = pd.read_excel(path)
    return df
df = load_data()


#Navigation Bar
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Demographics", "Performance", "Career Progression"
])

# Tab 1: Overview
with tab1:    
    st.subheader("📊 Key Performance Indicators (KPIs)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Employees", len(df.PERSON_ID))
    kpi2.metric("Avg Age of Employees", f"{df.UMUR.mean():,.2f}")
    filtered_df = df[df['POHON_PROFESI'].astype(str).str.match(r'^\d+\.\d+$')]
    kpi3.metric("Total Direktorat", f"{filtered_df['POHON_PROFESI'].nunique():.0f}")

    st.markdown("### 🔗 Data Preview")
    st.dataframe(df.head())

# Tab 2: Demographics
with tab2:
    st.subheader("Demographics")
    st.write("Komposisi pegawai berdasarkan karakteristik dasar.")

    # -------------------------------
    # Data Preparation
    # -------------------------------

    # Pastikan TGL_LAHIR sudah datetime
    df['TGL_LAHIR'] = pd.to_datetime(df['TGL_LAHIR'], errors='coerce')

    # Hitung range usia (per 10 tahun)
    bins = range(20, df['UMUR'].max() + 10, 10)
    labels = [f"{i}-{i+9}" for i in bins[:-1]]
    df['Range Usia'] = pd.cut(df['UMUR'], bins=bins, labels=labels, right=False)

    # Layout kolom
    col1, col2 = st.columns(2)

    # -------------------------------
    # Pie Chart Gender
    # -------------------------------
    with col1:
        gender_counts = df['SEX'].value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=['#66b3ff', '#ff99cc'])
        ax.set_title("Komposisi Gender")
        st.pyplot(fig)

    # -------------------------------
    # Bar Chart Distribusi Usia
    # -------------------------------
    with col2:
        age_counts = df['Range Usia'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5,4))
        ax.bar(age_counts.index, age_counts.values, color='#9ECFEF', edgecolor='none')
        ax.set_title("Distribusi Usia Pegawai")
        ax.set_xlabel("Rentang Usia")
        ax.set_ylabel("Jumlah Pegawai")
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        # Label persentase di atas batang
        total = age_counts.sum()
        for i, v in enumerate(age_counts.values):
            ax.text(i, v + 0.5, f"{(v/total)*100:.1f}%", ha='center', fontsize=9)

        st.pyplot(fig)

    # -------------------------------
    # Distribusi Pendidikan
    # -------------------------------
    st.subheader("🎓 Distribusi Pendidikan Pegawai")
    edu_counts = df['PENDIDIKAN'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7,4))
    ax.barh(edu_counts.index, edu_counts.values, color='#A7D3A9')
    ax.set_xlabel("Jumlah Pegawai")
    ax.set_ylabel("Tingkat Pendidikan")
    ax.set_title("Distribusi Pendidikan Pegawai")
    st.pyplot(fig)

    # -------------------------------
    # Sebaran Agama & Status Pernikahan
    # -------------------------------
    col3, col4 = st.columns(2)

    with col3:
        if 'AGAMA' in df.columns:
            agama_counts = df['AGAMA'].value_counts()
            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(agama_counts, labels=agama_counts.index, autopct='%1.1f%%', startangle=90)
            ax.set_title("Sebaran Agama")
            st.pyplot(fig)

    with col4:
        if 'MARITAL_STATUS' in df.columns:
            marital_counts = df['MARITAL_STATUS'].value_counts()
            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(marital_counts, labels=marital_counts.index, autopct='%1.1f%%', startangle=90)
            ax.set_title("Status Pernikahan")
            st.pyplot(fig)

# Tab 3: Performance
with tab3:
    st.subheader("Performance")
    st.write("Analisis kinerja individu & tim.")

    # Fungsi untuk load data
    @st.cache_data
    def load_data():
        # Gunakan raw string (r"...") biar backslash tidak bikin error di Windows
        path2 = r"data\PENILAIAN_202506231113.xlsx"
        df_kinerja = pd.read_excel(path2)
        return df_kinerja
    df_kinerja = load_data()

    # Pastikan kolom tanggal & numerik benar
    df_kinerja['TANGGAL_MULAI'] = pd.to_datetime(df_kinerja['TANGGAL_MULAI'], errors='coerce')
    df_kinerja['TANGGAL_SELESAI'] = pd.to_datetime(df_kinerja['TANGGAL_SELESAI'], errors='coerce')

    # -------------------------------
    # KPI METRICS
    # -------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Rata-rata Skor Kinerja", f"{df_kinerja['NILAI_ANGKA'].mean():.2f}")
    col2.metric("🏆 Skor Tertinggi", f"{df_kinerja['NILAI_ANGKA'].max():.2f}")
    col3.metric("👥 Total Pegawai Dinilai", f"{df_kinerja['PERSON_ID'].nunique()}")

    # -------------------------------
    # Distribusi Skor (Histogram)
    # -------------------------------
    st.subheader("📈 Distribusi Skor Kinerja")

    fig, ax = plt.subplots(figsize=(8,4))
    ax.hist(df_kinerja['NILAI_ANGKA'], bins=20, color='#9ECFEF', edgecolor='white')
    ax.set_title("Distribusi Nilai Kinerja Pegawai")
    ax.set_xlabel("Nilai Kinerja (NILAI_ANGKA)")
    ax.set_ylabel("Jumlah Pegawai")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig)

    # -------------------------------
    # Top 10 High Performers
    # -------------------------------
    st.subheader("🏅 Top 10 High Performers")

    top10 = (
        df_kinerja.sort_values(by='NILAI_ANGKA', ascending=False)
        .head(10)[['PERSON_ID', 'NILAI_ANGKA', 'NKI']]
        .reset_index(drop=True)
    )
    st.dataframe(top10.style.background_gradient(cmap='Blues'))

    # -------------------------------
    # Korelasi Kinerja vs Usia / Masa Kerja
    # -------------------------------
    
    st.subheader("📈 Hubungan Kinerja dengan Usia & Masa Kerja")

    fig, axes = plt.subplots(1, 2, figsize=(10,4))

    # Gabungkan data kinerja + demografi
    df_merge = df_kinerja.merge(df[['PERSON_ID', 'UMUR', 'TGL_MASUK']], on='PERSON_ID', how='left')

    # Hitung masa kerja (tahun)
    # Hitung masa kerja dalam tahun (berdasarkan selisih tahun, bukan hari)
    df_merge['TGL_MASUK'] = pd.to_datetime(df_merge['TGL_MASUK'], errors='coerce')
    current_year = pd.Timestamp.now().year
    df_merge['MASA_KERJA'] = current_year - df_merge['TGL_MASUK'].dt.year


    # Korelasi Usia vs Kinerja
    sns.regplot(data=df_merge, x='UMUR', y='NILAI_ANGKA', ax=axes[0],
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    axes[0].set_title('Kinerja vs Usia')
    axes[0].set_xlabel('Usia')
    axes[0].set_ylabel('Nilai Kinerja')

    # Korelasi Masa Kerja vs Kinerja
    sns.regplot(data=df_merge, x='MASA_KERJA', y='NILAI_ANGKA', ax=axes[1],
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    axes[1].set_title('Kinerja vs Masa Kerja')
    axes[1].set_xlabel('Masa Kerja (tahun)')
    axes[1].set_ylabel('')

    st.pyplot(fig)

#Tab 4: Career Progression
with tab4:
    st.header("Career Progression")
    st.caption("Melihat mobilitas karier & promosi pegawai dari waktu ke waktu.")

    # Pastikan kolom tanggal format datetime
    df['TANGGAL_MENJABAT'] = pd.to_datetime(df['TANGGAL_MENJABAT'], errors='coerce')
    df['TANGGAL_MULAI_JENJANG'] = pd.to_datetime(df['TANGGAL_MULAI_JENJANG'], errors='coerce')

    
        # ===========================================
    # Rata-rata waktu sebelum promosi
    # ===========================================
    if 'MASA_MENJABAT' in df.columns:
        avg_promosi = (df['MASA_MENJABAT'].mean() / 12)  # konversi bulan → tahun
        st.metric("⏳ Rata-rata Waktu Sebelum Promosi", f"{avg_promosi:.1f} tahun")
    else:
        st.info("Kolom 'MASA_MENJABAT' tidak ditemukan di dataset.")

        
    # ===========================================
    # Jumlah pegawai naik jabatan per tahun
    # ===========================================
    df['TAHUN_PROMOSI'] = df['TANGGAL_MULAI_JENJANG'].dt.year
    promosi_per_tahun = df['TAHUN_PROMOSI'].value_counts().sort_index()

    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.bar(promosi_per_tahun.index, promosi_per_tahun.values, color='#6FB1FC')
    ax1.set_title('Jumlah Pegawai Naik Jabatan per Tahun', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Tahun')
    ax1.set_ylabel('Jumlah Pegawai')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig1)

    # ===========================================
    # Perbandingan antar Divisi (Heatmap)
    # ===========================================
    if 'POHON_PROFESI' in df.columns and 'MASA_MENJABAT' in df.columns:
        divisi_promosi = df.groupby('POHON_PROFESI')['MASA_MENJABAT'].mean().reset_index()
        divisi_promosi['MASA_MENJABAT_TAHUN'] = divisi_promosi['MASA_MENJABAT'] / 12

        fig2, ax2 = plt.subplots(figsize=(8,5))
        sns.heatmap(divisi_promosi.pivot_table(values='MASA_MENJABAT_TAHUN', index='POHON_PROFESI'),
                    cmap='Blues', annot=True, fmt=".1f", linewidths=0.5,
                    cbar_kws={'label': 'Rata-rata (tahun)'}, ax=ax2)
        ax2.set_title('Perbandingan Rata-rata Masa Menjabat per Divisi', fontsize=11, fontweight='bold')
        st.pyplot(fig2)
    else:
        st.info("Kolom 'POHON_PROFESI' atau 'MASA_MENJABAT' tidak tersedia.")