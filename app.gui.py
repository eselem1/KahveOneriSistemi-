# app_gui.py  (Rev-4) — bej & sütlü kahve tema, veri kümesiyle tam uyum
from pathlib import Path
import sys, json, joblib
import numpy as np
from itertools import chain

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QVBoxLayout,
    QPushButton, QListWidget, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# -------------------------------------------------
# 0) Tema renkleri  – istediğiniz HEX’e göre ayarlayın
# -------------------------------------------------
BG_COLOR   = "#f5f5dc"   # bej
FG_COLOR   = "#7b5840"   # sütlü kahve
CTRL_COLOR = "#ece6d9"
BORDER_CLR = "#ae9c88"

# -------------------------------------------------
# 1) Model + kural motoru
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "coffee_recommendation_model_v2.joblib"
DATA_PATH  = ROOT / "coffee_recommendation_dataset_v7_logic_fixed.json"

def _load_rules():
    with open(DATA_PATH, encoding="utf-8") as f:
        rows = json.load(f)
    return {tuple(r[k] for k in (
            "sweetness","bitterness","milk","milk_type",
            "caffeine","temperature","size","flavor"
        )): r["recommendation"] for r in rows}

_rules = _load_rules()

try:
    _model = joblib.load(MODEL_PATH)
    print("[Bilgi] Makine-öğrenmesi modeli yüklendi.")
except Exception as e:
    _model = None
    print("[Uyarı] Model yüklenemedi, kural tabanına geçilecek:", e)

def safe_predict(row):
    """Model + geri dönüş yolu."""
    if _model:
        try:
            out = _model.predict([row])
            out = list(chain.from_iterable([out]))
            return out
        except Exception as e:
            print("[Model Hatası]", e)

    return _rules.get(tuple(row), ["Uygun kahve bulunamadı"])

# -------------------------------------------------
class CoffeeApp(QWidget):
    # Veri kümesindeki birebir değerler
    FEATURES = {
        "Tatlılık":  ["şekersiz", "az şekerli", "şekerli"],
        "Acılık":    ["acı", "orta", "yumuşak"],
        "Süt":       ["sütsüz", "sütlü"],
        # İlk seçenek: (boş) = veri kümesindeki "" değeri
        "Süt tipi":  ["", "normal süt", "laktozsuz süt", "bitkisel süt"],
        "Kafein":    ["kafeinli", "kafeinsiz"],
        "Sıcaklık":  ["sıcak", "soğuk"],
        "Boyut":     ["küçük", "orta", "büyük"],
        "Aroma":     ["doğal", "çikolatalı", "fındıklı", "karamelli", "vanilyalı"]
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kahve Öneri Sistemi")
        self.setFixedSize(390, 780)        # 6.6″ telefon
        self.setFont(QFont("Arial", 11))
        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 16)

        self.inputs = {}
        for label, options in self.FEATURES.items():
            lab   = QLabel(label)
            combo = QComboBox()
            combo.addItems(options)
            combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            combo.setMinimumContentsLength(max(len(o) for o in options))
            combo.view().setMinimumWidth(220)
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            lay = QVBoxLayout()
            lay.addWidget(lab)
            lay.addWidget(combo)
            root.addLayout(lay)
            self.inputs[label] = combo

        # Süt = sütsüz ⇒ süt tipi "" (ilk seçenek) ve pasif
        self.inputs["Süt"].currentIndexChanged.connect(self._toggle_milk_type)
        self._toggle_milk_type()

        btn = QPushButton("☕  Önerileri Göster")
        btn.clicked.connect(self.recommend)
        root.addWidget(btn)

        self.list_widget = QListWidget()
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.list_widget)

        # ---- Stil ----
        self.setStyleSheet(f"""
            QWidget        {{ background:{BG_COLOR}; color:{FG_COLOR}; }}
            QLabel         {{ font-weight:bold; }}
            QComboBox,
            QPushButton    {{ background:{CTRL_COLOR}; color:{FG_COLOR};
                               border:1px solid {BORDER_CLR}; border-radius:6px; padding:4px; }}
            QListWidget    {{ background:{CTRL_COLOR}; color:{FG_COLOR}; border-radius:6px; }}
        """)

    # ---------- Yardımcılar ----------
    def _toggle_milk_type(self):
        milk  = self.inputs["Süt"].currentText()
        combo = self.inputs["Süt tipi"]
        disabled = (milk == "sütsüz")
        combo.setEnabled(not disabled)
        if disabled:
            combo.setCurrentIndex(0)   # "" değeri

    # ---------- İşlem ----------
    def recommend(self):
        row = [c.currentText() for c in self.inputs.values()]
        recs = safe_predict(row)

        self.list_widget.clear()
        for r in recs:
            self.list_widget.addItem(f"• {r}")

        if recs == ["Uygun kahve bulunamadı"]:
            QMessageBox.information(self, "Sonuç Yok",
                                     "Seçilen kriterlere uygun kahve bulunamadı.")

# -------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = CoffeeApp()
    wnd.show()
    sys.exit(app.exec())
