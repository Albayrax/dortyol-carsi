import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests
import re

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v58 Visual Master",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = st.secrets.get("gemini_api_key", "")

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except: pass

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI ANALİZ VE GÖRSEL CSS ---
st.markdown("""
    <style>
    /* Mirror AI / Modern Renkli Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png'), linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-attachment: fixed;
    }
    
    /* Kartların Okunabilirliği İçin Glassmorphism Efekti */
    .standard-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.3);
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: 0.3s;
    }
    .standard-card:hover { transform: translateY(-5px); border-color: #FF8C00; }
    
    h1, h2, h3, h4, p, span, label, div { color: #001F3F !important; font-family: 'Inter', sans-serif; }
    .main-title { font-weight: 900; color: white !important; text-align: center; margin-top: -60px; font-size: 2.8rem; text-shadow: 3px 3px 10px rgba(0,0,0,0.5); }
    
    .badge-job { background: #001F3F; color: #FFB300 !important; padding: 5px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 800; }
    
    /* Görsel Kutuları */
    .img-box { width: 100%; height: 180px; border-radius: 15px; overflow: hidden; margin-bottom: 15px; border: 2px solid #001F3F; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; }
    
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; border: 2px solid #001F3F !important; background: white !important; color: #001F3F !important; }
    .stButton>button:hover { background: #001F3F !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA INITIALIZER (GÖRSEL VE İLAN DESTEKLİ) ---
def seed_data():
    if db:
        shops_col = get_col("dukkanlar")
        if len(list(shops_col.limit(1).stream())) == 0:
            # Örnek Dükkanlar
            sample_shops = [
                {
                    "ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "tel": "03261234567", 
                    "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?q=80&w=800", # Shell/Gas Station
                    "icerik": "Dörtyol'un en güvenilir yakıt istasyonu. 7/24 hizmetinizdeyiz.",
                    "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}, {"ad": "V-Power Dizel", "fiyat": 62.10}]
                },
                {
                    "ad": "Dörtyol Ekmek Fırını", "sektor": "Gıda", "sifre": "123", "tel": "03267120001",
                    "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=800", # Bread/Bakery
                    "icerik": "Odun ateşinde, sıcacık ve taze Dörtyol ekmeği. Hijyen ve kalite bizim işimiz.",
                    "urunler": [{"ad": "Taş Fırın Ekmeği", "fiyat": 10.00}, {"ad": "Susamlı Simit", "fiyat": 12.50}]
                },
                {
                    "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "tel": "05321234567",
                    "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800", # Kunafa with cheese
                    "icerik": "Tescilli Hatay lezzeti. Meşhur peynirli künefemiz ile kral gibi hissedin.",
                    "urunler": [{"ad": "Kral Hasırı (Büyük)", "fiyat": 280.0}, {"ad": "Peynirli Künefe", "fiyat": 190.0}]
                },
                {
                    "ad": "Petrol Ofisi Dörtyol", "sektor": "Ulaşım", "sifre": "123", "tel": "03261112233",
                    "img": "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800", # PO Logo/Station
                    "icerik": "Türkiye'nin enerjisi, Dörtyol'un güvencesi. V-Pro yakıtlarımızla yollar daha kısa.",
                    "urunler": [{"ad": "PO Benzin 95", "fiyat": 60.40}, {"ad": "V-Pro Dizel", "fiyat": 60.00}]
                }
            ]
            for s in sample_shops: shops_col.add(s)
            
            # Örnek İlanlar
            jobs_col = get_col("ilanlar")
            sample_jobs = [
                {"baslik": "Satış Pazarlama Sorumlusu", "isletme": "Antik Kral Künefe", "detay": "Güler yüzlü, satış becerisi yüksek çalışma arkadaşı.", "maas": "25.000 TL + Prim", "tel": "05321234567", "tip": "TAM ZAMANLI", "is_premium": True},
                {"baslik": "Fırın Ustası", "isletme": "Dörtyol Ekmek Fırını", "detay": "Taş fırında tecrübeli, gece mesaisine uygun usta.", "maas": "45.000 TL", "tel": "03267120001", "tip": "TAM ZAMANLI", "is_premium": False},
                {"baslik": "Tezgahtar / Pompa Görevlisi", "isletme": "Shell Dörtyol", "detay": "Müşteri karşılama ve yakıt dolumu yapacak, aktif.", "maas": "22.500 TL", "tel": "03261234567", "tip": "TAM ZAMANLI", "is_premium": False},
                {"baslik": "Ayakçı / Saha Yardımcısı", "isletme": "Petrol Ofisi Dörtyol", "detay": "Günde 5 saat, saha temizliği ve yardım işleri.", "maas": "12.000 TL", "tel": "03261112233", "tip": "VERİMLİ / PART-TIME", "is_premium": False}
            ]
            for j in sample_jobs: jobs_col.add(j)

# --- 5. GİRİŞ VE ANA MANTIK ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL ÇARŞI</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 3, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("PORTALIN KAPISINI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
    st.stop()

st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER", "🔐 PANEL", "🔑 ADMIN"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    if st.session_state.selected_shop_id is None:
        search = st.text_input("🔍 Ne lazım?", placeholder="Benzin, Ekmek, Künefe...")
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            filtered = [s for s in shops if search.lower() in s.get('ad','').lower()]
            
            for s in filtered:
                with st.container():
                    st.markdown(f"""
                    <div class="standard-card">
                        <div class="img-box"><img src="{s.get('img','')}"></div>
                        <h3 style="margin:0;">{s['ad']}</h3>
                        <p style="font-size:0.8rem; color:gray;">{s.get('sektor')} | ⭐ {s.get('puan', 5.0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🏪 Mağazayı İncele: {s['ad']}", key=f"btn_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        st.rerun()
        except: st.info("Sistem verileri tazeleyene kadar bekleyin...")
    else:
        sid = st.session_state.selected_shop_id
        shop_doc = get_col("dukkanlar").document(sid).get()
        if shop_doc.exists:
            s = shop_doc.to_dict()
            if st.button("⬅️ Çarşı Meydanına Dön"):
                st.session_state.selected_shop_id = None
                st.rerun()
            
            st.image(s.get('img',''), use_container_width=True)
            st.title(s['ad'])
            st.info(f"📍 Konum: {s.get('address','Dörtyol')} | 📞 Tel: {s.get('tel','0326')}")
            st.write(f"**Mağaza Hakkında:** {s.get('icerik','')}")
            st.divider()
            st.subheader("📋 Ürün ve Fiyat Kataloğu")
            for p in s.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:12px; border:1px solid #EEE; margin-bottom:8px; display:flex; justify-content:space-between;">
                    <b>{p['ad']}</b><b style="color:#FF8C00;">{p['fiyat']} ₺</b></div>""", unsafe_allow_html=True)

# --- TAB 1: KARİYER ---
with tabs[1]:
    mode = st.radio("", ["İş İlanları", "CV Bankası"], horizontal=True)
    if mode == "İş İlanları":
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f"""
                <div class="standard-card" style="border-left: 5px solid #001F3F;">
                    <span class="badge-job">{j.get('tip','TAM ZAMANLI')}</span>
                    <h4 style="margin:5px 0;">{j['baslik']}</h4>
                    <p style="margin:0;">🏢 <b>{j['isletme']}</b></p>
                    <p style="font-size:0.8rem; margin-top:5px;">{j.get('detay','')}</p>
                    <p style="color:#2E7D32; font-weight:bold;">Maaş: {j.get('maas','Görüşülür')}</p>
                </div>
                """, unsafe_allow_html=True)
        except: st.write("İlanlar yükleniyor...")
    else:
        st.write("Dörtyol'daki CV listesi burada toplanıyor...")
        # CV Gösterme mantığı...

# --- TAB 2: PANEL ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("PANELE GİR"):
            s_docs = get_col("dukkanlar").stream()
            match = next((d for d in s_docs if d.to_dict().get('ad') == l_ad and d.to_dict().get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.id; st.rerun()
    else:
        st.success("Mağaza Yönetimi Aktif!")
        if st.button("🚪 ÇIKIŞ"): st.session_state.owner_shop_id = None; st.rerun()

# --- TAB 3: ADMIN ---
with tabs[3]:
    adm_pwd = st.text_input("Admin Şifresi", type="password")
    if adm_pwd == ADMIN_SIFRE:
        if st.button("🚀 SİSTEMİ İLK VERİLERLE DOLDUR (Shell, Kral vb.)"):
            seed_data()
            st.success("Veriler hafızaya çakıldı!")
        
        st.divider()
        st.write("### 🏪 Mağazalar")
        try:
            for d in get_col("dukkanlar").stream():
                dat = d.to_dict()
                with st.expander(f"{dat.get('ad')}"):
                    st.write(f"Şifre: {dat.get('sifre')}")
                    if st.button(f"SİL: {dat.get('ad')}", key=f"del_{d.id}"):
                        get_col("dukkanlar").document(d.id).delete()
                        st.rerun()
        except: pass

st.markdown(f"<div style='text-align:center; padding-top:50px; color:white; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Master Visual v58</div>", unsafe_allow_html=True)
