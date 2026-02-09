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
    page_title="Dörtyol Portal | v64 Elite & Smart",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# API Anahtarı Streamlit Secrets'tan çekilir
# Dashboard -> Settings -> Secrets -> gemini_api_key = "..."
apiKey = st.secrets.get("gemini_api_key", "")

MAHALLELER = ["Tümü", "Numuneevler", "Çaylı", "Ocaklı", "Yeşilköy", "Kuzuculu", "Yeniyurt", "Altınçağ", "Özerli", "Sanayi"]
KATEGORILER = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Gıda", "Hizmet", "Teknoloji", "Kuyumcu", "Mobilya"]

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

# --- 3. AKILLI AI MOTORU (SPESİFİK SEKTÖRLER İÇİN) ---
def get_ai_niche_data(niche_type):
    """Sadece hareketli sektörler için anlık veri çeker"""
    if not apiKey: return "⚠️ API Anahtarı bağlı değil."
    
    prompt = ""
    if niche_type == "gold":
        prompt = "Bugün için güncel Gram Altın, Çeyrek Altın ve 22 Ayar bilezik alış-satış fiyatlarını kısa bir liste olarak ver."
    elif niche_type == "fuel":
        prompt = "Bugün Hatay Dörtyol'daki güncel Benzin ve Motorin litre fiyatlarını (EPDK verilerine yakın) ver."
    elif niche_type == "pharmacy":
        prompt = f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol'daki nöbetçi eczaneleri listele."

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri çekilemedi.")
        return "Limit dolmuş olabilir, lütfen daha sonra deneyin."
    except: return "Bağlantı hatası."

# --- 4. GÖRSEL TASARIM ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, span, b, label { 
        color: white !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        font-family: 'Inter', sans-serif;
    }
    .welcome-banner {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200');
        background-size: cover;
        background-position: center;
        padding: 60px 20px;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 30px;
        border: 2px solid white;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }
    .content-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #001F3F;
        box-shadow: 8px 8px 0px #001F3F;
        margin-bottom: 20px;
    }
    .content-card h3, .content-card h4, .content-card p, .content-card b, .content-card span {
        color: #001F3F !important;
        text-shadow: none !important;
    }
    .news-badge {
        padding: 4px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 900; text-transform: uppercase;
    }
    .badge-vefat { background: #001F3F; color: white !important; }
    .badge-indirim { background: #2E7D32; color: white !important; }
    .stButton>button {
        background-color: white !important;
        color: #001F3F !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: 3px solid #001F3F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GİRİŞ VE ANA MANTIK ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<div class="welcome-banner"><h1>DÖRTYOL PORTALI\'NA<br>HOŞ GELDİNİZ</h1><p>Şehrin En Akıllı Dijital Rehberi</p></div>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password")
        if st.button("PORTALI AKTİF ET"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<div style="text-align:center; padding: 20px 0;"><h1 style="font-size:3.5rem; font-weight:900; margin-bottom:0;">DÖRTYOL PORTAL</h1><p style="opacity:0.8;">Gerçek Veri, Gerçek Esnaf, Gerçek Dörtyol</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["📢 NABIZ", "🏛️ ÇARŞI", "🏆 SKOR", "💼 KARİYER", "🔑 ADMIN"])

# --- TAB 0: NABIZ (SEKTÖR VE MAHALLE FİLTRELİ) ---
with tabs[0]:
    st.markdown('<div class="pulse-card" style="padding:10px; border-radius:15px; background:rgba(255,255,255,0.1);">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    m_fil = c1.selectbox("📍 Mahalle", MAHALLELER)
    s_fil = c2.selectbox("🏢 Sektör", KATEGORILER)
    t_fil = c3.selectbox("📰 Haber Tipi", ["Tümü", "vefat", "kesinti", "indirim"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Haberleri Çek ve Filtrele
    try:
        query = get_col("haberler").order_by("tarih", direction="DESCENDING").limit(20).stream()
        docs = [d.to_dict() for d in query]
        if m_fil != "Tümü": docs = [d for d in docs if d.get('mahalle') == m_fil]
        if s_fil != "Tümü": docs = [d for d in docs if d.get('sektor') == s_fil]
        if t_fil != "Tümü": docs = [d for d in docs if d.get('tip') == t_fil]
        
        if not docs: st.info(f"Seçilen kriterlere göre güncel bir haber bulunamadı.")
        for d in docs:
            st.markdown(f"""
            <div class="content-card">
                <span class="news-badge badge-{d.get('tip','vefat')}">{d.get('tip','duyuru')}</span>
                <small style="float:right; color:gray;">{d['tarih'].strftime('%d.%m.%Y')}</small>
                <h4>{d['baslik']}</h4>
                <p style="font-size:0.8rem; margin:0;">📍 {d.get('mahalle')} | 🏢 {d.get('sektor','Genel')}</p>
                <p style="margin-top:10px;">{d['detay']}</p>
            </div>
            """, unsafe_allow_html=True)
    except: st.write("Haberler yükleniyor...")

# --- TAB 1: ÇARŞI (SEKTÖREL DÜKKANLAR) ---
with tabs[1]:
    if st.session_state.selected_shop_id is None:
        c_search = st.selectbox("Sektöre Göz Atın:", KATEGORILER)
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            if c_search != "Tümü": shops = [s for s in shops if s.get('sektor') == c_search]
            
            # Premiumları öne çıkar
            shops = sorted(shops, key=lambda x: x.get('is_premium', False), reverse=True)
            
            for s in shops:
                premium_style = "border: 4px solid #FFD700;" if s.get('is_premium') else ""
                st.markdown(f"""
                <div class="content-card" style="{premium_style}">
                    <h3 style="margin:0;">{s['ad']} {'⭐' if s.get('is_premium') else ''}</h3>
                    <p style="margin:0; font-size:0.8rem; color:gray;">{s.get('sektor')} | 👁️ {s.get('tıklanma', 0)} Kişi Baktı</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 Dükkana Gir: {s['ad']}", key=f"btn_s_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.write("Yükleniyor...")
    else:
        # DETAY
        sid = st.session_state.selected_shop_id
        doc = get_col("dukkanlar").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Geri"): st.session_state.selected_shop_id = None; st.rerun()
            st.title(s['ad'])
            for p in s.get('urunler', []):
                st.markdown(f'<div class="content-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 4: ADMIN (AKILLI GÜNCELLEME) ---
with tabs[4]:
    adm = st.text_input("Yönetici Paneli", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı.")
        
        st.write("### 🤖 Akıllı Veri Botları")
        st.info("Bu butonlar Google Search üzerinden en güncel Dörtyol verilerini çeker. Gereksiz kullanmayın (Limit Dostu).")
        
        c_up1, c_up2, c_up3 = st.columns(3)
        if c_up1.button("💰 ALTIN FİYATI ÇEK"):
            with st.spinner("Piyasa taranıyor..."):
                res = get_ai_niche_data("gold")
                get_col("haberler").add({"tip": "indirim", "mahalle": "Tümü", "sektor": "Kuyumcu", "baslik": "Güncel Altın Piyasası", "detay": res, "tarih": datetime.now()})
                st.success("Altın fiyatları Nabız'a eklendi!")
        
        if c_up2.button("⛽ BENZİN FİYATI ÇEK"):
            with st.spinner("EPDK taranıyor..."):
                res = get_ai_niche_data("fuel")
                get_col("haberler").add({"tip": "duyuru", "mahalle": "Tümü", "sektor": "Ulaşım", "baslik": "Akaryakıt Durumu", "detay": res, "tarih": datetime.now()})
                st.success("Fiyatlar güncellendi!")
        
        if c_up3.button("🚑 ECZANELERİ ÇEK"):
            with st.spinner("Nöbetçiler aranıyor..."):
                res = get_ai_niche_data("pharmacy")
                get_col("haberler").add({"tip": "duyuru", "mahalle": "Tümü", "baslik": "Nöbetçi Eczaneler", "detay": res, "tarih": datetime.now()})
                st.success("Eczane listesi yayında!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax Elite & Smart v64</div>", unsafe_allow_html=True)
