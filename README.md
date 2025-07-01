# 🫁 Sistem Prediksi Risiko Penyakit Paru

## 📝 Deskripsi Singkat

Sistem AI untuk prediksi risiko penyakit paru yang menggabungkan analisis citra X-Ray dengan data kualitas udara real-time. Menggunakan dual model AI (ResNet + Logistic Regression) dengan bobot 85% untuk faktor lingkungan dan 15% untuk model ML tradisional.

**Proyek Akhir**: Big Data dalam Bidang Medis
**Link Video Yotube** : https://youtu.be/1-W6jM2MEQE
## ✨ Fitur Utama

- **🔍 Klasifikasi X-Ray**: ResNet model untuk deteksi Normal/COVID-19/Pneumonia/TB
- **🌍 Data Real-time**: Integrasi 13+ kota Indonesia dengan aqicn.org API
- **⚖️ Enhanced Prediction**: AQI weighting 85% + LogReg 15% untuk akurasi tinggi
- **📊 Risk Classification**: AQI <100 (Rendah), 100-150 (Sedang), >150 (Tinggi)
- **🔄 Fallback System**: Multi-layer fallback untuk 99.9% uptime
- **📱 Modern UI**: React interface dengan real-time indicators

## 🏗️ Arsitektur Proyek

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│                 │    │                 │    │                 │
│ • React UI      │───▶│ • Django Views  │───▶│ • aqicn.org API │
│ • City Select   │    │ • URL Routing   │    │ • Air Quality   │
│ • Image Upload  │    │ • File Handling │    │ • Real-time AQI │
│ • Results       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   AI/ML Layer   │
                       │                 │
                       │ • ResNet Model  │
                       │ • LogReg Model  │
                       │ • Enhanced Pred │
                       │ • AQI Weighting │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### **Backend**
- **Framework**: Django 5.2
- **Language**: Python 3.8+
- **Database**: SQLite

### **AI/ML**
- **Deep Learning**: TensorFlow/Keras (ResNet)
- **Machine Learning**: scikit-learn (Logistic Regression)
- **Image Processing**: PIL/Pillow
- **Data Processing**: NumPy, Pandas

### **Frontend**
- **Framework**: React 18 (via CDN)
- **Styling**: CSS3 + Font Awesome
- **JavaScript**: ES6+ with Babel

### **External APIs**
- **Air Quality**: aqicn.org API
- **Backup**: OpenAQ API

## 📁 Struktur Proyek

```
lung_prediction_system/
├── 🏗️ Core
│   ├── lung_prediction_system/     # Django project config
│   ├── prediction/                 # Main app
│   │   ├── views.py               # Main controllers
│   │   ├── urls.py                # URL routing
│   │   └── templates/index.html   # React frontend
│   └── manage.py                  # Django CLI
│
├── 🤖 AI/ML
│   ├── prediction/
│   │   ├── ml_models.py           # ResNet wrapper
│   │   ├── logreg_model.py        # LogReg wrapper  
│   │   └── enhanced_risk_prediction.py  # AQI weighting
│   └── models/
│       ├── final_resnet_xray_model.h5   # Trained ResNet
│       └── multiclass_model.joblib      # Trained LogReg
│
├── 🌍 Data Integration
│   └── prediction/
│       ├── aqicn_integration.py   # Real-time air quality
│       └── openaq_integration.py  # Alternative API
│
└── 🧪 Testing
    ├── test_enhanced_integration.py   # System tests
    ├── test_realtime_data.py         # Data verification
    └── debug_backend.py              # Debug utilities
```

## 🚀 Cara Implementasi

### 1. **Setup Environment**
```bash
# Clone & navigate
git clone <repository>
cd lung_prediction_system

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install django tensorflow scikit-learn pillow numpy requests
```

### 2. **Configure Database**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. **Setup ML Models**
```bash
# Ensure model files exist:
# models/final_resnet_xray_model.h5
# models/multiclass_model.joblib
```

### 4. **API Configuration**
```python
# prediction/aqicn_integration.py
AQICN_API_KEY = "452d02260843c9375aa32ee052ea2abc527a2a87"
```

### 5. **Launch System**
```bash
# Test system
python test_enhanced_integration.py

# Start server
python manage.py runserver

# Access: http://localhost:8000/
```

### 6. **Verify Installation**
- ✅ Homepage loads dengan 14 Indonesian cities
- ✅ Select city shows real-time AQI data
- ✅ Upload X-ray image works
- ✅ Prediction returns enhanced results

## 📊 Sumber Data

### **Real-time Air Quality**
- **Primary**: [aqicn.org](https://aqicn.org) - 13+ Indonesian cities
  - Jakarta, Medan, Semarang, Palembang, Malang
  - Yogyakarta, Pontianak, Bengkulu, Pekanbaru
  - Bekasi, Tangerang, Depok, Batu
- **Backup**: [OpenAQ.org](https://openaq.org) - Global air quality database
- **Parameters**: PM2.5, PM10, PM1, humidity, temperature, AQI

### **Machine Learning Models**
- **ResNet Model**: Pre-trained untuk X-ray classification
  - **Classes**: Normal, COVID-19, Pneumonia, Tuberkulosis
  - **Input**: 224x224 RGB images
  - **Output**: Classification + confidence scores

- **Logistic Regression**: Environmental risk prediction
  - **Features**: PM1, PM10, PM2.5, humidity, temperature, location
  - **Output**: Risk probabilities (Rendah/Sedang/Tinggi)
  - **Training Data**: Indonesian environmental + health case data

### **Static Fallback Data**
- **Indonesian Cities**: Static AQI estimates untuk 13 cities
- **Default Values**: Country-level air quality estimates
- **Reliability**: 24/7 availability bahkan ketika APIs down

---

## 📈 Quick Results

**Enhanced Prediction Example:**
- **Location**: Jakarta (Real-time AQI: 151)
- **X-ray**: Normal
- **LogReg Original**: Rendah (60% confidence)
- **Enhanced Result**: Sedang (87% confidence) - AQI dominates
- **Breakdown**: 85% environmental + 15% ML weighting

---

*© 2024 - Big Data dalam Bidang Medis Course Project*
