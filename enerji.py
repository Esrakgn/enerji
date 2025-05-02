import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# Sayfa yapılandırması
st.set_page_config(page_title="Güneş Paneli Hesaplama", layout="wide")

# Türkiye'nin 81 ili ve güneşlenme süreleri
iller_guneslenme = {
    "Adana": 284, "Adıyaman": 276, "Afyonkarahisar": 253, "Ağrı": 220, "Amasya": 228, "Ankara": 252,
    "Antalya": 300, "Artvin": 196, "Aydın": 276, "Balıkesir": 237, "Bilecik": 229, "Bingöl": 211,
    "Bitlis": 210, "Bolu": 226, "Burdur": 276, "Bursa": 240, "Çanakkale": 241, "Çankırı": 235, "Çorum": 236,
    "Denizli": 274, "Diyarbakır": 283, "Edirne": 235, "Elazığ": 257, "Erzincan": 249, "Erzurum": 219,
    "Eskişehir": 241, "Gaziantep": 287, "Giresun": 207, "Gümüşhane": 210, "Hakkari": 188, "Hatay": 284,
    "Iğdır": 260, "Isparta": 255, "İstanbul": 219, "İzmir": 275, "Kars": 233, "Kastamonu": 214, "Kayseri": 270,
    "Kırklareli": 222, "Kırşehir": 252, "Kocaeli": 226, "Konya": 276, "Kütahya": 238, "Malatya": 268, "Manisa": 270,
    "Mardin": 290, "Mersin": 294, "Muğla": 290, "Muş": 215, "Nevşehir": 250, "Niğde": 257, "Ordu": 206, "Osmaniye": 277,
    "Rize": 185, "Sakarya": 225, "Samsun": 212, "Siirt": 271, "Sinop": 215, "Sivas": 248, "Şanlıurfa": 300, "Şırnak": 234,
    "Tekirdağ": 224, "Tokat": 229, "Trabzon": 196, "Tunceli": 232, "Uşak": 242, "Van": 235, "Yalova": 216,
    "Yozgat": 235, "Zonguldak": 213
}

# Panel türleri
panel_verimlilik_dict = {"Monokristalin": 0.22, "Polikristalin": 0.18, "İnce Film": 0.14}
panel_fiyat_dict = {"Monokristalin": 2000, "Polikristalin": 1500, "İnce Film": 1000}  # m² başı fiyat (TL)

# Hesaplama fonksiyonları
def enerji_hesapla(alan, verimlilik, panel_tipi):
    verim = panel_verimlilik_dict.get(panel_tipi, 0.18)
    return alan * 1000 * verim * (verimlilik / 100)

def karbon_hesapla(enerji): return enerji * 0.4
def maliyet_hesapla(alan, panel_tipi): return alan * panel_fiyat_dict[panel_tipi]
def tasarruf_hesapla(yillik_enerji): return yillik_enerji * 1.5  # 1 kWh = 1.5 TL
def geri_donus(maliyet, tasarruf): return maliyet / tasarruf if tasarruf > 0 else 0

# Başlık
st.title("🔆 Güneş Paneli Enerji, Tasarruf ve Karbon Hesaplayıcı")

# Giriş Alanı
col1, col2, col3 = st.columns(3)
with col1:
    sehir = st.selectbox("Şehir Seçin", list(iller_guneslenme.keys()))
with col2:
    panel_tipi = st.selectbox("Panel Tipi", list(panel_verimlilik_dict.keys()))
with col3:
    alan = st.number_input("Panel Alanı (m²)", min_value=1, max_value=1000, value=20)

verimlilik = st.slider("Panel Verimliliği (%)", 10, 100, 50)

# Hesaplamalar
guneslenme = iller_guneslenme[sehir]
günlük_enerji = enerji_hesapla(alan, verimlilik, panel_tipi)
yillik_enerji = günlük_enerji * guneslenme
karbon = karbon_hesapla(yillik_enerji)
maliyet = maliyet_hesapla(alan, panel_tipi)
tasarruf = tasarruf_hesapla(yillik_enerji)
geri_donus_suresi = geri_donus(maliyet, tasarruf)

# Sonuç Kartları
st.markdown("## 📈 Hesap Sonuçları")
col1, col2, col3 = st.columns(3)
col1.metric("Günlük Enerji (kWh)", f"{günlük_enerji:.2f}")
col2.metric("Yıllık Enerji (kWh)", f"{yillik_enerji:.0f}")
col3.metric("Yıllık Karbon Engelleme (kg)", f"{karbon:.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("Toplam Panel Maliyeti (TL)", f"{maliyet:,.0f}")
col5.metric("Yıllık Tasarruf (TL)", f"{tasarruf:,.0f}")
col6.metric("Geri Dönüş Süresi (yıl)", f"{geri_donus_suresi:.1f}")

# Grafikler
st.markdown("---")
st.subheader("💡 Panel Türlerine Göre Verimlilik")
veri_df = pd.DataFrame({
    "Panel Tipi": list(panel_verimlilik_dict.keys()),
    "Verimlilik": list(panel_verimlilik_dict.values())
})
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(data=veri_df, x="Panel Tipi", y="Verimlilik", palette="coolwarm", ax=ax)
ax.set_ylabel("Verimlilik Oranı")
st.pyplot(fig)

# Öneriler
def öneriler(sehir, panel_tipi, alan):
    öneri = []
    if panel_tipi == "Monokristalin":
        öneri.append("Monokristalin paneller yüksek verimlidir, küçük alanlar için idealdir.")
    elif panel_tipi == "Polikristalin":
        öneri.append("Polikristalin paneller maliyet açısından daha uygundur.")
    else:
        öneri.append("İnce Film paneller büyük alanlarda tercih edilebilir.")
    
    if alan < 20:
        öneri.append("Alanınız küçük olduğu için yüksek verimli panel seçimi önerilir.")
    if iller_guneslenme[sehir] > 270:
        öneri.append(f"{sehir}, yüksek güneşlenme süresine sahip, panel verimi iyi değerlendirilmeli.")
    return öneri

st.sidebar.title("🧠 Öneriler")
for o in öneriler(sehir, panel_tipi, alan):
    st.sidebar.write(f"✅ {o}")

