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
    page_title="Dörtyol Dijital Şehir Portalı | v71",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.write("Secrets test:", st.secrets.get("app_id"), st.secrets.get("year"))

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# Secrets Kontrolü (Hassas Dedektör)
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
        st.error(f"Sistem Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI BELEDİYE BOTU (HASSAS TARAMA) ---
def get_municipality_data(data_type):
    """Belediye sitesine odaklı, bugünkü 3 vefatı ve duyuruları çeken motor"""
    if not apiKey: return "⚠️ API Anahtarı eksik! Lütfen Secrets kısmını kontrol edin."

    target_prompts = {
        "funeral": "https://www.dortyol.bel.tr sitesini tara. Bugün vefat edenlerin listesini getir. Özellikle bugün vefat eden 3 kişi olduğu bilgisi var, bu kişilerin isimlerini ve cenaze detaylarını madde madde ver.",
        "announcements": "dortyol.bel.tr sitesindeki en güncel ihale, kurs ve belediye duyurularını liste şeklinde ver.",
        "news": "Dörtyol Belediyesi'nin gerçekleştirdiği son faaliyetleri ve projeleri başlıklar halinde özetle.",
        "pharmacy": "Hatay Dörtyol'da bugünkü nöbetçi eczanelerin isim, adres ve telefonlarını liste ver."
    }

    user_query = target_prompts.get(data_type, "")
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen Dörtyol Belediyesi resmi dijital asistanısın. Yazıların her zaman koyu renkli kartlarda okunacağını bilerek, kurumsal ve net bilgiler ver. Bugün 3 vefat olduğu bilgisiyle tarama yap."}]}
    }
    
    # Desteklenen Model: gemini-2.5-flash-preview-09-2025
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=40)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri şu an çekilemedi, lütfen tekrar deneyin.")
        return f"⚠️ Google Hatası (Kod {res.status_code})"
    except: return "⚠️ Bağlantı hatası: Belediye sunucularına erişilemedi."

# --- 4. KURUMSAL TASARIM (MAX OKUNABİLİRLİK) ---
st.markdown("""
    <style>
    /* Ana Tema */
    .stApp {
        background-color: #F8FAFC;
        background-image: linear-gradient(180deg, #003366 0%, #F8FAFC 400px);
        background-attachment: fixed;
    }

    /* Yazı Okunabilirliği Ayarları */
    h1, h2 { color: white !important; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    h3, h4, p, span, li, label { font-family: 'Inter', sans-serif; color: #003366 !important; }
    
    /* Beyaz Alanlardaki Yazıları Zorla Lacivert Yap */
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #003366 !important; font-weight: 500; }

    /* Resmi Belediye Kartları */
    .official-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border-top: 6px solid #FF8C00;
        box-shadow: 0 12px 30px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .official-card h4 { color: #003366 !important; font-weight: 800; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; margin-bottom: 15px; }

    /* Navigasyon Sekmeleri */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.05) !important; 
        color: white !important; 
        border-radius: 12px 12px 0 0 !important;
        padding: 12px 24px !important;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [aria-selected="true"] { background-color: white !important; color: #003366 !important; border: none !important; }

    /* Streamlit Buton Global */
    .stButton>button {
        background: #003366 !important; color: white !important; border-radius: 12px !important; 
        font-weight: 800 !important; border: 2px solid #FF8C00 !important; height: 3.8rem; width: 100%;
    }
    .stButton>button:hover { background: #FF8C00 !important; border-color: #003366 !important; }
    
    input, textarea, select { color: #003366 !important; font-weight: 600 !important; border: 2px solid #CBD5E1 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GİRİŞ KONTROLÜ ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; font-size:3rem; line-height:1;">🏛️ DÖRTYOL <br/> ŞEHİR PORTALI</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("PORTALI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 style="text-align:center; margin-top:-40px;">🏛️ DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:white; font-weight:700;">T.C. Dörtyol Belediyesi Dijital Hizmet Ağı</p>', unsafe_allow_html=True)

tabs = st.tabs(["📢 ŞEHİR NABZI", "🏛️ E-BELEDİYE", "🛍️ ESNAF ÇARŞISI", "💼 KARİYER", "🔑 YÖNETİM"])

# --- TAB 0: ŞEHİR NABZI ---
with tabs[0]:
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live = data_snap.to_dict() if data_snap.exists else {}
    except: live = {}

    st.markdown(f'<div class="official-card"><h4>🕯️ Vefat Haberleri (Güncel)</h4>{live.get("funeral", "*Belediye kayıtları yükleniyor...*")}</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="official-card"><h4>💊 Nöbetçi Eczaneler</h4>{live.get("pharmacy", "*Lütfen güncelleyin.*")}</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="official-card"><h4>🔔 Duyurular & İhaleler</h4>{live.get("announcements", "*Kayıt yok.*")}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="official-card"><h4>📰 Belediye Haberleri</h4>{live.get("news", "*Akış bekleniyor.*")}</div>', unsafe_allow_html=True)

# --- TAB 1: E-BELEDİYE ---
with tabs[1]:
    st.markdown('<div class="official-card"><h4>🏛️ Belediye Başkanı Mesajı</h4><p>"Dörtyolumuzu Türkiye Yüzyılı vizyonuna hazırlıyoruz. Dijital belediyecilikle tüm hemşehrilerimizin yanındayız."</p></div>', unsafe_allow_html=True)
    m_cols = st.columns(3)
    # Hızlı İşlem Butonları (Görsel temsil)
    for col, title in zip(m_cols*2, ["💳 Vergi Ödeme", "🏗️ E-İmar Planı", "📜 Rayiç Değer", "🗺️ Kent Rehberi", "📦 Sosyal Yardım", "✍️ Başkana Yazın"]):
        with col: st.button(title, key=f"eb_btn_{title}")

# --- TAB 2: ESNAF ÇARŞISI ---
with tabs[2]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f'<div class="official-card"><h3>{s["ad"]}</h3><p><b>Sektör:</b> {s.get("sektor")} | 📍 Dörtyol Merkez</p></div>', unsafe_allow_html=True)
                if st.button(f"🏪 İncele: {s['ad']}", key=f"shop_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    st.rerun()
        except: st.info("Dükkanlar yükleniyor...")
    else:
        sid = st.session_state.selected_shop_id
        doc = get_col("dukkanlar").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            if s.get('img'): st.image(s['img'], use_container_width=True)
            st.title(s['ad'])
            st.divider()
            for p in s.get('urunler', []):
                st.markdown(f'<div class="official-card" style="display:flex; justify-content:space-between; border-top:none; border-left:6px solid #FF8C00;"><b>{p["ad"]}</b><b style="color:#003366;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 3: KARİYER ---
with tabs[3]:
    st.subheader("Dörtyol İstihdam Merkezi")
    k_tabs = st.tabs(["📢 Aktif İlanlar", "👤 CV Bankası"])
    with k_tabs[0]:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            if not jobs: st.write("Şu an aktif ilan bulunamadı.")
            for j in jobs:
                st.markdown(f'<div class="official-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>📞 İletişim: {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: pass
    with k_tabs[1]:
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            for c in cvs:
                st.markdown(f'<div class="official-card"><h4>👤 {c["ad"]}</h4><p><b>Hedef:</b> {c.get("uzm","")} | <b>Tür:</b> {c.get("tur","")}</p><p><i>"{c.get("yazi","")}"</i></p></div>', unsafe_allow_html=True)
        except: st.write("CV Bankası boş.")

# --- TAB 4: YÖNETİM ---
with tabs[4]:
    adm = st.text_input("Yönetici Yetkilendirme", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Girişi Başarılı.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🕯️ VEFAT GÜNCELLE"):
                res = get_municipality_data("funeral")
                get_col("sistem_bilgi").document("canli").set({"funeral": res}, merge=True); st.rerun()
        with c2:
            if st.button("🔔 DUYURU GÜNCELLE"):
                res = get_municipality_data("announcements")
                get_col("sistem_bilgi").document("canli").set({"announcements": res}, merge=True); st.rerun()
        with c3:
            if st.button("📰 HABER GÜNCELLE"):
                res = get_municipality_data("news")
                get_col("sistem_bilgi").document("canli").set({"news": res}, merge=True); st.rerun()
        with c4:
            if st.button("💊 ECZANE GÜNCELLE"):
                res = get_municipality_data("pharmacy")
                get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:#003366; font-weight:800;'>© {GUNCEL_YIL} Dörtyol Dijital Şehir Portalı | v71 Zirve</div>", unsafe_allow_html=True)
