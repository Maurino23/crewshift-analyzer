# ✈️ CrewShift Analyzer

**CrewShift Analyzer** adalah aplikasi web interaktif untuk menganalisis perubahan jadwal crew penerbangan. Aplikasi ini membandingkan jadwal yang direncanakan (planned schedule) dengan jadwal aktual (actual schedule) untuk mengidentifikasi perubahan dan memberikan insight yang actionable.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 🎯 Fitur Utama

- ✅ **Analisis Otomatis** - Bandingkan planned vs actual schedule dengan satu klik
- 📊 **Visualisasi Interaktif** - Grafik yang mudah dipahami untuk presentasi
- 🔍 **Filter Multi-Level** - Filter berdasarkan Rank (Cockpit/Cabin) dan Tanggal
- 👥 **Kategori Rank** - Otomatis mengelompokkan CPT, FO, dan Cabin Crew
- 📈 **Analisis Per Tanggal** - Lihat tren maintain dan change per hari
- 💾 **Export Excel** - Download hasil analisis lengkap dalam format Excel
- 🚀 **User-Friendly** - Interface yang intuitif dan mudah digunakan

---

## 📊 Kategori Analisis

### **Maintain**
Schedule yang **tidak berubah** antara planned dan actual

### **Change**
Schedule yang **berubah** antara planned dan actual

### **Rank Categories**
- **Cockpit**: CPT (Captain) dan FO (First Officer)
- **Cabin**: Seluruh crew selain CPT dan FO

---

## 🚀 Cara Menggunakan

### 1. **Upload Data**
- Upload file Excel untuk **Planned Schedule**
- Upload file Excel untuk **Actual Schedule**

### 2. **Pilih Filter**
- Pilih **Rank**: All, CPT, FO, atau Cabin
- (Opsional) Pilih **Tanggal** tertentu

### 3. **Lihat Hasil**
Jelajahi 5 tab berbeda:
- 📊 **Overview** - Total maintain vs change
- 📅 **Per Tanggal (Stacked)** - Grafik bertumpuk
- 📅 **Per Tanggal (Grouped)** - Grafik bersebelahan
- 👥 **Per Rank** - Perbandingan antar rank
- 📋 **Data Detail** - Tabel lengkap

### 4. **Download Hasil**
Export hasil analisis dalam format Excel dengan 4 sheet berbeda

---

## 💻 Instalasi Lokal

### **Requirements**
- Python 3.8 atau lebih baru
- pip (Python package manager)

### **Langkah Instalasi**

1. **Clone repository**
```bash
git clone https://github.com/username/crewshift-analyzer.git
cd crewshift-analyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Jalankan aplikasi**
```bash
streamlit run app.py
```

4. **Buka browser**
```
http://localhost:8501
```

---

## 📦 Dependencies

```text
streamlit
pandas
openpyxl
matplotlib
seaborn
```

---

## 📁 Struktur Data Input

### Format File Excel yang Diperlukan:

**Kolom Wajib:**
- `Crew ID` - ID unik crew
- `Crew Name` - Nama crew
- `Company Bank` - Bank perusahaan
- `Period` - Periode (contoh: Jun-2025)
- `Training Qualification` - Kualifikasi training
- `Under Training Status` - Status training
- `1` sampai `31` - Kolom untuk setiap tanggal dalam sebulan

**Contoh Format:**
```
| Crew ID | Crew Name | Company Bank | Period   | 1    | 2    | 3    | ... | 31   |
|---------|-----------|--------------|----------|------|------|------|-----|------|
| 52010011| JOHN DOE  | JT           | Jun-2025 | OFF  | JT123| OFF  | ... | JT456|
```

---

## 🎨 Screenshot

### Dashboard Utama
*[Tambahkan screenshot aplikasi Anda di sini]*

### Grafik Analisis
*[Tambahkan screenshot grafik di sini]*

---

## 🔧 Konfigurasi

### Deteksi Rank
Aplikasi otomatis mendeteksi rank berdasarkan `Crew ID`. Anda dapat menyesuaikan logika deteksi di fungsi `detect_rank()`:

```python
def detect_rank(crew_id):
    crew_id_str = str(crew_id).upper()
    
    if 'CPT' in crew_id_str or crew_id_str.startswith('52'):
        return 'CPT'
    elif 'FO' in crew_id_str or crew_id_str.startswith('53'):
        return 'FO'
    else:
        return 'Cabin'
```

---

## 📊 Output Excel

File Excel yang dihasilkan berisi 4 sheet:

1. **Detail Semua Data** - Data lengkap setiap crew dan tanggal
2. **Maintain-Change per Tanggal** - Summary per tanggal
3. **Maintain-Change per Crew** - Summary per crew
4. **Summary Total** - Ringkasan keseluruhan dengan persentase

---

## 🤝 Kontribusi

Kontribusi selalu diterima! Jika Anda ingin berkontribusi:

1. Fork repository ini
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

---

## 📝 Changelog

### Version 1.0.0 (2025-09-30)
- ✅ Initial release
- ✅ Fitur upload dan analisis schedule
- ✅ Filter berdasarkan Rank dan Tanggal
- ✅ 5 tab visualisasi interaktif
- ✅ Export ke Excel

---

## 📄 License

Project ini menggunakan MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

## 👨‍💻 Author

**Rino**
- 📧 Email: [audrianmaurino@gmail.com]
- 💼 LinkedIn: [Your LinkedIn Profile]
- 🐙 GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Framework aplikasi web
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) - Visualisasi data

---

## 📞 Support

Jika Anda mengalami masalah atau punya pertanyaan:
- 🐛 **Bug Reports**: [Create an issue](https://github.com/username/crewshift-analyzer/issues)
- 💬 **Questions**: [Start a discussion](https://github.com/username/crewshift-analyzer/discussions)
- 📧 **Email**: email@example.com

---

<div align="center">

**⭐ Jika aplikasi ini membantu Anda, berikan star di GitHub! ⭐**

Made with ❤️ by Rino

</div>
