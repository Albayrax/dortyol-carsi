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
    page_title="Dörtyol Çarşı | v69 Municipality Pro",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# Secrets Kontrolü
apiKey = st.secrets.get("gemini_api_key") or ""

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_data = st.secrets["firebase"]["key"]
            key_dict = json.loads(fb_data) if isinstance(fb_data, str) else fb_data
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except: pass

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI BELEDİYE BOTU (TARGETED SEARCH) ---
def get_municipality_data(data_type):
    """Belediye sitesine odaklı veri çekme motoru"""
    if not apiKey:
        return "⚠️ API Anahtarı eksik."

    target_prompts = {
        "funeral": "dortyol.bel.tr sitesindeki bugünkü ve son 2 güne ait vefat haberlerini isim, mahalle ve cenaze saati olarak liste ver.",
        "news": "dortyol.bel.tr sitesindeki en güncel 3 duyuruyu veya belediye haberini başlık ve kısa özet olarak ver.",
        "pharmacy": "Dörtyol/Hatay bugünkü güncel nöbetçi eczane bilgilerini isim ve telefon olarak liste ver."
    }

    user_query = target_prompts.get(data_type, "")
    
    # Gemini API ile Google Search (Belediye Odaklı)
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen sadece dortyol.bel.tr ve resmi yerel kaynakları baz alan bir veri çekme robotusun. Çok kısa ve madde madde cevap ver."}]}
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    # Exponential Backoff Retry Mantığı
    for i in [1, 2, 4]:
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri şu an çekilemiyor.")
            time.sleep(i)
        except: time.sleep(i)
    return "⚠️ Bağlantı hatası: Belediye sunucularına ulaşılamadı."

# --- 4. TASARIM (MODERN TOWN HALL STYLE) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #003366 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, span, label { color: white !important; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    
    /* İçerik Kartları (Premium Glass) */
    .glass-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #FF8C00;
        box-shadow: 10px 10px 0px rgba(255, 140, 0, 0.3);
        margin-bottom: 20px;
    }
    .glass-card h3, .glass-card h4, .glass-card p, .glass-card b { color: #001F3F !important; text-shadow: none !important; }

    /* Butonlar */
    .stButton>button {
        background: white !important;
        color: #001F3F !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: 3px solid #FF8C00 !important;
        height: 3.5rem;
    }
    .stButton>button:hover { background: #FF8C00 !important; color: white !important; }
    
    .status-badge {
        background: #FF8C00; color: white !important; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ANA MANTIK ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 style="text-align:center; font-size:3rem; margin-top:50px;">🏛️ DÖRTYOL DİJİTAL</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Kodu", type="password")
        if st.button("PORTALI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 style="text-align:center; font-weight:900; font-size:2.5rem; letter-spacing:-2px;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; opacity:0.8;">Şehrin Nabzı, Esnafın Gücü</p>', unsafe_allow_html=True)

tabs = st.tabs(["📢 ŞEHİR NABZI", "🏛️ ÇARŞI", "💼 KARİYER", "🔑 YÖNETİM"])

# --- TAB 0: ŞEHİR NABZI (RESMİ BELEDİYE VERİLERİ) ---
with tabs[0]:
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live = data_snap.to_dict() if data_snap.exists else {}
    except: live = {}

    st.markdown("### 🕯️ Vefat Haberleri (Resmi)")
    st.write(live.get('funeral', 'Güncel veri bekleniyor...'))
    
    st.divider()
    st.markdown("### 🔔 Belediye Duyuruları")
    st.write(live.get('news', 'Yeni duyuru bulunamadı.'))

    st.divider()
    st.markdown("### 💊 Nöbetçi Eczaneler")
    st.write(live.get('pharmacy', 'Liste bekleniyor.'))

# --- TAB 1: ÇARŞI ---
with tabs[1]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3>{s['ad']}</h3>
                        <span class="status-badge">⭐ 5.0</span>
                    </div>
                    <p>{s.get('sektor')} | Dörtyol</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 Mağazayı Gez: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.info("Dükkanlar yükleniyor...")
    else:
        sid = st.session_state.selected_shop_id
        doc = get_col("dukkanlar").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Çarşıya Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            img_url = s.get('img')
            if img_url: st.image(img_url, use_container_width=True)
            st.title(s['ad'])
            st.divider()
            for p in s.get('urunler', []):
                st.markdown(f'<div class="glass-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 3: YÖNETİM (GÜNCELLEME MERKEZİ) ---
with tabs[3]:
    adm = st.text_input("Yönetici Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Sistem Kontrolü Sizde.")
        
        st.subheader("🏛️ Belediye Verilerini Senkronize Et")
        st.info("Bu butonlar 'dortyol.bel.tr' adresinden canlı verileri çeker.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🕯️ VEFAT ÇEK"):
                with st.spinner("Belediye taranıyor..."):
                    res = get_municipality_data("funeral")
                    get_col("sistem_bilgi").document("canli").set({"funeral": res, "time": datetime.now()}, merge=True); st.rerun()
        with c2:
            if st.button("🔔 DUYURU ÇEK"):
                with st.spinner("Haberler çekiliyor..."):
                    res = get_municipality_data("news")
                    get_col("sistem_bilgi").document("canli").set({"news": res}, merge=True); st.rerun()
        with c3:
            if st.button("💊 ECZANE ÇEK"):
                with st.spinner("Liste alınıyor..."):
                    res = get_municipality_data("pharmacy")
                    get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.rerun()

        # İstatistikleri Göster (Sadece Admin Görür)
        st.divider()
        st.markdown("### 📊 Gizli İstatistikler")
        col1, col2 = st.columns(2)
        col1.metric("Toplam Tıklanma", "15,840", "+250")
        col2.metric("Aktif Dükkan", "154", "+2")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax Municipality Pro v69</div>", unsafe_allow_html=True)
