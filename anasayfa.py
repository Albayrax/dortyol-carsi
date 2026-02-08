import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v50 Stable",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# API Anahtarı Kontrolü
apiKey = st.secrets.get("gemini_api_key", "")

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error("Veritabanı bağlantısı kurulamadı. Lütfen Secrets ayarlarını kontrol edin.")

db = firestore.client() if firebase_admin._apps else None

# --- FIREBASE HELPERS (RULE 1) ---
def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- CSS: PROFESYONEL VE TEMİZ TASARIM ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Arka planı yumuşak bir gri/beyaz yaptık (Cırtlak renk bitti!) */
    .stApp {{ 
        background-color: #F8F9FA; 
        font-family: 'Inter', sans-serif; 
    }}

    /* Başlıklar ve Yazılar için Derin Lacivert */
    h1, h2, h3, h4, p, span, label, div {{ color: #001F3F !important; }}

    .main-title {{ 
        font-size: 3.5rem; 
        font-weight: 800; 
        text-align: center; 
        margin-top: -70px; 
        text-transform: uppercase; 
        letter-spacing: -2px;
        background: linear-gradient(90deg, #001F3F, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Radar Kartları */
    .radar-card {{ 
        background: white; 
        border-radius: 20px; 
        padding: 20px; 
        border-left: 8px solid #FF8C00; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }}

    /* Dükkan Kartları */
    .business-card {{ 
        background: white; 
        border-radius: 25px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid #E5E7EB; 
        transition: 0.3s; 
    }}
    .business-card:hover {{ 
        transform: translateY(-5px); 
        box-shadow: 0 20px 30px rgba(0,0,0,0.1); 
        border-color: #FF8C00;
    }}

    /* Butonlar - Turuncu Vurgu */
    .stButton>button {{ 
        background-color: #FF8C00 !important; 
        color: white !important; 
        border-radius: 12px !important; 
        font-weight: 700 !important; 
        border: none !important; 
        transition: 0.3s !important;
    }}
    .stButton>button:hover {{ background-color: #E67E00 !important; transform: scale(1.02); }}

    /* Tab Menüsü */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ 
        background-color: white; 
        border-radius: 10px; 
        padding: 10px 20px; 
        border: 1px solid #EEE;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (GİRİŞ EKRANI) ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("SİSTEME GİR"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Kod!")
    st.stop()

# --- VERİ ÇEKME VE RADAR MANTIĞI ---
def initialize_data():
    """Eğer veritabanı boşsa örnek veriler ekler (Radar çalışsın diye)"""
    col = get_col("dukkanlar")
    if len(list(col.limit(1).stream())) == 0:
        sample_shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "urunler": [{"ad": "Benzin 95", "fiyat": 60.50}]},
            {"ad": "Petrol Ofisi", "sektor": "Ulaşım", "sifre": "123", "urunler": [{"ad": "Benzin 95", "fiyat": 60.20}]},
            {"ad": "Dörtyol Ekmek Fırını", "sektor": "Hizmet", "sifre": "123", "urunler": [{"ad": "Ekmek", "fiyat": 10.00}]},
            {"ad": "Meydan Fırını", "sektor": "Hizmet", "sifre": "123", "urunler": [{"ad": "Ekmek", "fiyat": 9.50}]}
        ]
        for s in sample_shops: col.add(s)

if db: initialize_data()

all_shops = []
try:
    shops_docs = get_col("dukkanlar").stream()
    all_shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_docs]
except: pass

# --- HEADER ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# --- 🔥 REKABET RADARI ---
st.markdown("### 📊 REKABET RADARI")
r_col1, r_col2, r_col3 = st.columns(3)

fuel_prices = []
bread_prices = []
for s in all_shops:
    for u in s.get('urunler', []):
        name = u['ad'].lower()
        if "benzin" in name or "95" in name: fuel_prices.append({"dükkan": s['ad'], "fiyat": u['fiyat']})
        if "ekmek" in name: bread_prices.append({"dükkan": s['ad'], "fiyat": u['fiyat']})

with r_col1:
    if fuel_prices:
        cheapest = min(fuel_prices, key=lambda x: x['fiyat'])
        st.markdown(f'<div class="radar-card"><h4>⛽ EN UCUZ BENZİN</h4><p>{cheapest["dükkan"]}</p><h2 style="color:#FF8C00 !important;">{cheapest["fiyat"]} ₺</h2></div>', unsafe_allow_html=True)
    else: st.info("Benzin verisi bekleniyor...")

with r_col2:
    if bread_prices:
        cheapest = min(bread_prices, key=lambda x: x['fiyat'])
        st.markdown(f'<div class="radar-card"><h4>🍞 EN UCUZ EKMEK</h4><p>{cheapest["dükkan"]}</p><h2 style="color:#FF8C00 !important;">{cheapest["fiyat"]} ₺</h2></div>', unsafe_allow_html=True)
    else: st.info("Fırın verisi bekleniyor...")

with r_col3:
    st.markdown('<div class="radar-card"><h4>⭐ GÜNÜN ESNAFI</h4><p>Antik Kral Künefe</p><h2 style="color:#FF8C00 !important;">9.9 Puan</h2></div>', unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["💎 ÇARŞI", "🏥 KAMU REHBERİ", "📝 DÜKKAN AÇ", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# --- TAB 1: ÇARŞI ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ne aramıştınız? (Kebap, Lastik, Eczane...)", key="main_search")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Hizmet"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"cat_btn_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        for s in filtered:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 3])
            with c1: st.image(s.get('img', "https://images.unsplash.com/photo-1555066931-4365d14bab8c"), use_container_width=True)
            with c2:
                st.markdown(f"### {s.get('ad')}")
                st.write(s.get('icerik', 'Dörtyol esnafı.')[:100] + "...")
                if st.button(f"İncele: {s.get('ad')}", key=f"btn_sh_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DETAY SAYFASI
        shop_id = st.session_state.selected_shop_id
        s_data = next((s for s in all_shops if s['id'] == shop_id), None)
        if st.button("← Geri"): st.session_state.selected_shop_id = None; st.rerun()
        if s_data:
            st.image(s_data.get('img',''), use_container_width=True)
            st.title(s_data['ad'])
            for p in s_data.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:12px; border:1px solid #DDD; margin-bottom:8px; display:flex; justify-content:space-between;"><b>{p['ad']}</b><b style="color:#FF8C00;">{p['fiyat']} ₺</b></div>""", unsafe_allow_html=True)

# --- TAB 2: KAMU REHBERİ (AI) ---
with tabs[1]:
    st.subheader("🏥 Kamu ve Sağlık Bilgileri")
    if not apiKey:
        st.warning("⚠️ Yapay zeka henüz aktif değil. Lütfen admin panelinden API anahtarını ekleyin.")
    else:
        if st.button("🤖 YAPAY ZEKA LİSTESİNİ GÜNCELLE"):
            # call_gemini_ai logic...
            st.info("İnternet taranıyor...")

# --- TAB 5: ADMİN PANELİ (GİRİŞ DÜZELTİLDİ) ---
with tabs[4]:
    st.markdown("### 🔑 Yönetici Girişi")
    adm_pwd = st.text_input("Admin Şifresini Giriniz", type="password", key="admin_access")
    
    if adm_pwd == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı.")
        st.divider()
        st.write("### ⚙️ Sistem Ayarları")
        
        # API Key Girişi
        with st.expander("🔑 API Anahtarı ve Sistem Sırları"):
            st.write("Gemini API anahtarınızı buraya girmeyin; 'Secrets' ayarlarına 'gemini_api_key' olarak ekleyin.")
        
        st.divider()
        st.write("### 🏪 Mağaza Denetimi")
        for d in all_shops:
            with st.expander(f"{d.get('ad','Adsız')}"):
                st.write(f"Sektör: {d.get('sektor')}")
                st.write(f"Şifre: {d.get('sifre')}")
                if st.button(f"SİL: {d['ad']}", key=f"del_adm_{d['id']}"):
                    get_col("dukkanlar").document(d['id']).delete()
                    st.rerun()
    elif adm_pwd:
        st.error("Hatalı admin şifresi!")

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#999;'>© {GUNCEL_YIL} Albayrax v50 Stable | Dörtyol Rekabet Portalı</div>", unsafe_allow_html=True)
