import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="Crew Schedule Analysis",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# JUDUL APLIKASI
# ============================================
st.title("✈️ Crew Schedule Change Analysis")
st.markdown("---")

# ============================================
# SIDEBAR - UPLOAD FILE
# ============================================
st.sidebar.header("📂 Upload Data")
st.sidebar.markdown("Upload file Excel untuk Planned dan Actual Schedule")

planned_file = st.sidebar.file_uploader("Upload Planned Schedule", type=['xlsx', 'xls'])
actual_file = st.sidebar.file_uploader("Upload Actual Schedule", type=['xlsx', 'xls'])

# ============================================
# FUNGSI UNTUK DETECT RANK
# ============================================
def detect_rank(crew_id):
    """
    Deteksi rank berdasarkan Crew ID
    Sesuaikan dengan format Crew ID di data Anda
    """
    crew_id_str = str(crew_id).upper()
    
    # Deteksi CPT (Captain)
    if 'CPT' in crew_id_str or crew_id_str.startswith('52'):
        return 'CPT'
    # Deteksi FO (First Officer)
    elif 'FO' in crew_id_str or crew_id_str.startswith('53'):
        return 'FO'
    # Selain CPT dan FO = Cabin Crew
    else:
        return 'Cabin'

# ============================================
# FUNGSI ANALISIS
# ============================================
@st.cache_data
def analyze_schedule(planned_df, actual_df, id_columns):
    """
    Fungsi untuk menganalisis perubahan schedule
    """
    # Identifikasi kolom tanggal
    date_columns = [col for col in planned_df.columns if col not in id_columns]
    
    all_changes = []
    
    # Loop setiap crew
    for idx in range(len(planned_df)):
        crew_id = planned_df.iloc[idx]['Crew ID']
        crew_name = planned_df.iloc[idx]['Crew Name']
        
        # Detect rank
        rank = detect_rank(crew_id)
        
        # Loop setiap tanggal
        for date_col in date_columns:
            # Ambil nilai planned dan actual
            planned_val = str(planned_df.iloc[idx][date_col])
            actual_val = str(actual_df.iloc[idx][date_col])
            
            # Bersihkan nilai kosong
            if planned_val == 'nan':
                planned_val = '-'
            if actual_val == 'nan':
                actual_val = '-'
            
            # Tentukan kategori
            if planned_val == actual_val:
                kategori = 'maintain'
            else:
                kategori = 'change'
            
            # Simpan data
            all_changes.append({
                'Crew ID': crew_id,
                'Crew Name': crew_name,
                'Rank': rank,
                'Tanggal': date_col,
                'Planned': planned_val,
                'Actual': actual_val,
                'Kategori': kategori
            })
    
    changes_df = pd.DataFrame(all_changes)
    return changes_df

# ============================================
# FUNGSI UNTUK MEMBUAT GRAFIK
# ============================================
def create_total_chart(df):
    """Grafik Total Maintain vs Change"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    kategori_counts = df['Kategori'].value_counts()
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax.bar(kategori_counts.index, kategori_counts.values, color=colors)
    ax.set_title('Total Maintain vs Change', fontsize=16, fontweight='bold')
    ax.set_xlabel('Kategori', fontsize=12)
    ax.set_ylabel('Jumlah', fontsize=12)
    
    # Tambahkan angka di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    return fig

def create_daily_stacked_chart(df):
    """Grafik Maintain dan Change per Tanggal (Stacked)"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    daily_pivot = df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
    daily_pivot.plot(kind='bar', stacked=True, color=['#2ecc71', '#e74c3c'], ax=ax)
    
    ax.set_xlabel('Tanggal', fontsize=12)
    ax.set_ylabel('Jumlah', fontsize=12)
    ax.set_title('Maintain dan Change per Tanggal (Stacked)', fontsize=16, fontweight='bold')
    ax.legend(title='Kategori', labels=['Maintain', 'Change'])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_daily_grouped_chart(df):
    """Grafik Maintain dan Change per Tanggal (Side by Side)"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    daily_pivot = df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
    daily_pivot.plot(kind='bar', color=['#2ecc71', '#e74c3c'], ax=ax, width=0.8)
    
    ax.set_xlabel('Tanggal', fontsize=12)
    ax.set_ylabel('Jumlah', fontsize=12)
    ax.set_title('Maintain dan Change per Tanggal (Side by Side)', fontsize=16, fontweight='bold')
    ax.legend(title='Kategori', labels=['Maintain', 'Change'])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_rank_comparison_chart(df):
    """Grafik Perbandingan Maintain vs Change per Rank"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    rank_pivot = df.groupby(['Rank', 'Kategori']).size().unstack(fill_value=0)
    rank_pivot.plot(kind='bar', color=['#2ecc71', '#e74c3c'], ax=ax, width=0.7)
    
    ax.set_xlabel('Rank', fontsize=12)
    ax.set_ylabel('Jumlah', fontsize=12)
    ax.set_title('Maintain dan Change per Rank', fontsize=16, fontweight='bold')
    ax.legend(title='Kategori', labels=['Maintain', 'Change'])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================
# MAIN APP
# ============================================

if planned_file is not None and actual_file is not None:
    try:
        # Load data
        with st.spinner('📂 Membaca file...'):
            planned_df = pd.read_excel(planned_file, header=1)
            actual_df = pd.read_excel(actual_file, header=1)
        
        st.success(f"✅ Data berhasil dimuat! Planned: {len(planned_df)} rows, Actual: {len(actual_df)} rows")
        
        # Setting kolom ID
        id_columns = ['No', 'Crew ID', 'Crew Name', 'Company', 'Rank', 'Period', 'Training Qualification', 'Under Training Status']
        
        # Analisis data
        with st.spinner('🔍 Menganalisis data...'):
            changes_df = analyze_schedule(planned_df, actual_df, id_columns)
        
        st.success("✅ Analisis selesai!")
        
        # ============================================
        # SIDEBAR - FILTER
        # ============================================
        st.sidebar.markdown("---")
        st.sidebar.header("🔍 Filter Data")
        
        # Filter Rank
        rank_options = ['All'] + sorted(changes_df['Rank'].unique().tolist())
        selected_rank = st.sidebar.selectbox(
            "Pilih Rank:",
            rank_options,
            help="Cockpit: CPT, FO | Cabin: Selain CPT & FO"
        )
        
        # Filter berdasarkan kategori rank
        if selected_rank == 'All':
            filtered_df = changes_df.copy()
            rank_label = "Semua Rank"
        elif selected_rank in ['CPT', 'FO']:
            filtered_df = changes_df[changes_df['Rank'] == selected_rank].copy()
            rank_label = f"Cockpit - {selected_rank}"
        else:
            filtered_df = changes_df[changes_df['Rank'] == 'Cabin'].copy()
            rank_label = "Cabin Crew"
        
        # Filter Tanggal (optional)
        st.sidebar.markdown("---")
        date_filter = st.sidebar.multiselect(
            "Filter Tanggal (opsional):",
            options=sorted(changes_df['Tanggal'].unique().tolist()),
            default=None,
            help="Kosongkan untuk melihat semua tanggal"
        )
        
        if date_filter:
            filtered_df = filtered_df[filtered_df['Tanggal'].isin(date_filter)]
        
        # ============================================
        # TAMPILAN UTAMA
        # ============================================
        
        # Header dengan info filter
        st.markdown(f"## 📊 Hasil Analisis - {rank_label}")
        st.markdown("---")
        
        # Statistik Umum
        col1, col2, col3, col4 = st.columns(4)
        
        total_data = len(filtered_df)
        maintain_count = len(filtered_df[filtered_df['Kategori'] == 'maintain'])
        change_count = len(filtered_df[filtered_df['Kategori'] == 'change'])
        total_crews = filtered_df['Crew Name'].nunique()
        
        with col1:
            st.metric("Total Data", f"{total_data:,}")
        with col2:
            st.metric("Maintain", f"{maintain_count:,}", 
                     delta=f"{maintain_count/total_data*100:.1f}%" if total_data > 0 else "0%")
        with col3:
            st.metric("Change", f"{change_count:,}", 
                     delta=f"{change_count/total_data*100:.1f}%" if total_data > 0 else "0%",
                     delta_color="inverse")
        with col4:
            st.metric("Total Crew", f"{total_crews}")
        
        st.markdown("---")
        
        # ============================================
        # TAB UNTUK VISUALISASI
        # ============================================
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "📅 Per Tanggal (Stacked)", 
            "📅 Per Tanggal (Grouped)",
            "👥 Per Rank",
            "📋 Data Detail"
        ])
        
        with tab1:
            st.subheader("Total Maintain vs Change")
            if len(filtered_df) > 0:
                fig1 = create_total_chart(filtered_df)
                st.pyplot(fig1)
                plt.close()
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab2:
            st.subheader("Maintain dan Change per Tanggal (Stacked)")
            if len(filtered_df) > 0:
                fig2 = create_daily_stacked_chart(filtered_df)
                st.pyplot(fig2)
                plt.close()
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab3:
            st.subheader("Maintain dan Change per Tanggal (Grouped)")
            if len(filtered_df) > 0:
                fig3 = create_daily_grouped_chart(filtered_df)
                st.pyplot(fig3)
                plt.close()
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab4:
            st.subheader("Maintain dan Change per Rank")
            if len(filtered_df) > 0:
                fig4 = create_rank_comparison_chart(filtered_df)
                st.pyplot(fig4)
                plt.close()
                
                # Tabel summary per rank
                st.markdown("### Ringkasan per Rank")
                rank_summary = filtered_df.groupby(['Rank', 'Kategori']).size().unstack(fill_value=0)
                rank_summary['Total'] = rank_summary.sum(axis=1)
                st.dataframe(rank_summary, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab5:
            st.subheader("Detail Data")
            
            # Tabel Maintain dan Change per Tanggal
            st.markdown("### 📅 Maintain dan Change per Tanggal")
            daily_summary = filtered_df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
            daily_summary['Total'] = daily_summary.sum(axis=1)
            daily_summary = daily_summary.reset_index()
            st.dataframe(daily_summary, use_container_width=True)
            
            # Tabel Detail Semua Data
            st.markdown("### 📋 Detail Semua Data")
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download button
            st.markdown("### 💾 Download Data")
            
            # Prepare Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='Detail Semua Data', index=False)
                daily_summary.to_excel(writer, sheet_name='Per Tanggal', index=False)
                
                # Summary per crew
                crew_summary = filtered_df.groupby(['Crew Name', 'Rank', 'Kategori']).size().unstack(fill_value=0)
                crew_summary['Total'] = crew_summary.sum(axis=1)
                crew_summary = crew_summary.sort_values('Total', ascending=False)
                crew_summary.to_excel(writer, sheet_name='Per Crew')
                
                # Summary total
                total_summary = filtered_df['Kategori'].value_counts().reset_index()
                total_summary.columns = ['Kategori', 'Jumlah']
                total_summary['Persentase'] = (total_summary['Jumlah'] / len(filtered_df) * 100).round(2)
                total_summary.to_excel(writer, sheet_name='Summary Total', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download Excel",
                data=output,
                file_name=f"Crew_Analysis_{rank_label.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Pastikan format file Excel sesuai dengan yang diharapkan")

else:
    # Tampilan awal sebelum upload
    st.info("👈 Silakan upload file Planned dan Actual Schedule di sidebar untuk memulai analisis")
    
    st.markdown("""
    ### 📝 Cara Menggunakan:
    
    1. **Upload File** - Upload file Excel untuk Planned dan Actual Schedule di sidebar
    2. **Pilih Filter** - Pilih Rank (Cockpit: CPT/FO atau Cabin)
    3. **Lihat Hasil** - Lihat visualisasi dan data di berbagai tab
    4. **Download** - Download hasil analisis dalam format Excel
    
    ### 🎯 Fitur:
    
    - ✅ Analisis Maintain vs Change
    - ✅ Filter berdasarkan Rank (Cockpit: CPT, FO | Cabin: lainnya)
    - ✅ Filter berdasarkan Tanggal
    - ✅ Visualisasi interaktif per tanggal dan per rank
    - ✅ Export hasil ke Excel
    
    ### 📊 Kategori:
    
    - **Maintain** - Schedule tidak berubah antara planned dan actual
    - **Change** - Schedule berubah antara planned dan actual
    
    ### 👥 Rank:
    
    - **Cockpit** - CPT (Captain) dan FO (First Officer)
    - **Cabin** - Selain CPT dan FO
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>✈️ Crew Schedule Change Analysis v1.0</p>
    </div>
    """,
    unsafe_allow_html=True
)