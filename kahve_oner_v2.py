# kahve_oner_simple.py
import joblib
import pandas as pd
import numpy as np
import unicodedata
import re

# ----------------- Yardımcı listeler -----------------
COLD_WORDS  = ("iced", "cold", "nitro", "frapp")
MILKY_WORDS = ("latte", "cappuccino", "mocha", "flat white",
               "macchiato", "breve", "au lait", "white coffee")
DECAF_WORDS = ("decaf", "decaffeinated")

# ----------------- Yardımcı fonksiyonlar -----------------
def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))

def is_cold(name):   return any(w in name.lower() for w in COLD_WORDS)
def is_milky(name):  return any(w in name.lower() for w in MILKY_WORDS)
def is_decaf(name):  return any(w in name.lower() for w in DECAF_WORDS)

def matches(name, temp, milk, caf):
    # 1) sıcak / soğuk
    if   temp == "sıcak" and is_cold(name):  return False
    elif temp == "soğuk" and not is_cold(name): return False
    # 2) süt
    if   milk == "sütlü"  and not is_milky(name): return False
    elif milk == "sütsüz" and is_milky(name):     return False
    # 3) kafein
    if   caf == "kafeinli"  and is_decaf(name):   return False
    elif caf == "kafeinsiz" and not is_decaf(name): return False
    return True

# ----------------- Model -----------------
model = joblib.load("coffee_recommendation_model_v2.joblib")

# ----------------- Kullanıcı girdileri -----------------
print("\nKahve tercihini belirt lütfen:\n")

def ask(prompt):
    return input(prompt).strip().lower()

sweet  = ask("Tatlılık (şekerli / az şekerli / şekersiz): ")
bitter = ask("Acılık (acı / orta / yumuşak): ")
milk   = ask("Süt (sütlü / sütsüz): ")

milk_type = ""
if milk == "sütlü":
    milk_type = ask("Süt tipi (laktozsuz süt / bitkisel süt / normal süt): ")

caf   = ask("Kafein (kafeinli / kafeinsiz): ")
temp  = ask("Sıcaklık (sıcak / soğuk): ")
size  = ask("Boyut (küçük / orta / büyük): ")
flav  = ask("Aroma (çikolatalı / fındıklı / karamelli / vanilyalı / doğal): ")

# Yazım hatası düzeltme (örn. ıcak ➜ sıcak)
temp_norm = strip_accents(temp)
if temp_norm.startswith("sic"): temp = "sıcak"
elif temp_norm.startswith("soc") or temp_norm.startswith("sog"): temp = "soğuk"

# ----------------- Tek satır DataFrame -----------------
X_new = pd.DataFrame([{
    "sweetness": sweet, "bitterness": bitter, "milk": milk, "milk_type": milk_type,
    "caffeine": caf, "temperature": temp, "size": size, "flavor": flav
}])

probas  = model.predict_proba(X_new)[0]
classes = model.classes_
ranked  = np.argsort(probas)[::-1]          # en yüksek olasılıktan başla

suggestion = next(
    (classes[i] for i in ranked
     if matches(classes[i], temp, milk, caf)),
    None
)

print("\n🎯 Sana en uygun kahve:")
if suggestion:
    print("•", suggestion)
else:
    print("Maalesef tam koşullara uyan kahve bulunamadı. "
          "Kısıtları gevşetip yeniden deneyebilirsin.")
