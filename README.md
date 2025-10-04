# ✈️ Military Aircraft Search Engine

Doğal dil tabanlı askeri uçak fotoğrafı arama motoru. OpenAI'nin CLIP modeli ve Faiss vektör veritabanı kullanılarak geliştirilmiştir.

> 🎉 **Hazır Kullanım**: Bu repository, önceden oluşturulmuş embedding dosyalarını (~131 MB) içermektedir. Sadece veri setini indirip hemen kullanmaya başlayabilirsiniz.

## 🎯 Proje Özeti

Bu proje, uçak fotoğraflarını doğal dil sorguları ile arama yapabilen bir web uygulamasıdır. Kullanıcılar "F-35 weapon bay door", "cockpit view", "landing gear" gibi metinsel ifadelerle binlerce fotoğraf arasından en alakalı görselleri bulabilir.

### Ana Özellikler

- 🔍 **Doğal Dil Araması**: Metinsel açıklamalar ile görsel arama
- 🚀 **Hızlı Sonuçlar**: Faiss ile optimize edilmiş vektör araması
- 🎨 **Modern Arayüz**: Responsive ve kullanıcı dostu tasarım
- 📊 **Benzerlik Skorları**: Her sonuç için benzerlik yüzdesi
- 🖼️ **Modal Görüntüleme**: Fotoğrafları tam ekran görüntüleme
- ⚡ **GPU Desteği**: CUDA ile hızlandırılmış işleme (opsiyonel)

## 🛠️ Teknolojiler

### Backend
- **Python 3.8+**
- **Flask**: Web framework
- **PyTorch**: Derin öğrenme framework'ü
- **Transformers (Hugging Face)**: CLIP modeli için
- **Faiss**: Vektör benzerlik araması için
- **Pillow & OpenCV**: Görüntü işleme

### Frontend
- **HTML5 & CSS3**
- **Vanilla JavaScript**: Framework'süz, performanslı
- **Responsive Design**: Mobil uyumlu

### AI Model
- **CLIP (openai/clip-vit-large-patch14)**: Görüntü-metin eşleştirme modeli

## 📁 Proje Yapısı

```
airplaneSearchEngine/
├── app.py                      # Flask uygulaması
├── config.py                   # Konfigürasyon ayarları
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Proje dokümantasyonu
│
├── models/                     # Model sınıfları
│   ├── __init__.py
│   └── vector_db.py           # Faiss veritabanı wrapper
│
├── scripts/                    # Yardımcı scriptler
│   └── create_embeddings.py   # Embedding oluşturma scripti
│
├── data/                       # Veri klasörü
│   ├── airplane_photos/       # Uçak fotoğrafları (buraya ekleyin)
│   └── embeddings/            # Oluşturulan vektörler ve metadata
│
├── static/                     # Statik dosyalar
│   ├── css/
│   │   └── style.css          # CSS stilleri
│   └── js/
│       └── app.js             # Frontend JavaScript
│
└── templates/                  # HTML şablonları
    └── index.html             # Ana sayfa
```

## 🚀 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/talhakenan1/military-aircraft-search-engine.git
cd military-aircraft-search-engine
```

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**Not**: PyTorch kurulumu için GPU desteği istiyorsanız, [PyTorch resmi sitesinden](https://pytorch.org/get-started/locally/) sisteminize uygun komutu kullanın.

### 4. Veri Setini İndirin

#### 📦 Veri Seti Hakkında

Bu proje, **Kaggle** üzerinde bulunan açık kaynaklı military aircraft veri setini kullanmaktadır:

**Veri Seti Kaynağı**: [Military Aircraft Recognition Dataset](https://www.kaggle.com/datasets) (Kaggle)
- **Boyut**: ~5.4 GB
- **Görsel Sayısı**: 40,000+ fotoğraf
- **Format**: JPG, PNG
- **İçerik**: Çeşitli askeri uçakların farklı açılardan çekilmiş fotoğrafları

#### İndirme Adımları:

**Seçenek 1: Kaggle CLI (Önerilen)**

1. Kaggle hesabı oluşturun (ücretsiz): [kaggle.com](https://www.kaggle.com)
2. Kaggle API token'ınızı indirin: [kaggle.com/settings](https://www.kaggle.com/account) → "Create New API Token"
3. `kaggle.json` dosyasını uygun konuma yerleştirin:
   - **Windows**: `C:\Users\<username>\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`
4. Veri setini indirin:

```bash
# Kaggle CLI'ı kurun
pip install kaggle

# Veri setini indirin (dataset adını güncelleyin)
kaggle datasets download -d <dataset-username>/<dataset-name>

# Zip dosyasını açın
unzip <dataset-name>.zip -d data/airplane_photos/
```

**Seçenek 2: Manuel İndirme**

1. Kaggle veri seti sayfasına gidin
2. "Download" butonuna tıklayın
3. İndirilen zip dosyasını `data/airplane_photos/` klasörüne çıkarın

**Seçenek 3: Kendi Veri Setiniz**

Kendi uçak fotoğraflarınızı kullanabilirsiniz:

```bash
data/airplane_photos/
├── F-35/
│   ├── image1.jpg
│   └── image2.png
├── Su-57/
│   └── image3.jpg
└── ...
```

**Desteklenen formatlar**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`

### 5. Embedding'leri Oluşturun (Opsiyonel)

> **⚠️ ÖNEMLİ**: Bu repository, **önceden oluşturulmuş embedding dosyalarını** içermektedir (`data/embeddings/`).
> Eğer aynı veri setini kullanıyorsanız, bu adımı atlayabilirsiniz ve direkt 6. adıma geçebilirsiniz.

Kendi veri setinizi kullanıyorsanız veya embedding'leri yeniden oluşturmak istiyorsanız:

```bash
python scripts/create_embeddings.py
```

Bu işlem:
- Tüm fotoğrafları tarar
- Her fotoğraf için CLIP ile embedding oluşturur
- Faiss index'i ve metadata'yı `data/embeddings/` klasörüne kaydeder

**Süre**: 
- ~40,000 görsel için: 2-3 saat (GPU ile) veya 8-12 saat (CPU ile)
- Fotoğraf sayısına ve donanıma bağlı olarak değişir

### 6. Web Uygulamasını Başlatın

```bash
python app.py
```

Tarayıcınızda şu adresi açın: **http://localhost:5000**

## 📖 Kullanım

### Web Arayüzü

1. Arama kutusuna sorgunuzu girin (örn: "F-35 weapon bay door")
2. Sonuç sayısını seçin (10-100 arası)
3. "Ara" butonuna tıklayın veya Enter tuşuna basın
4. Sonuçlar benzerlik skoruna göre sıralanarak gösterilir
5. Bir fotoğrafa tıklayarak büyütülmüş görüntüleyin

### Örnek Sorgular

- `F-35 weapon bay door` - Silah bölmesi kapağı
- `F-15 bottom view` - Alt görünüm
- `Su-57 assembly line` - Montaj hattı
- `cockpit view` - Kokpit görünümü
- `landing gear` - İniş takımı
- `arresting hook` - Yakalama kancası

### API Kullanımı

#### Arama Endpoint'i

```bash
POST /api/search
Content-Type: application/json

{
    "query": "F-35 weapon bay door",
    "top_k": 50
}
```

**Response:**

```json
{
    "success": true,
    "query": "F-35 weapon bay door",
    "total_results": 50,
    "results": [
        {
            "id": 123,
            "filename": "f35_bay.jpg",
            "path": "f35_bay.jpg",
            "similarity_score": 0.8542,
            "rank": 1,
            "image_url": "/api/image/f35_bay.jpg"
        },
        ...
    ]
}
```

#### İstatistik Endpoint'i

```bash
GET /api/stats
```

## ⚙️ Konfigürasyon

`config.py` dosyasında ayarları değiştirebilirsiniz:

```python
# Model Ayarları
CLIP_MODEL_NAME = "openai/clip-vit-large-patch14"  # veya "openai/clip-vit-base-patch32"
EMBEDDING_DIM = 768  # Model çıktı boyutu

# İşleme Ayarları
BATCH_SIZE = 32  # GPU belleğine göre ayarlayın
MAX_IMAGE_SIZE = (512, 512)  # Maksimum görüntü boyutu

# Arama Ayarları
DEFAULT_TOP_K = 50  # Varsayılan sonuç sayısı
MAX_TOP_K = 100  # Maksimum sonuç sayısı

# Flask Ayarları
FLASK_PORT = 5000
FLASK_DEBUG = True
```

## 🔧 Performans İyileştirmeleri

### GPU Kullanımı

CUDA destekli GPU'nuz varsa:

```bash
# CUDA destekli PyTorch yükleyin
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Batch Size Optimizasyonu

GPU belleğinize göre `config.py` içinde `BATCH_SIZE` değerini artırın:
- 4GB VRAM: 16-32
- 8GB VRAM: 32-64
- 12GB+ VRAM: 64-128

### Daha Hızlı Model

Daha küçük ama hızlı model için `config.py` içinde:

```python
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
EMBEDDING_DIM = 512
```

## 🐛 Sorun Giderme

### "No images found" Hatası

- Fotoğrafların `data/airplane_photos/` klasöründe olduğundan emin olun
- Dosya uzantılarının desteklenen formatlarda olduğunu kontrol edin

### "Failed to load vector database" Hatası

- Önce `python scripts/create_embeddings.py` komutunu çalıştırın
- `data/embeddings/` klasörünün oluşturulduğunu kontrol edin

### Yavaş Arama

- GPU kullanıyor musunuz kontrol edin: `python -c "import torch; print(torch.cuda.is_available())"`
- `config.py` içinde `BATCH_SIZE` değerini optimize edin

### Port Zaten Kullanımda

`config.py` içinde farklı bir port kullanın:

```python
FLASK_PORT = 5001
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🙏 Teşekkürler

- [OpenAI CLIP](https://github.com/openai/CLIP) - Görüntü-metin modeli
- [Hugging Face Transformers](https://huggingface.co/transformers/) - Model kütüphanesi
- [Faiss](https://github.com/facebookresearch/faiss) - Vektör benzerlik araması
- [Flask](https://flask.palletsprojects.com/) - Web framework

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

<div align="center">

### 🚀 Powered by

**OpenAI CLIP** • **Facebook Faiss** • **Hugging Face Transformers**

Geliştirici: **Talha Kenan** | 2025

[![GitHub](https://img.shields.io/badge/GitHub-talhakenan1-181717?style=flat&logo=github)](https://github.com/talhakenan1)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!

</div>
