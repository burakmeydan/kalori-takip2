import streamlit as st
import pandas as pd
from datetime import date

# Uygulama Başlığı
st.set_page_config(page_title="Kalori Takipçisi", page_icon="🍎")
st.title("🍎 Günlük Kalori Takipçisi")

# Yan Panel: Kullanıcı Bilgileri ve Hedef
with st.sidebar:
    st.header("Profil ve Hedef")
    hedef_kalori = st.number_input("Günlük Kalori Hedefiniz:", value=2000, step=50)
    st.info(f"Hedeflenen: {hedef_kalori} kcal")

# Veri depolama (Session State kullanarak)
if 'meals' not in st.session_state:
    st.session_state.meals = []

# Yeni Öğün Ekleme Alanı
st.subheader("🍽️ Yeni Öğün Ekle")
col1, col2 = st.columns([3, 1])

with col1:
    food_name = st.text_input("Yiyecek Adı", placeholder="Örn: Tavuklu Salata")
with col2:
    calories = st.number_input("Kalori", min_value=0, step=10)

if st.button("Listeye Ekle"):
    if food_name:
        st.session_state.meals.append({"Öğün": food_name, "Kalori": calories, "Tarih": date.today()})
        st.success(f"{food_name} eklendi!")
    else:
        st.warning("Lütfen yiyecek adını girin.")

# Özet ve Grafikler
if st.session_state.meals:
    df = pd.DataFrame(st.session_state.meals)
    toplam_tuketilen = df["Kalori"].sum()
    kalan_kalori = hedef_kalori - toplam_tuketilen

    # Göstergeler (Metrics)
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Hedef", f"{hedef_kalori} kcal")
    m2.metric("Tüketilen", f"{toplam_tuketilen} kcal")
    m3.metric("Kalan", f"{kalan_kalori} kcal", delta_color="inverse")

    # İlerleme Çubuğu
    oran = min(toplam_tuketilen / hedef_kalori, 1.0)
    st.progress(oran)

    # Bugünün Listesi
    st.subheader("📝 Bugün Ne Yedin?")
    st.table(df)

    # Verileri Temizle
    if st.button("Listeyi Temizle"):
        st.session_state.meals = []
        st.rerun()
else:
    st.info("Henüz bir şey eklemedin. Hadi başlayalım!")