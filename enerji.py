import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date, timedelta
from PIL import Image

from dotenv import load_dotenv
import smtplib
import os
from email.mime.text import MIMEText
import streamlit as st


load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(message):
    from email.mime.multipart import MIMEMultipart  # eksikse eklenmeli
    msg = MIMEMultipart()
    msg["Subject"] = "Yeni Geri Bildirim"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"Mail gönderme başarısız: {e}")



# Sayfa yapılandırması
st.set_page_config(page_title="Güneş Paneli Hesaplama", layout="wide")

# Panel türleri
panel_verimlilik_dict = {
    "Monokristalin": 0.22, 
    "Polikristalin": 0.18, 
    "İnce Film": 0.14,
    "Hibrid": 0.25,  # Yeni panel tipi
    "CIGS": 0.17  # Yeni panel tipi
}
panel_fiyat_dict = {
    "Monokristalin": 2000, 
    "Polikristalin": 1500, 
    "İnce Film": 1000,
    "Hibrid": 2200,  # Yeni panel tipi fiyatı
    "CIGS": 1800  # Yeni panel tipi fiyatı
}  # m² başı fiyat (TL)

# Türkiye illeri listesi
turkiye_iller = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın",
    "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa",
    "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum",
    "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir",
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa",
    "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
]

# Fonksiyon: Şehir isminden koordinat al
def sehir_to_koordinat(sehir):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={sehir},Turkey"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers).json()
    if response:
        lat = float(response[0]["lat"])
        lon = float(response[0]["lon"])
        return lat, lon
    return None, None

# Fonksiyon: Open-Meteo API ile güneşlenme süresi (saat cinsinden)
def guneslenme_verisi_getir(lat, lon):
    today = date.today()
    end = today + timedelta(days=6)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=sunshine_duration"
        f"&timezone=auto&start_date={today}&end_date={end}"
    )
    response = requests.get(url).json()
    if "daily" in response:
        durations = response["daily"]["sunshine_duration"]
        saat_listesi = [d / 3600 for d in durations]
        ortalama_saat = sum(saat_listesi) / len(saat_listesi)
        return round(ortalama_saat * 365, 0)  # yıllık güneşlenme süresi
    return 0

# Hesaplama fonksiyonları
def enerji_hesapla(alan, verimlilik, panel_tipi):
    verim = panel_verimlilik_dict.get(panel_tipi, 0.18)
    return alan * 1000 * verim * (verimlilik / 100)

def karbon_hesapla(enerji): return enerji * 0.4
def maliyet_hesapla(alan, panel_tipi): return alan * panel_fiyat_dict[panel_tipi]
def tasarruf_hesapla(yillik_enerji): return yillik_enerji * 1.5


# Güneş logosu ve başlık yan yana
col_logo, col_title = st.columns([0.1, 0.9])
with col_logo:
    gunes_logo = Image.open('sun_logo.png')  
    st.image(gunes_logo, width=60)
with col_title:
    st.title("Güneş Paneli Enerji ve Tasarruf Hesaplayıcı")

# Giriş Alanı
col1, col2, col3 = st.columns(3)
with col1:
    sehir = st.selectbox("Şehir Seçiniz", turkiye_iller)
with col2:
    panel_tipi = st.selectbox("Panel Tipi", list(panel_verimlilik_dict.keys()))
with col3:
    alan = st.number_input("Panel Alanı (m²)", min_value=1, max_value=1000, value=20)

verimlilik = st.slider("Panel Verimliliği (%)", 10, 100, 50)

# API Entegrasyonu
lat, lon = sehir_to_koordinat(sehir)
if lat and lon:
    guneslenme = guneslenme_verisi_getir(lat, lon)
else:
    st.error("Şehir bulunamadı veya koordinat alınamadı.")
    st.stop()

# Hesaplamalar
günlük_enerji = enerji_hesapla(alan, verimlilik, panel_tipi)
yillik_enerji = günlük_enerji * guneslenme
karbon = karbon_hesapla(yillik_enerji)
maliyet = maliyet_hesapla(alan, panel_tipi)
tasarruf = tasarruf_hesapla(yillik_enerji)


# Sonuç Kartları
st.markdown("## 📈 Hesap Sonuçları")
col1, col2, col3 = st.columns(3)
col1.metric("Günlük Enerji (kWh)", f"{günlük_enerji:.2f}")
col2.metric("Yıllık Enerji (kWh)", f"{yillik_enerji:,.0f}")
col3.metric("Yıllık Karbon Engelleme (kg)", f"{karbon:,.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("Toplam Panel Maliyeti (TL)", f"{maliyet:,.0f}")
col5.metric("Yıllık Tasarruf (TL)", f"{tasarruf:,.0f}")


# 🔋 Batarya Hesabı - 1 günlük üretimi depolayacak kapasite
batarya_kapasitesi = günlük_enerji * 1000  # Wh cinsinden

st.markdown("## 🔋 Enerji Depolama Sistemi")
st.write(f"📦 Önerilen Batarya Kapasitesi (1 günlük enerji için): **{batarya_kapasitesi:,.0f} Wh**")

# Depolama değerlendirmesi
if batarya_kapasitesi < 5000:
    st.info("Bu kapasite küçük sistemler için yeterlidir.")
elif batarya_kapasitesi < 10000:
    st.info("Orta büyüklükte bir ev için uygundur.")
else:
    st.info("Yüksek enerji ihtiyacı olan sistemlerde kullanılabilir.") 


# --- Batarya Depolama Sistemi Hesaplama ---
st.markdown("---")
st.subheader("🔋 Batarya Depolama Hesabı")

st.markdown(""" 
Sisteminizin güneşsiz günlerde de çalışması için yeterli batarya kapasitesi hesaplanır.
Bu hesaplama, panellerin günlük ortalama enerji üretimine göre yapılır.
""")

# Kullanıcının kaç günlük enerji depolamak istediğini seçmesi
yedek_gun = st.slider("Kaç Günlük Enerji Yedeklenmeli?", 1, 10, 1)

# Depolanabilir enerji günlük üretime eşit
depolanabilir_enerji = günlük_enerji  # kWh
batarya_kapasitesi_wh = depolanabilir_enerji * 1000 * yedek_gun  # Wh

# Sonuçları göster
col_b1, col_b2 = st.columns(2)
col_b1.metric("Depolanabilir Enerji (kWh/gün)", f"{depolanabilir_enerji:.2f}")
col_b2.metric(f"Gerekli Batarya Kapasitesi ({yedek_gun} gün)", f"{batarya_kapasitesi_wh:,.0f} Wh")


# Farklı Lokasyon Karşılaştırması
st.markdown("---")
st.subheader("🌍 Farklı Lokasyon Karşılaştırması")

sehir2 = st.selectbox("Karşılaştırmak için ikinci şehir", turkiye_iller)

if sehir2:
    lat2, lon2 = sehir_to_koordinat(sehir2)
    if lat2 and lon2:
        guneslenme2 = guneslenme_verisi_getir(lat2, lon2)
        yillik_enerji2 = enerji_hesapla(alan, verimlilik, panel_tipi) * guneslenme2
        karbon2 = karbon_hesapla(yillik_enerji2)
        maliyet2 = maliyet_hesapla(alan, panel_tipi)
        tasarruf2 = tasarruf_hesapla(yillik_enerji2)

        st.markdown(f"### 📊 {sehir} ve {sehir2} Karşılaştırması")
        veri_karsilastirma = pd.DataFrame({
            "Kriter": ["Yıllık Güneşlenme (saat)", "Yıllık Enerji (kWh)", "Karbon (kg)", "Maliyet (TL)", "Tasarruf (TL)", ],
            sehir: [guneslenme, yillik_enerji, karbon, maliyet, tasarruf],
            sehir2: [guneslenme2, yillik_enerji2, karbon2, maliyet2, tasarruf2],
        })

        st.dataframe(veri_karsilastirma)


# Öneriler
def öneriler(sehir, panel_tipi, alan, guneslenme):
    öneri = []
    if guneslenme > 270 * 365 / 12:
        öneri.append(f"{sehir}, yüksek güneşlenme süresine sahip, panel verimi iyi değerlendirilmeli.")
    else:
        öneri.append(f"{sehir}, düşük güneşlenme süresine sahip, verimli panel seçimine dikkat edilmelidir.")

    if panel_tipi == "Monokristalin":
        öneri.append("Monokristalin paneller yüksek verimlidir, küçük alanlar için idealdir.")
    elif panel_tipi == "Polikristalin":
        öneri.append("Polikristalin paneller maliyet açısından daha uygundur.")
    elif panel_tipi == "İnce Film":
        öneri.append("İnce Film paneller büyük alanlarda tercih edilebilir.")
    elif panel_tipi == "Hibrid":
        öneri.append("Hibrid paneller, hem güneş hem de sıcaklık farklarından faydalanır, yüksek verimlilik sağlar.")
    else:
        öneri.append("CIGS paneller, düşük ışık koşullarında bile verimli çalışır.")

    if alan < 20:
        öneri.append("Alanınız küçük olduğu için yüksek verimli panel seçimi önerilir.")
    öneri.append("Panel bakımı ile verimliliği artırabilirsiniz. Temizlik ve düzenli kontrol önemlidir.")
    öneri.append("Enerji verimliliği için evde gereksiz ışıkları kapatmak ve enerji tasarruflu cihazlar kullanmak önemlidir.")

    return öneri

st.sidebar.title("🧠 Öneriler")
for o in öneriler(sehir, panel_tipi, alan, guneslenme):
    st.sidebar.write(f"✅ {o}")
    
# Geri Bildirim Alanı ve Renkli Gönder Butonu
st.text_area("Geri bildirimlerinizi bırakın", key="feedback")

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #28a745;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

feedback = st.session_state.get("feedback", "")

if st.button("📨 Gönder", use_container_width=True):
    if feedback.strip() == "":
        st.warning("Lütfen geri bildirim girin.")
    else:
        try:
            send_email(feedback)
            st.success("Teşekkür ederiz! Geri bildiriminiz kaydedildi.")
        except Exception as e:
            st.error(f"Mail gönderilirken hata oluştu: {e}")

