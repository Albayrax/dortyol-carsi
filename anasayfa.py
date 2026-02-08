import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import re

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v60 Final Fix",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

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
    # Public Data Yolu (MANDATORY RULE 1)
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. GÖRSEL TASARIM (HIGH CONTRAST & MIRROR AI STYLE) ---
st.markdown("""
    <style>
    /* Mirror AI Temalı Dinamik Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }

    /* Yazıların Okunması İçin Ana Konteyner */
    h1, h2, h3, h4, p, span, label { 
        color: white !important; 
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }

    /* Kart Tasarımları */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }
    
    .content-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #001F3F;
        box-shadow: 8px 8px 0px #001F3F;
    }
    
    .content-card h3, .content-card p, .content-card b {
        color: #001F3F !important;
        text-shadow: none !important;
    }

    /* Butonlar */
    .stButton>button {
        background-color: white !important;
        color: #001F3F !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: 2px solid #001F3F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SİSTEM BAŞLATICI (MANDATORY DATA) ---
def seed_system():
    if db:
        # 1. DÜKKANLAR
        d_col = get_col("dukkanlar")
        shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?w=800", "icerik": "7/24 Güvenli Yakıt", "tel":"0326", "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}]},
            {"ad": "Meydan Fırını", "sektor": "Gıda", "sifre": "123", "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800", "icerik": "Sıcak Taş Fırın Ekmeği", "tel":"0326", "urunler": [{"ad": "Ekmek", "fiyat": 10.00}]},
            {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?w=800", "icerik": "Meşhur Hatay Lezzeti", "tel":"0532", "urunler": [{"ad": "Kral Hasırı", "fiyat": 240.0}]}
        ]
        for s in shops: d_col.add(s)

        # 2. İLANLAR
        i_col = get_col("ilanlar")
        jobs = [
            {"baslik": "Usta Pideci", "isletme": "Meydan Fırını", "tel": "0326", "detay": "Tecrübeli usta aranıyor.", "maas": "45.000 TL"},
            {"baslik": "Satış Elemanı", "isletme": "Kral Künefe", "tel": "0532", "detay": "Güler yüzlü eleman.", "maas": "25.000 TL"},
            {"baslik": "Pompa Görevlisi", "isletme": "Shell Dörtyol", "tel": "0326", "detay": "Vardiyalı çalışacak.", "maas": "22.500 TL"}
        ]
        for j in jobs: i_col.add(j)

        # 3. CVLER
        c_col = get_col("cvler")
        cvs = [
            {"ad": "Ahmet Yılmaz", "is": "Şoför / Kurye", "tel": "0500", "yazi": "Dörtyol içi her yeri bilirim."},
            {"ad": "Mehmet Can", "is": "Garson / Komi", "tel": "0501", "yazi": "Hızlı ve enerjik çalışırım."}
        ]
        for c in cvs: c_col.add(c)

# --- 5. ANA MANTIK VE NAVİGASYON ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL ÇARŞI</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 3, 1])
    with c:
        pwd = st.text_input("Giriş Kodu", type="password")
        if st.button("SİSTEME GİR"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER", "🔐 PANEL", "🔑 ADMIN"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f'<div class="content-card"><h3>{s["ad"]}</h3><p>{s.get("sektor")} | ⭐ 5.0</p></div>', unsafe_allow_html=True)
                if st.button(f"İncele: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    st.rerun()
        except: st.info("Hafıza boş. Admin panelinden 'Sistemi Kur' butonuna basın.")
    else:
        # DETAY SAYFASI
        doc = get_col("dukkanlar").document(st.session_state.selected_shop_id).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Çarşıya Geri Dön"): 
                st.session_state.selected_shop_id = None
                st.rerun()
            
            # Resim Hata Koruması
            img_url = s.get('img')
            if img_url and img_url.startswith("http"):
                st.image(img_url, use_container_width=True)
            else:
                st.warning("Bu dükkanın resmi henüz yüklenmemiş.")
            
            st.markdown(f"<h2>{s['ad']}</h2>", unsafe_allow_html=True)
            st.info(f"📞 İletişim: {s.get('tel','0326')}")
            st.write(s.get('icerik',''))
            st.divider()
            for p in s.get('urunler', []):
                st.markdown(f'<div class="content-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 1: KARİYER ---
with tabs[1]:
    sub_tabs = st.tabs(["📢 İş İlanları", "👤 CV Bankası"])
    
    with sub_tabs[0]:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="content-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>💰 {j.get("maas","")}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("İlan yok.")
        
    with sub_tabs[1]:
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            if not cvs: st.write("CV Bankası şu an boş.")
            for c in cvs:
                st.markdown(f'<div class="content-card"><b>👤 {c["ad"]}</b><br>🎯 {c["is"]}<br>📞 {c["tel"]}<p style="font-size:0.8rem;">{c.get("yazi","")}</p></div>', unsafe_allow_html=True)
        except: st.write("CV yüklenemedi.")

# --- TAB 3: ADMIN ---
with tabs[3]:
    adm = st.text_input("Admin Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Girişi Başarılı")
        if st.button("🚀 SİSTEMİ KUR VE ÖRNEK VERİLERİ YÜKLE"):
            seed_system()
            st.success("Tüm veriler (Dükkanlar, CV'ler, İlanlar) Firebase'e yüklendi!")
        
        st.divider()
        if st.button("🗑️ TÜM VERİLERİ TEMİZLE"):
            # Temizleme mantığı buraya gelebilir
            st.warning("Bu özellik manuel olarak Firebase panelinden yapılmalıdır.")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.5; color:white;'>© {GUNCEL_YIL} Albayrax Final Fix v60</div>", unsafe_allow_html=True)
