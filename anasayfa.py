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
    page_title="Dörtyol Dijital Şehir Portalı | v70",
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

# --- 3. AKILLI BELEDİYE BOTU (GELİŞMİŞ) ---
def get_municipality_data(data_type):
    """Belediye sitesine odaklı profesyonel veri çekme motoru"""
    if not apiKey: return "⚠️ API Anahtarı eksik."

    target_prompts = {
        "funeral": "dortyol.bel.tr sitesindeki bugünkü vefat haberlerini (isim, mahalle, cenaze saati) liste şeklinde ver.",
        "announcements": "dortyol.bel.tr sitesindeki güncel duyuruları, ihaleleri ve kurs ilanlarını başlıklar halinde ver.",
        "news": "Dörtyol Belediyesi'nin son 3 güncel haberini başlık ve kısa özet olarak ver.",
        "pharmacy": "Dörtyol Hatay bugün nöbetçi eczane bilgilerini isim ve telefon olarak liste ver."
    }

    user_query = target_prompts.get(data_type, "")
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen bir belediye asistanısın. Sadece resmi kaynakları baz alarak, kurumsal bir dille, kısa ve öz liste ver."}]}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri şu an çekilemiyor.")
    except: pass
    return "⚠️ Bağlantı hatası: Sunucuya ulaşılamadı."

# --- 4. KURUMSAL TASARIM (TOWN HALL UI) ---
st.markdown("""
    <style>
    /* Belediye Kurumsal Teması */
    .stApp {
        background-color: #F4F7F9;
        background-image: linear-gradient(180deg, #003366 0%, #F4F7F9 350px);
        background-attachment: fixed;
    }

    h1, h2, h3, h4, p, span, label { font-family: 'Inter', sans-serif; }
    .main-header { color: white !important; font-weight: 900; text-align: center; margin-top: -50px; font-size: 2.2rem; }
    
    /* Kartlar (Official Glassmorphism) */
    .official-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-top: 5px solid #FF8C00;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .official-card h3, .official-card h4 { color: #003366 !important; margin-top: 0; }
    .official-card p { color: #444 !important; line-height: 1.6; }

    /* Navigasyon Sekmeleri */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.1) !important; 
        color: white !important; 
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 20px !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: white !important; color: #003366 !important; }

    /* Hızlı İşlem Butonları */
    .quick-action {
        background: #003366; color: white !important; padding: 15px; border-radius: 12px; text-align: center; 
        cursor: pointer; transition: 0.3s; font-weight: bold; border: 1px solid rgba(255,255,255,0.2);
    }
    .quick-action:hover { background: #FF8C00; transform: translateY(-3px); }

    /* Buton Tasarımı */
    .stButton>button {
        background: #003366 !important; color: white !important; border-radius: 10px !important; font-weight: 800 !important;
        border: none !important; height: 3.5rem; transition: 0.3s;
    }
    .stButton>button:hover { background: #FF8C00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GİRİŞ KONTROLÜ ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">DÖRTYOL DİJİTAL <br/> ŞEHİR PORTALI</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Kodu", type="password")
        if st.button("PORTALA GİRİŞ YAP"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 class="main-header">🏛️ DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:white; opacity:0.9;">Geleceğin Akıllı Şehri Dörtyol</p>', unsafe_allow_html=True)

tabs = st.tabs(["📢 ŞEHİR NABZI", "🏛️ E-BELEDİYE", "🛍️ ESNAF ÇARŞISI", "💼 KARİYER", "🔑 YÖNETİM"])

# --- TAB 0: ŞEHİR NABZI ---
with tabs[0]:
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live = data_snap.to_dict() if data_snap.exists else {}
    except: live = {}

    st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <div class="quick-action" style="flex:1;">🕯️ Vefat</div>
        <div class="quick-action" style="flex:1;">💊 Eczane</div>
        <div class="quick-action" style="flex:1;">🔔 Duyuru</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f'<div class="official-card"><h4>🕯️ Vefat Haberleri</h4>{live.get("funeral", "*Güncel veri bekleniyor.*")}</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown(f'<div class="official-card"><h4>💊 Nöbetçi Eczaneler</h4>{live.get("pharmacy", "*Lütfen güncelleyin.*")}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="official-card"><h4>🔔 Güncel Duyuru & İhaleler</h4>{live.get("announcements", "*Yeni duyuru bulunamadı.*")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="official-card"><h4>📰 Belediye Haberleri</h4>{live.get("news", "*Haber akışı bekleniyor.*")}</div>', unsafe_allow_html=True)

# --- TAB 1: E-BELEDİYE (YENİ) ---
with tabs[1]:
    st.subheader("Hızlı Belediye İşlemleri")
    st.info("Bu bölüm sizi resmi 'dortyol.bel.tr' işlem sayfalarına yönlendirir.")
    
    e_cols = st.columns(2)
    with e_cols[0]:
        st.markdown('<div class="quick-action">💳 Vergi Ödeme (E-Belediye)</div>', unsafe_allow_html=True)
        st.markdown('<div class="quick-action">📜 Arsa Rayiç Sorgulama</div>', unsafe_allow_html=True)
    with e_cols[1]:
        st.markdown('<div class="quick-action">📝 Nikah Başvurusu</div>', unsafe_allow_html=True)
        st.markdown('<div class="quick-action">📂 Başvuru Takip</div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown('<div class="official-card"><h4>🏛️ Başkanın Mesajı</h4><p>"Dörtyolumuzu dijital çağın imkanlarıyla buluşturmaya devam ediyoruz. Bu portal, esnafımızla halkımızı bir araya getiren şehrimizin yeni vitrinidir."</p></div>', unsafe_allow_html=True)

# --- TAB 2: ESNAF ÇARŞISI ---
with tabs[2]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f"""
                <div class="official-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3>{s['ad']}</h3>
                        <span style="background:#003366; color:white; padding:4px 10px; border-radius:10px; font-size:0.7rem;">ESNAF</span>
                    </div>
                    <p>{s.get('sektor')} | Dörtyol Rehberi</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 Mağazayı İncele: {s['ad']}", key=f"v_{s['id']}"):
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
                st.markdown(f'<div class="official-card" style="display:flex; justify-content:space-between; border-top:none; border-left:5px solid #FF8C00;"><b>{p["ad"]}</b><b style="color:#003366;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 3: KARİYER ---
with tabs[3]:
    st.subheader("Dörtyol İstihdam Merkezi")
    k_tabs = st.tabs(["📢 Personel Alımları", "👤 Özgeçmiş (CV) Havuzu"])
    with k_tabs[0]:
        st.write("Dörtyol Belediyesi ve yerel esnafın aktif iş ilanları.")
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="official-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("Aktif ilan bulunamadı.")

# --- TAB 4: YÖNETİM ---
with tabs[4]:
    adm = st.text_input("Yönetici Yetkilendirme", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Resmi Yönetici Girişi Onaylandı.")
        
        st.subheader("🏛️ Belediye Veri Senkronizasyonu")
        st.info("Canlı verileri belediye sunucularından tazeleyin.")
        
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

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3;'>© {GUNCEL_YIL} Albayrax Municipality Pro v70</div>", unsafe_allow_html=True)
