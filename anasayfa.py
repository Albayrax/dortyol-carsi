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
    page_title="Dörtyol Dijital Şehir Portalı | v72 Mirror Horizon",
    page_icon="🏛️",
    layout="centered",
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
    """Bulut veri tabanı yolu"""
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI BELEDİYE BOTU (REFAH TARAMA) ---
def get_municipality_data(data_type):
    """Belediye sitesinden canlı veri çeken yapay zeka motoru"""
    if not apiKey: return "⚠️ API Anahtarı eksik! Lütfen Secrets kutusunu kontrol edin."

    prompts = {
        "funeral": "dortyol.bel.tr sitesini tara. Bugün vefat edenlerin isimlerini, mahallelerini ve cenaze vakitlerini liste halinde ver. Bugün 3 vefat haberi olduğu bilgisini doğrula.",
        "notices": "dortyol.bel.tr sitesindeki en yeni belediye duyurularını, ihaleleri ve sosyal etkinlikleri başlıklar halinde ver.",
        "pharmacy": "Dörtyol Hatay bugünkü nöbetçi eczaneleri isim, telefon ve tam adres olarak liste ver."
    }

    payload = {
        "contents": [{"parts": [{"text": prompts.get(data_type, "")}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen profesyonel bir belediye veri botusun. Bilgileri kısa, öz ve tablo/madde formatında sun."}]}
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=35)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri şu an çekilemedi.")
    except: pass
    return "⚠️ Sunucu meşgul, lütfen Admin panelinden tekrar güncelleyin."

# --- 4. MIRROR AI TASARIM (GELİŞMİŞ CSS) ---
st.markdown(f"""
    <style>
    /* Mirror AI / Dinamik Arka Plan */
    .stApp {{
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }}

    /* Yazı Okunabilirliği ve Kontrast */
    h1, h2, h3, h4, p, span, label, b {{ 
        font-family: 'Inter', sans-serif;
        color: #003366 !important; /* Kart içi standart */
    }}

    /* Ana Başlıklar Beyaz ve Gölgeli */
    .main-title {{ 
        color: white !important; 
        text-align: center; 
        font-weight: 900; 
        font-size: 2.8rem; 
        text-shadow: 3px 3px 10px rgba(0,0,0,0.5); 
        margin-top: -60px;
    }}

    /* Mirror Card Tasarımı (Glassmorphism) */
    .mirror-card {{
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(15px);
        padding: 22px;
        border-radius: 22px;
        border-left: 8px solid #FF8C00;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        transition: 0.3s ease;
    }}
    .mirror-card:hover {{ transform: scale(1.02); border-left-color: #003366; }}

    /* Skor Tablosu Kartı */
    .score-card {{
        background: #001F3F;
        color: white !important;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #FF8C00;
    }}
    .score-card h5 {{ color: #FF8C00 !important; margin: 0; font-size: 0.7rem; text-transform: uppercase; }}
    .score-card h2 {{ color: white !important; margin: 5px 0; font-size: 1.8rem; }}

    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; background: rgba(0,0,0,0.2); padding: 5px; border-radius: 12px; }}
    .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: 800; border: none !important; }}
    .stTabs [aria-selected="true"] {{ background: white !important; color: #001F3F !important; border-radius: 8px !important; }}

    /* Butonlar */
    .stButton>button {{
        background: white !important;
        color: #003366 !important;
        border: 2px solid #FF8C00 !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        height: 3.5rem;
    }}
    .stButton>button:hover {{ background: #FF8C00 !important; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. GİRİŞ KONTROLÜ ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL <br/> ŞEHİR PORTALINA HOŞGELDİNİZ</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Kodu", type="password", placeholder="dortyol2026")
        if st.button("PORTALIN KAPISINI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# --- ŞEHİR SKOR TABLOLARI (STATİSTİKLER) ---
col1, col2, col3 = st.columns(3)
with col1: st.markdown('<div class="score-card"><h5>👥 ZİYARETÇİ</h5><h2>14.2K</h2></div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="score-card"><h5>🏪 ESNAF</h5><h2>158</h2></div>', unsafe_allow_html=True)
with col3: st.markdown('<div class="score-card"><h5>💼 İLANLAR</h5><h2>42</h2></div>', unsafe_allow_html=True)

tabs = st.tabs(["📢 ŞEHİR NABZI", "🏛️ E-BELEDİYE", "🛍️ ESNAF ÇARŞISI", "👤 CV BANKASI", "🔑 YÖNETİM"])

# --- TAB 0: ŞEHİR NABZI ---
with tabs[0]:
    try:
        live = get_col("sistem_bilgi").document("canli").get().to_dict() or {}
    except: live = {}

    st.markdown(f'<div class="mirror-card"><h4>🕯️ Vefat Haberleri (Belediye Onaylı)</h4><p>{live.get("funeral", "Veri bekleniyor... Admin panelinden güncelleyin.")}</p></div>', unsafe_allow_html=True)
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown(f'<div class="mirror-card"><h4>💊 Nöbetçi Eczaneler</h4><p>{live.get("pharmacy", "Bekleniyor.")}</p></div>', unsafe_allow_html=True)
    with c_b:
        st.markdown(f'<div class="mirror-card"><h4>🔔 Güncel Duyurular</h4><p>{live.get("notices", "Kayıt yok.")}</p></div>', unsafe_allow_html=True)

# --- TAB 1: E-BELEDİYE ---
with tabs[1]:
    st.markdown('<div class="mirror-card"><h4>🏛️ E-Belediye İşlem Merkezi</h4><p>Resmi işlemlerinizi portal üzerinden hızlıca başlatabilirsiniz.</p></div>', unsafe_allow_html=True)
    e_cols = st.columns(3)
    titles = ["💳 Vergi Borcu", "🏗️ E-İmar Durumu", "📜 Rayiç Sorgulama", "🗺️ Kent Rehberi", "📦 Sosyal Yardım", "✍️ Başkana Mesaj"]
    for i, title in enumerate(titles):
        with e_cols[i % 3]:
            if st.button(title): st.toast(f"{title} servisi belediye sitesine yönlendiriliyor...")

# --- TAB 2: ESNAF ÇARŞISI ---
with tabs[2]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f"""
                <div class="mirror-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h3>{s['ad']}</h3>
                        <b style="color:#FF8C00;">⭐ 5.0</b>
                    </div>
                    <p><b>Sektör:</b> {s.get('sektor')} | 👁️ {s.get('tıklanma',0)} Görüntülenme</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 Detaylar: {s['ad']}", key=f"s_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.info("Hafıza yükleniyor...")
    else:
        sid = st.session_state.selected_shop_id
        shop = get_col("dukkanlar").document(sid).get().to_dict()
        if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.title(shop['ad'])
            if shop.get('img'): st.image(shop['img'], use_container_width=True)
            st.divider()
            for p in shop.get('urunler', []):
                st.markdown(f'<div class="mirror-card" style="border-left:none; border-top:4px solid #FF8C00; display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 3: CV BANKASI ---
with tabs[3]:
    st.subheader("👤 Dörtyol İstihdam ve CV Havuzu")
    cv_sub1, cv_sub2 = st.tabs(["📢 İş İlanları", "👤 CV Bırak / Banka"])
    
    with cv_sub1:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="mirror-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>💰 {j.get("maas","Görüşülür")}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("İlan yok.")
    
    with cv_sub2:
        with st.form("cv_form_v72"):
            st.write("Dörtyol esnafının size ulaşması için bilgilerinizi girin.")
            c_ad = st.text_input("Ad Soyad*")
            c_is = st.text_input("İstenen Pozisyon*")
            c_tel = st.text_input("WhatsApp No*")
            c_not = st.text_area("Kısa Not")
            if st.form_submit_button("BANKAYA KAYDET"):
                if c_ad and c_is and c_tel:
                    get_col("cvler").add({"ad": c_ad, "is": c_is, "tel": c_tel, "not": c_not, "tarih": datetime.now()})
                    st.success("Kaydınız yapıldı!"); time.sleep(1); st.rerun()

        st.divider()
        st.write("🔍 Kayıtlı CV Listesi")
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            for c in cvs:
                st.markdown(f'<div class="mirror-card"><b>{c["ad"]}</b><br>🎯 {c["is"]}<br>📞 {c["tel"]}</div>', unsafe_allow_html=True)
        except: pass

# --- TAB 4: YÖNETİM ---
with tabs[4]:
    adm = st.text_input("Admin Anahtarı", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Resmi Yönetici Girişi Başarılı.")
        st.subheader("🏛️ Belediye Veri Senkronizasyonu")
        
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("🕯️ VEFAT GÜNCELLE"):
                with st.spinner("Taranıyor..."):
                    res = get_municipality_data("funeral")
                    get_col("sistem_bilgi").document("canli").set({"funeral": res}, merge=True); st.rerun()
        with cb:
            if st.button("🔔 DUYURU GÜNCELLE"):
                with st.spinner("Çekiliyor..."):
                    res = get_municipality_data("notices")
                    get_col("sistem_bilgi").document("canli").set({"notices": res}, merge=True); st.rerun()
        with cc:
            if st.button("💊 ECZANE GÜNCELLE"):
                with st.spinner("Yükleniyor..."):
                    res = get_municipality_data("pharmacy")
                    get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white; font-weight:800;'>© {GUNCEL_YIL} Albayrax Mirror Horizon v72 | Dörtyol Dijital Portal</div>", unsafe_allow_html=True)
