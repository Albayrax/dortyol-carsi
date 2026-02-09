import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests
import re

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Dijital Şehir Portalı | v73 Nexus",
    page_icon="🏛️",
    layout="wide", # Hepsiburada tarzı geniş yerleşim için 'wide' seçtik
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# Secrets Kontrolü
apiKey = st.secrets.get("gemini_api_key") or st.secrets.get("gemini-api-key") or ""

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_data = st.secrets["firebase"]["key"]
            key_dict = json.loads(fb_data) if isinstance(fb_data, str) else fb_data
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Sistem Hafıza Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI BELEDİYE BOTU ---
def get_municipality_data(data_type):
    if not apiKey: return "⚠️ API Anahtarı eksik!"
    prompts = {
        "funeral": "dortyol.bel.tr sitesini tara. Bugün vefat edenlerin isimlerini, mahallelerini ve cenaze vakitlerini liste halinde ver.",
        "notices": "dortyol.bel.tr sitesindeki en yeni belediye duyurularını ve ihaleleri ver.",
        "pharmacy": "Dörtyol Hatay bugünkü nöbetçi eczaneleri isim, telefon ve adres olarak ver."
    }
    payload = {
        "contents": [{"parts": [{"text": prompts.get(data_type, "")}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen profesyonel bir belediye veri botusun. Bilgileri kısa, öz ve kurumsal sun."}]}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    try:
        res = requests.post(url, json=payload, timeout=35)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri bulunamadı.")
    except: pass
    return "⚠️ Bağlantı hatası."

# --- 4. NEXUS DİNAMİK TASARIM (DALLANAN MENÜ & ARKA PLAN) ---
st.markdown(f"""
    <style>
    /* Dinamik Mirror AI Arka Plan */
    .stApp {{
        background: linear-gradient(-45deg, #FF8C00, #EE7752, #23A6D5, #23D5AB, #001F3F);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        background-attachment: fixed;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Hepsiburada Tarzı Üzerine Gelince Dallanan Menü (CSS Mega Menu) */
    .nexus-nav {{
        display: flex;
        justify-content: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 30px;
        position: relative;
        z-index: 1000;
    }}

    .nav-item {{
        position: relative;
        padding: 10px 25px;
        color: white;
        font-weight: 800;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .nav-item:hover {{ color: #FF8C00; }}

    /* Dallanan Alt Menü (Zihin Haritası Mantığı) */
    .sub-menu {{
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        background: white;
        min-width: 250px;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        padding: 10px 0;
        animation: slideIn 0.3s ease;
    }}

    .nav-item:hover .sub-menu {{ display: block; }}

    .sub-item {{
        padding: 12px 20px;
        color: #003366;
        border-bottom: 1px solid #F0F0F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }}

    .sub-item:hover {{ background: #F8FAFC; color: #FF8C00; }}

    /* Yana Doğru Dallanma */
    .nested-menu {{
        display: none;
        position: absolute;
        left: 100%;
        top: 0;
        background: #FDFDFD;
        min-width: 200px;
        border-radius: 15px;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.1);
        padding: 10px 0;
    }}

    .sub-item:hover .nested-menu {{ display: block; }}

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Hareketli Fırsat Baloncukları */
    .floating-badge {{
        position: fixed;
        background: #FF8C00;
        color: white;
        padding: 8px 15px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 0.7rem;
        box-shadow: 0 5px 15px rgba(255, 140, 0, 0.4);
        z-index: 100;
        animation: float 6s ease-in-out infinite;
    }}

    @keyframes float {{
        0%, 100% {{ transform: translateY(0) rotate(0); }}
        50% {{ transform: translateY(-20px) rotate(5deg); }}
    }}

    /* Kartlar (Hepsiburada Ürün Kartı Stili) */
    .nexus-card {{
        background: white;
        border-radius: 20px;
        padding: 0;
        overflow: hidden;
        border: 1px solid #EEE;
        transition: 0.4s;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .nexus-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        border-color: #FF8C00;
    }}
    
    .card-img {{ width: 100%; height: 180px; object-fit: cover; border-bottom: 3px solid #FF8C00; }}
    .card-content {{ padding: 20px; flex-grow: 1; }}
    .card-title {{ font-weight: 900; color: #003366; font-size: 1.2rem; margin-bottom: 5px; }}
    .card-tag {{ background: #E8F5E9; color: #2E7D32; font-size: 0.7rem; padding: 3px 10px; border-radius: 5px; font-weight: 700; }}

    .main-title {{ 
        color: white; text-align: center; font-weight: 900; font-size: 3.2rem; 
        text-shadow: 4px 4px 15px rgba(0,0,0,0.4); margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. HAREKETLİ FIRSAT BALONCUKLARI ---
st.markdown('<div class="floating-badge" style="top: 20%; left: 5%;">🔥 Kral Künefe %10 İndirim</div>', unsafe_allow_html=True)
st.markdown('<div class="floating-badge" style="top: 60%; right: 10%;">⛽ Benzin 60.50 ₺</div>', unsafe_allow_html=True)
st.markdown('<div class="floating-badge" style="top: 40%; left: 2%;">💼 3 Yeni İş İlanı</div>', unsafe_allow_html=True)

# --- 6. GİRİŞ KONTROLÜ ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">DÖRTYOL NEXUS <br/> HOŞGELDİNİZ</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("SİSTEMİ BAŞLAT"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER & DALLANAN MENÜ ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# Custom Dallanan Menü (Zihin Haritası Tarzı)
st.markdown("""
<div class="nexus-nav">
    <div class="nav-item">🏠 ANA SAYFA</div>
    <div class="nav-item">🏛️ BELEDİYE
        <div class="sub-menu">
            <div class="sub-item">Haberler & Duyurular ➡️
                <div class="nested-menu">
                    <div class="sub-item">🕯️ Vefat Bilgileri</div>
                    <div class="sub-item">🏗️ İhaleler</div>
                    <div class="sub-item">🎉 Etkinlikler</div>
                </div>
            </div>
            <div class="sub-item">E-Belediye ➡️
                <div class="nested-menu">
                    <div class="sub-item">💳 Vergi Ödeme</div>
                    <div class="sub-item">📜 Arsa Rayiç</div>
                    <div class="sub-item">✍️ Başkana Mesaj</div>
                </div>
            </div>
        </div>
    </div>
    <div class="nav-item">🛍️ ÇARŞI
        <div class="sub-menu">
            <div class="sub-item">Gıda & Tatlı ➡️
                <div class="nested-menu">
                    <div class="sub-item">🥮 Künefeciler</div>
                    <div class="sub-item">🥩 Kebapçılar</div>
                    <div class="sub-item">🥖 Fırınlar</div>
                </div>
            </div>
            <div class="sub-item">Yatırım & Ulaşım ➡️
                <div class="nested-menu">
                    <div class="sub-item">💰 Kuyumcular</div>
                    <div class="sub-item">⛽ Akaryakıt</div>
                </div>
            </div>
        </div>
    </div>
    <div class="nav-item">💼 KARİYER
        <div class="sub-menu">
            <div class="sub-item">👤 İş Arayanlar</div>
            <div class="sub-item">📢 Aktif İlanlar</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- ANA İÇERİK ---
tabs = st.tabs(["📢 ŞEHİR NABZI", "🛍️ ESNAF VİTRİNİ", "👤 CV BANKASI", "🔑 YÖNETİM"])

with tabs[0]:
    try:
        live = get_col("sistem_bilgi").document("canli").get().to_dict() or {}
    except: live = {}
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="nexus-card" style="padding:20px;"><h3>🕯️ Güncel Vefat Listesi</h3><p>{live.get("funeral", "Bekleniyor...")}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="nexus-card" style="padding:20px;"><h3>💊 Nöbetçi Eczaneler</h3><p>{live.get("pharmacy", "Lütfen güncelleyin.")}</p></div>', unsafe_allow_html=True)

with tabs[1]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            cols = st.columns(3)
            for i, s in enumerate(shops):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="nexus-card">
                        <img src="{s.get('img','https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800')}" class="card-img">
                        <div class="card-content">
                            <span class="card-tag">{s.get('sektor','Esnaf')}</span>
                            <div class="card-title">{s['ad']}</div>
                            <p style="color:#666; font-size:0.8rem;">👁️ {s.get('tıklanma',0)} Görüntülenme</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🏪 İncele: {s['ad']}", key=f"s_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
        except: st.info("Dükkanlar yükleniyor...")
    else:
        sid = st.session_state.selected_shop_id
        shop = get_col("dukkanlar").document(sid).get().to_dict()
        if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.title(shop['ad'])
            if shop.get('img'): st.image(shop['img'], use_container_width=True)
            for p in shop.get('urunler', []):
                st.markdown(f'<div class="nexus-card" style="padding:20px; margin-bottom:10px; display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

with tabs[3]:
    adm = st.text_input("Yönetici Girişi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Kontrol Paneli Aktif.")
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("🕯️ VEFAT GÜNCELLE"):
                res = get_municipality_data("funeral")
                get_col("sistem_bilgi").document("canli").set({"funeral": res}, merge=True); st.rerun()
        with cb:
            if st.button("💊 ECZANE GÜNCELLE"):
                res = get_municipality_data("pharmacy")
                get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.rerun()
        with cc:
            if st.button("🔔 DUYURU GÜNCELLE"):
                res = get_municipality_data("notices")
                get_col("sistem_bilgi").document("canli").set({"notices": res}, merge=True); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white; font-weight:800;'>© {GUNCEL_YIL} Albayrax Nexus v73 | Dörtyol Dijital Şehir Portalı</div>", unsafe_allow_html=True)
