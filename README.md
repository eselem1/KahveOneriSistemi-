## Kahve Öneri Sistemi ##

Bu proje, kullanıcı tercihlerini analiz ederek uygun kahve önerileri sunan makine öğrenmesi tabanlı bir sistemdir.

## Özellikler ##
- Kullanıcının seçimlerine göre kahve önerisi
- Python ile geliştirilmiş GUI arayüz (`app.gui.py`)
- Eğitimli model dosyası ile hızlı tahminleme (`model_egit_v2.py`)
- Kapsamlı kahve veri seti (`coffee_recommendation_dataset_v7_logic_filtered.csv`)
- Model eğitimi için ayrı Python dosyası (`kahve_oner_v2.py`)

## Gereksinimler ##

Projenin çalışabilmesi için aşağıdaki Python paketlerinin yüklü olması gerekir:

```bash
pip install pandas scikit-learn joblib PySide6
