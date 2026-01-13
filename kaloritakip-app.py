import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os

# Sayfa yapılandırması
st.set_page_config(page_title="Kalori Takip", page_icon="🍎", layout="wide")

# Veri dosyası
DATA_FILE = "calorie_data.json"

# Yiyecek veritabanı (100g başına: [kalori, protein%, karb%, yağ%])
FOOD_DB = {
    'tavuk': [165, 31, 0, 3.6],
    'tavuk ızgara': [165, 31, 0, 3.6],
    'kızarmış tavuk': [220, 26, 0, 12],
    'fasulye': [88, 7, 16, 0.3],
    'mercimek': [116, 9, 20, 0.4],
    'pirinç': [130, 2.7, 28, 0.3],
    'makarna': [371, 12, 75, 1.1],
    'ekmek': [265, 9, 49, 3.3],
    'tam buğday ekmek': [246, 13, 41, 3.7],
    'muz': [89, 1.1, 23, 0.3],
    'elma': [52, 0.26, 14, 0.17],
    'portakal': [47, 0.9, 12, 0.12],
    'yumurta': [155, 13, 1.1, 11],
    'beyaz peynir': [112, 18, 3.5, 4],
    'süt': [61, 3.2, 4.8, 3.3],
    'yoğurt': [59, 3.5, 3.3, 0.4],
    'balık': [82, 18, 0, 0.7],
    'somon': [208, 20, 0, 13],
    'et': [250, 26, 0, 15],
    'patates': [77, 2, 17, 0.1],
    'brokoli': [34, 2.8, 7, 0.4],
    'domates': [18, 0.9, 3.9, 0.2],
    'havuç': [41, 0.9, 10, 0.2],
    'zeytinyağı': [884, 0, 0, 100],
    'çorba': [50, 2, 8, 1],
    'pizza': [266, 12, 36, 10],
    'hamburger': [295, 17, 24, 14]
}

# Session state başlatma
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 2000
if 'meals' not in st.session_state:
    st.session_state.meals = {
        'Kahvaltı': [],
        'Öğle Yemeği': [],
        'Akşam Yemeği': [],
        'Ara Öğün': []
    }

# Veri yükleme/kaydetme fonksiyonları
def load_data():
    """Geçmiş verileri yükle"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_daily_data():
    """Günlük verileri kaydet"""
    history = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    total_calories = sum(food['calories'] for meal in st.session_state.meals.values() for food in meal)
    
    if total_calories > 0:
        # Bugünün kaydını güncelle veya ekle
        entry = {
            'date': today,
            'calories': total_calories,
            'goal': st.session_state.daily_goal,
            'deficit': st.session_state.daily_goal - total_calories
        }
        
        # Aynı tarihli kayıt varsa güncelle
        history = [h for h in history if h['date'] != today]
        history.append(entry)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

def calculate_macros(food_name, amount, unit):
    """Yiyecek için makro besin değerlerini hesapla"""
    food_key = food_name.lower().strip()
    food_data = None
    
    # Veritabanında ara
    if food_key in FOOD_DB:
        food_data = FOOD_DB[food_key]
    else:
        # Kısmi eşleşme
        for key in FOOD_DB:
            if key in food_key or food_key in key:
                food_data = FOOD_DB[key]
                break
    
    if not food_data:
        # Varsayılan değerler
        food_data = [100, 10, 50, 30]
    
    # Gram cinsine çevir
    grams = float(amount)
    if unit == 'kg':
        grams *= 1000
    elif unit == 'porsiyon':
        grams *= 150
    elif unit == 'adet':
        if 'yumurta' in food_key:
            grams = 50
        elif 'muz' in food_key:
            grams = 120
        elif any(word in food_key for word in ['elma', 'portakal']):
            grams = 150
        else:
            grams = 100
    
    calories, protein_p, carbs_p, fat_p = food_data
    total_cal = (grams / 100) * calories
    protein_cal = total_cal * (protein_p / 100)
    carbs_cal = total_cal * (carbs_p / 100)
    fat_cal = total_cal * (fat_p / 100)
    
    return {
        'name': food_name,
        'amount': amount,
        'unit': unit,
        'calories': round(total_cal),
        'protein': round(protein_cal),
        'carbs': round(carbs_cal),
        'fat': round(fat_cal),
        'protein_p': protein_p,
        'carbs_p': carbs_p,
        'fat_p': fat_p
    }

def calculate_period_stats():
    """Haftalık ve aylık istatistikleri hesapla"""
    history = load_data()
    if not history:
        return None
    
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    week_data = [h for h in history if datetime.strptime(h['date'], '%Y-%m-%d') >= week_ago]
    month_data = [h for h in history if datetime.strptime(h['date'], '%Y-%m-%d') >= month_ago]
    
    return {
        'week_deficit': sum(h['deficit'] for h in week_data),
        'week_days': len(week_data),
        'month_deficit': sum(h['deficit'] for h in month_data),
        'month_days': len(month_data)
    }

# Ana başlık
st.title("🍎 Günlük Kalori & Makro Takibi")

# Sidebar - Ayarlar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    new_goal = st.number_input("Günlük Kalori Hedefi", min_value=500, max_value=5000, 
                                value=st.session_state.daily_goal, step=50)
    if new_goal != st.session_state.daily_goal:
        st.session_state.daily_goal = new_goal
        st.rerun()
    
    st.divider()
    
    if st.button("📊 Verileri Kaydet"):
        save_daily_data()
        st.success("Veriler kaydedildi!")
    
    if st.button("🗑️ Bugünü Sıfırla"):
        st.session_state.meals = {
            'Kahvaltı': [],
            'Öğle Yemeği': [],
            'Akşam Yemeği': [],
            'Ara Öğün': []
        }
        st.rerun()

# Günlük özet hesaplama
all_foods = [food for meal in st.session_state.meals.values() for food in meal]
total_calories = sum(f['calories'] for f in all_foods)
total_protein = sum(f['protein'] for f in all_foods)
total_carbs = sum(f['carbs'] for f in all_foods)
total_fat = sum(f['fat'] for f in all_foods)
remaining = st.session_state.daily_goal - total_calories

# Günlük Özet Kartları
st.header("📈 Günlük Özet")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Kalori", f"{total_calories} kcal", f"Hedef: {st.session_state.daily_goal}")
with col2:
    protein_pct = (total_protein / total_calories * 100) if total_calories > 0 else 0
    st.metric("Protein", f"{total_protein} kcal", f"{protein_pct:.1f}%")
with col3:
    carbs_pct = (total_carbs / total_calories * 100) if total_calories > 0 else 0
    st.metric("Karbonhidrat", f"{total_carbs} kcal", f"{carbs_pct:.1f}%")
with col4:
    fat_pct = (total_fat / total_calories * 100) if total_calories > 0 else 0
    st.metric("Yağ", f"{total_fat} kcal", f"{fat_pct:.1f}%")

# İlerleme çubuğu
percentage = (total_calories / st.session_state.daily_goal * 100) if st.session_state.daily_goal > 0 else 0
st.progress(min(percentage / 100, 1.0))
st.caption(f"Kalan: **{remaining} kcal** ({percentage:.1f}% tamamlandı)")

# Haftalık/Aylık İstatistikler
stats = calculate_period_stats()
if stats and stats['week_days'] > 0:
    st.divider()
    st.subheader("📊 Kalori Açığı İstatistikleri")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Son 7 Gün**
        - Toplam: **{stats['week_deficit']:+d} kcal**
        - Gün sayısı: {stats['week_days']}
        - Ortalama: {stats['week_deficit'] / stats['week_days']:.0f} kcal/gün
        """)
    
    with col2:
        st.info(f"""
        **Son 30 Gün**
        - Toplam: **{stats['month_deficit']:+d} kcal**
        - Gün sayısı: {stats['month_days']}
        - Ortalama: {stats['month_deficit'] / stats['month_days']:.0f} kcal/gün
        """)

st.divider()

# Yiyecek Ekleme
st.subheader("➕ Yiyecek Ekle")
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    meal_type = st.selectbox("Öğün", ['Kahvaltı', 'Öğle Yemeği', 'Akşam Yemeği', 'Ara Öğün'])
with col2:
    food_name = st.text_input("Yiyecek Adı", placeholder="örn: tavuk")
with col3:
    amount = st.number_input("Miktar", min_value=0.0, value=100.0, step=10.0)
with col4:
    unit = st.selectbox("Birim", ['g', 'kg', 'adet', 'porsiyon'])

if st.button("Ekle", type="primary", use_container_width=True):
    if food_name and amount > 0:
        food_data = calculate_macros(food_name, amount, unit)
        st.session_state.meals[meal_type].append(food_data)
        save_daily_data()
        st.rerun()
    else:
        st.error("Lütfen yiyecek adı ve miktarını girin!")

st.divider()

# Öğünleri Göster
for meal_name, foods in st.session_state.meals.items():
    if foods:
        st.subheader(f"🍽️ {meal_name}")
        
        meal_cal = sum(f['calories'] for f in foods)
        meal_protein = sum(f['protein'] for f in foods)
        meal_carbs = sum(f['carbs'] for f in foods)
        meal_fat = sum(f['fat'] for f in foods)
        
        # Makro bar grafiği
        if meal_cal > 0:
            fig = go.Figure(data=[
                go.Bar(name='Protein', x=[meal_protein], y=[''], orientation='h', 
                       marker_color='#ef4444'),
                go.Bar(name='Karbonhidrat', x=[meal_carbs], y=[''], orientation='h', 
                       marker_color='#3b82f6'),
                go.Bar(name='Yağ', x=[meal_fat], y=[''], orientation='h', 
                       marker_color='#eab308')
            ])
            fig.update_layout(
                barmode='stack',
                height=100,
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Yiyecekleri listele
        for idx, food in enumerate(foods):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{food['name']}** ({food['amount']}{food['unit']})")
            with col2:
                st.write(f"{food['calories']} kcal • P:{food['protein_p']:.0f}% K:{food['carbs_p']:.0f}% Y:{food['fat_p']:.0f}%")
            with col3:
                if st.button("🗑️", key=f"del_{meal_name}_{idx}"):
                    st.session_state.meals[meal_name].pop(idx)
                    save_daily_data()
                    st.rerun()
        
        st.caption(f"**Öğün Toplamı:** {meal_cal} kcal")
        st.divider()

# Geçmiş veriler
if st.checkbox("📅 Geçmiş Kayıtları Göster"):
    history = load_data()
    if history:
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        st.subheader("Günlük Geçmiş")
        for _, row in df.head(15).iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(row['date'].strftime('%d %B %Y'))
            with col2:
                st.write(f"{row['calories']} / {row['goal']} kcal")
            with col3:
                deficit_color = "🟢" if row['deficit'] > 0 else "🔴"
                st.write(f"{deficit_color} {row['deficit']:+d}")
    else:
        st.info("Henüz kayıt yok")

# Footer
st.divider()
st.caption("💡 **Renk Açıklaması:** 🔴 Protein | 🔵 Karbonhidrat | 🟡 Yağ")
