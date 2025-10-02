import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="CrewShift Analyzer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
    <style>
    .main-metric {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# JUDUL APLIKASI
# ============================================
st.title("✈️ CrewShift Analyzer")
st.markdown("*Analyze Flight Crew Schedule Changes*")
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
def detect_rank(rank_value):
    """
    Deteksi kategori rank berdasarkan kolom 'Rank' di data
    CPT atau FO = Cockpit
    Selain CPT dan FO = Cabin
    """
    rank_str = str(rank_value).upper().strip()
    
    # Jika Rank adalah CPT atau FO = Cockpit
    if rank_str in ['CPT', 'FO']:
        return 'Cockpit'
    # Selain CPT dan FO = Cabin
    else:
        return 'Cabin'

# ============================================
# FUNGSI ANALISIS
# ============================================
@st.cache_data
def analyze_schedule(planned_df, actual_df, id_columns):
    """
    Fungsi untuk menganalisis perubahan schedule
    Menggunakan Crew ID sebagai kunci untuk matching
    """
    # Identifikasi kolom tanggal
    date_columns = [col for col in planned_df.columns if col not in id_columns]
    
    all_changes = []
    
    # Buat dictionary dari actual_df untuk lookup lebih cepat
    # Key: Crew ID, Value: row data
    actual_dict = {}
    for idx in range(len(actual_df)):
        crew_id = actual_df.iloc[idx]['Crew ID']
        actual_dict[crew_id] = actual_df.iloc[idx]
    
    # Loop setiap crew di planned
    for idx in range(len(planned_df)):
        crew_id = planned_df.iloc[idx]['Crew ID']
        crew_name = planned_df.iloc[idx]['Crew Name']
        rank_value = planned_df.iloc[idx]['Rank']
        
        # Detect rank berdasarkan kolom Rank
        rank = detect_rank(rank_value)
        
        # Cek apakah crew ini ada di actual
        if crew_id not in actual_dict:
            # Crew sudah OUT (ada di planned, tidak ada di actual)
            # Skip crew ini atau bisa ditandai sebagai "OUT"
            continue
        
        actual_row = actual_dict[crew_id]
        
        # Loop setiap tanggal
        for date_col in date_columns:
            # Ambil nilai planned dan actual
            planned_val = str(planned_df.iloc[idx][date_col])
            actual_val = str(actual_row[date_col])
            
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
    
    # Tambahkan crew baru yang ada di actual tapi tidak di planned
    planned_crew_ids = set(planned_df['Crew ID'].tolist())
    
    for idx in range(len(actual_df)):
        crew_id = actual_df.iloc[idx]['Crew ID']
        
        # Jika crew ini tidak ada di planned (crew baru)
        if crew_id not in planned_crew_ids:
            crew_name = actual_df.iloc[idx]['Crew Name']
            rank_value = actual_df.iloc[idx]['Rank']
            rank = detect_rank(rank_value)
            
            # Loop setiap tanggal untuk crew baru
            for date_col in date_columns:
                actual_val = str(actual_df.iloc[idx][date_col])
                
                # Bersihkan nilai kosong
                if actual_val == 'nan':
                    actual_val = '-'
                
                # Crew baru: planned = '-', actual = nilai dari data
                all_changes.append({
                    'Crew ID': crew_id,
                    'Crew Name': crew_name,
                    'Rank': rank,
                    'Tanggal': date_col,
                    'Planned': '-',
                    'Actual': actual_val,
                    'Kategori': 'change' if actual_val != '-' else 'maintain'
                })
    
    changes_df = pd.DataFrame(all_changes)
    return changes_df

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
        id_columns = ['No', 'Crew ID', 'Crew Name', 'Company', 'Rank', 'Period', 'Training Qualification', 'Under Training Status', 'Crew Category']
        
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
        rank_options = ['All', 'Cockpit', 'Cabin']
        selected_rank = st.sidebar.selectbox(
            "Pilih Rank:",
            rank_options,
            help="Cockpit: CPT, FO | Cabin: Selain CPT & FO"
        )
        
        # Filter berdasarkan rank
        if selected_rank == 'All':
            filtered_df = changes_df.copy()
            rank_label = "Semua Rank"
        else:
            filtered_df = changes_df[changes_df['Rank'] == selected_rank].copy()
            rank_label = selected_rank
        
        # Filter Tanggal (optional)
        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Filter Tanggal")
        
        # Opsi filter tanggal
        date_filter_option = st.sidebar.radio(
            "Pilih metode filter:",
            ["Semua Tanggal", "Range Tanggal", "Pilih Tanggal Spesifik"],
            help="Pilih cara filter tanggal yang Anda inginkan"
        )
        
        if date_filter_option == "Range Tanggal":
            # Konversi tanggal ke integer untuk slider
            all_dates = sorted([int(d) for d in changes_df['Tanggal'].unique()])
            
            col_date1, col_date2 = st.sidebar.columns(2)
            with col_date1:
                start_date = st.number_input(
                    "Dari Tanggal:",
                    min_value=min(all_dates),
                    max_value=max(all_dates),
                    value=min(all_dates),
                    step=1
                )
            with col_date2:
                end_date = st.number_input(
                    "Sampai Tanggal:",
                    min_value=min(all_dates),
                    max_value=max(all_dates),
                    value=max(all_dates),
                    step=1
                )
            
            # Filter berdasarkan range
            filtered_df = filtered_df[
                (filtered_df['Tanggal'].astype(int) >= start_date) & 
                (filtered_df['Tanggal'].astype(int) <= end_date)
            ]
            
            st.sidebar.success(f"📊 Menampilkan data dari tanggal {start_date} s/d {end_date}")
            
        elif date_filter_option == "Pilih Tanggal Spesifik":
            date_filter = st.sidebar.multiselect(
                "Pilih tanggal:",
                options=sorted(changes_df['Tanggal'].unique().tolist()),
                default=None,
                help="Pilih satu atau lebih tanggal"
            )
            
            if date_filter:
                filtered_df = filtered_df[filtered_df['Tanggal'].isin(date_filter)]
                st.sidebar.success(f"📊 Menampilkan {len(date_filter)} tanggal terpilih")
            else:
                st.sidebar.info("💡 Pilih minimal 1 tanggal")
        
        else:  # Semua Tanggal
            st.sidebar.info("📊 Menampilkan semua tanggal")
        
        # ============================================
        # TAMPILAN UTAMA
        # ============================================
        
        # Header dengan info filter
        st.markdown(f"## 📊 Hasil Analisis - {rank_label}")
        st.markdown("---")
        
        # Statistik Umum
        total_data = len(filtered_df)
        maintain_count = len(filtered_df[filtered_df['Kategori'] == 'maintain'])
        change_count = len(filtered_df[filtered_df['Kategori'] == 'change'])
        total_crews = filtered_df['Crew ID'].nunique()
        
        maintain_pct = (maintain_count/total_data*100) if total_data > 0 else 0
        change_pct = (change_count/total_data*100) if total_data > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Data", f"{total_data:,}")
        with col2:
            st.metric("Maintain", f"{maintain_pct:.1f}%", 
                     delta=f"{maintain_count:,} items")
        with col3:
            st.metric("Change", f"{change_pct:.1f}%", 
                     delta=f"{change_count:,} items",
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
                # Hitung data
                kategori_counts = filtered_df['Kategori'].value_counts()
                kategori_pct = (kategori_counts / len(filtered_df) * 100).round(1)
                
                # Buat dataframe untuk chart
                chart_data = pd.DataFrame({
                    'Kategori': kategori_counts.index,
                    'Jumlah': kategori_counts.values,
                    'Persentase': kategori_pct.values
                })
                
                # Chart dengan Plotly
                fig = go.Figure()
                
                colors = {'maintain': '#2ecc71', 'change': '#e74c3c'}
                
                for idx, row in chart_data.iterrows():
                    fig.add_trace(go.Bar(
                        x=[row['Kategori']],
                        y=[row['Jumlah']],
                        name=row['Kategori'],
                        text=[f"{row['Persentase']:.1f}%<br>({int(row['Jumlah'])} items)"],
                        textposition='outside',
                        marker_color=colors.get(row['Kategori'], '#3498db'),
                        showlegend=False
                    ))
                
                fig.update_layout(
                    title="Total Maintain vs Change",
                    xaxis_title="Kategori",
                    yaxis_title="Jumlah",
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabel summary
                st.markdown("### 📊 Summary Statistics")
                summary_df = pd.DataFrame({
                    'Kategori': chart_data['Kategori'],
                    'Jumlah': chart_data['Jumlah'],
                    'Persentase': chart_data['Persentase'].apply(lambda x: f"{x:.1f}%")
                })
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab2:
            st.subheader("Maintain dan Change per Tanggal (Stacked)")
            if len(filtered_df) > 0:
                # Pivot data
                daily_pivot = filtered_df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
                daily_pivot_pct = (daily_pivot.div(daily_pivot.sum(axis=1), axis=0) * 100).round(1)
                
                # Buat stacked bar chart
                fig = go.Figure()
                
                colors = {'maintain': '#2ecc71', 'change': '#e74c3c'}
                
                for kategori in daily_pivot.columns:
                    # Buat text labels dengan persentase dan jumlah
                    text_labels = []
                    for idx, tanggal in enumerate(daily_pivot.index):
                        count = daily_pivot.loc[tanggal, kategori]
                        pct = daily_pivot_pct.loc[tanggal, kategori]
                        # Hanya tampilkan jika ada nilai (tidak 0)
                        if count > 0:
                            text_labels.append(f"{pct:.1f}%<br>({int(count)})")
                        else:
                            text_labels.append("")
                    
                    customdata = []
                    for idx, tanggal in enumerate(daily_pivot.index):
                        count = daily_pivot.loc[tanggal, kategori]
                        pct = daily_pivot_pct.loc[tanggal, kategori]
                        customdata.append([count, pct])
                    
                    fig.add_trace(go.Bar(
                        x=daily_pivot.index,
                        y=daily_pivot[kategori],
                        name=kategori.capitalize(),
                        marker_color=colors.get(kategori, '#3498db'),
                        text=text_labels,
                        textposition='inside',
                        textfont=dict(size=10, color='white'),
                        customdata=customdata,
                        hovertemplate='<b>Tanggal %{x}</b><br>' +
                                    'Kategori: ' + kategori + '<br>' +
                                    'Jumlah: %{customdata[0]}<br>' +
                                    'Persentase: %{customdata[1]:.1f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Maintain dan Change per Tanggal (Stacked)",
                    xaxis_title="Tanggal",
                    yaxis_title="Jumlah",
                    barmode='stack',
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab3:
            st.subheader("Maintain dan Change per Tanggal (Grouped)")
            if len(filtered_df) > 0:
                # Pivot data
                daily_pivot = filtered_df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
                daily_pivot_pct = (daily_pivot.div(daily_pivot.sum(axis=1), axis=0) * 100).round(1)
                
                # Buat grouped bar chart
                fig = go.Figure()
                
                colors = {'maintain': '#2ecc71', 'change': '#e74c3c'}
                
                for kategori in daily_pivot.columns:
                    # Buat text labels dengan persentase dan jumlah
                    text_labels = []
                    for idx, tanggal in enumerate(daily_pivot.index):
                        count = daily_pivot.loc[tanggal, kategori]
                        pct = daily_pivot_pct.loc[tanggal, kategori]
                        # Hanya tampilkan jika ada nilai (tidak 0)
                        if count > 0:
                            text_labels.append(f"{pct:.1f}%<br>({int(count)})")
                        else:
                            text_labels.append("")
                    
                    customdata = []
                    for idx, tanggal in enumerate(daily_pivot.index):
                        count = daily_pivot.loc[tanggal, kategori]
                        pct = daily_pivot_pct.loc[tanggal, kategori]
                        customdata.append([count, pct])
                    
                    fig.add_trace(go.Bar(
                        x=daily_pivot.index,
                        y=daily_pivot[kategori],
                        name=kategori.capitalize(),
                        marker_color=colors.get(kategori, '#3498db'),
                        text=text_labels,
                        textposition='outside',
                        textfont=dict(size=10),
                        customdata=customdata,
                        hovertemplate='<b>Tanggal %{x}</b><br>' +
                                    'Kategori: ' + kategori + '<br>' +
                                    'Jumlah: %{customdata[0]}<br>' +
                                    'Persentase: %{customdata[1]:.1f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Maintain dan Change per Tanggal (Grouped)",
                    xaxis_title="Tanggal",
                    yaxis_title="Jumlah",
                    barmode='group',
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab4:
            st.subheader("Maintain dan Change per Rank")
            if len(filtered_df) > 0:
                # Pivot data
                rank_pivot = filtered_df.groupby(['Rank', 'Kategori']).size().unstack(fill_value=0)
                rank_pivot_pct = (rank_pivot.div(rank_pivot.sum(axis=1), axis=0) * 100).round(1)
                
                # Buat grouped bar chart
                fig = go.Figure()
                
                colors = {'maintain': '#2ecc71', 'change': '#e74c3c'}
                
                for kategori in rank_pivot.columns:
                    customdata = []
                    for idx, rank in enumerate(rank_pivot.index):
                        count = rank_pivot.loc[rank, kategori]
                        pct = rank_pivot_pct.loc[rank, kategori]
                        customdata.append([count, pct])
                    
                    fig.add_trace(go.Bar(
                        x=rank_pivot.index,
                        y=rank_pivot[kategori],
                        name=kategori.capitalize(),
                        marker_color=colors.get(kategori, '#3498db'),
                        text=[f"{customdata[i][1]:.1f}%<br>({customdata[i][0]} items)" 
                              for i in range(len(customdata))],
                        textposition='outside',
                        customdata=customdata,
                        hovertemplate='<b>%{x}</b><br>' +
                                    'Kategori: ' + kategori + '<br>' +
                                    'Jumlah: %{customdata[0]}<br>' +
                                    'Persentase: %{customdata[1]:.1f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Maintain dan Change per Rank",
                    xaxis_title="Rank",
                    yaxis_title="Jumlah",
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabel summary per rank
                st.markdown("### 📊 Ringkasan per Rank")
                rank_summary_display = rank_pivot.copy()
                rank_summary_display['Total'] = rank_summary_display.sum(axis=1)
                
                # Tambahkan persentase
                for col in rank_pivot.columns:
                    rank_summary_display[f'{col} (%)'] = rank_pivot_pct[col].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(rank_summary_display, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan")
        
        with tab5:
            st.subheader("Detail Data")
            
            # Tabel Maintain dan Change per Tanggal
            st.markdown("### 📅 Maintain dan Change per Tanggal")
            daily_summary = filtered_df.groupby(['Tanggal', 'Kategori']).size().unstack(fill_value=0)
            daily_summary['Total'] = daily_summary.sum(axis=1)
            
            # Tambahkan persentase
            daily_summary_pct = (daily_summary[['maintain', 'change']].div(daily_summary['Total'], axis=0) * 100).round(1)
            daily_summary['Maintain (%)'] = daily_summary_pct['maintain'].apply(lambda x: f"{x:.1f}%")
            daily_summary['Change (%)'] = daily_summary_pct['change'].apply(lambda x: f"{x:.1f}%")
            
            daily_summary = daily_summary.reset_index()
            st.dataframe(daily_summary, use_container_width=True, hide_index=True)
            
            # Tabel Detail Semua Data
            st.markdown("### 📋 Detail Semua Data")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
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
                total_summary['Persentase'] = (total_summary['Jumlah'] / len(filtered_df) * 100).round(2).apply(lambda x: f"{x:.2f}%")
                total_summary.to_excel(writer, sheet_name='Summary Total', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download Excel",
                data=output,
                file_name=f"CrewShift_Analysis_{rank_label.replace(' ', '_')}.xlsx",
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
    2. **Pilih Filter** - Pilih Rank (All, Cockpit, atau Cabin)
    3. **Lihat Hasil** - Lihat visualisasi dan data di berbagai tab
    4. **Download** - Download hasil analisis dalam format Excel
    
    ### 🎯 Fitur:
    
    - ✅ Analisis Maintain vs Change
    - ✅ Filter berdasarkan Rank (Cockpit atau Cabin)
    - ✅ Filter berdasarkan Tanggal
    - ✅ Visualisasi interaktif dengan Plotly
    - ✅ Data ditampilkan dalam persentase dan jumlah
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
        <p>✈️ CrewShift Analyzer v1.0 | Made with ❤️ by Rino</p>
    </div>
    """,
    unsafe_allow_html=True
)
