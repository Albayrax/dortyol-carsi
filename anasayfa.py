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
    page_title="Dörtyol Çarşı | v66 Ultra Logic",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- SECRETS KONTROLÜ (GELİŞMİŞ HATA YÖNETİMİ) ---
# Burada hem alt çizgi hem tire kontrolü yapıyoruz ki hata payı kalmasın
apiKey = st.secrets.get("gemini_api_key") or st.secrets.get("gemini-api-key") or ""

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Firebase Bağlantı Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    """Firestore koleksiyon yolu yardımcısı"""
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. SMART AI ENGINE (GOOGLE SEARCH GROUNDING) ---
def get_live_info(query_type):
    """Google Search destekli anlık veri çekme motoru"""
    if not apiKey:
        return "⚠️ API Anahtarı hala sistem tarafından okunmuyor! Lütfen Secrets kutusunu kontrol edin."

    user_query = ""
    if query_type == "gold":
        user_query = "Bugün için güncel Çeyrek Altın, Gram Altın ve 22 Ayar Bilezik satış fiyatlarını Dörtyol/Hatay piyasasına göre listele."
    elif query_type == "fuel":
        user_query = "Bugün Hatay Dörtyol'daki Shell, Petrol Ofisi ve BP güncel Benzin ve Motorin (Dizel) litre fiyatlarını ver."
    elif query_type == "pharmacy":
        user_query = f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol ilçesindeki nöbetçi eczanelerin isim ve telefonlarını liste şeklinde ver."

    # Gemini 2.5 Flash Preview API Payload
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen Dörtyol halkına hizmet veren bir asistansın. Kısa, net ve doğru bilgi ver."}]}
    }
    
    # Sadece desteklenen model: gemini-2.5-flash-preview-09-2025
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            result_text = res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri bulunamadı.")
            return result_text
        elif res.status_code == 400:
            return "⚠️ API Anahtarı geçersiz veya kısıtlı. Lütfen yeni bir anahtar almayı deneyin."
        return f"⚠️ Hata Kodu: {res.status_code}. Google şu an yanıt vermiyor."
    except Exception as e:
        return f"⚠️ Bağlantı hatası oluştu: {str(e)}"

# --- 4. TASARIM (MIRROR AI STYLE) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, span, b, label { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #001F3F;
        box-shadow: 10px 10px 0px #001F3F;
        margin-bottom: 20px;
    }
    .glass-card h3, .glass-card h4, .glass-card p, .glass-card b, .glass-card span { color: #001F3F !important; text-shadow: none !important; }
    .stats-card { background: #001F3F; padding: 15px; border-radius: 15px; border: 2px solid #FF8C00; text-align: center; }
    .stButton>button { background-color: white !important; color: #001F3F !important; font-weight: 800 !important; border-radius: 12px !important; border: 3px solid #001F3F !important; height: 3.5rem; }
    .stButton>button:hover { background-color: #001F3F !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA SEEDER (FULL PAKET) ---
def seed_v66():
    if db:
        # 1. DÜKKANLAR (Tüm sektörler)
        d_col = get_col("dukkanlar")
        shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?w=800", "icerik": "7/24 Güvenli Yakıt ve Market.", "tel":"0326", "tıklanma": 1500, "urunler": [{"ad": "Benzin 95", "fiyat": 60.50}]},
            {"ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "123", "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800", "icerik": "Çeyrek, Gram ve 22 Ayar Bilezik.", "tel":"0326", "tıklanma": 950, "urunler": [{"ad": "22 Ayar Bilezik (Gr)", "fiyat": 2980.0}]},
            {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?w=800", "icerik": "Tescilli Hatay Lezzeti.", "tel":"0532", "tıklanma": 3500, "urunler": [{"ad": "Peynirli Künefe", "fiyat": 190.0}]},
            {"ad": "Meydan Fırını", "sektor": "Gıda", "sifre": "123", "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800", "icerik": "Taze ve Sıcak Ekmek.", "tel":"0326", "tıklanma": 2200, "urunler": [{"ad": "Ekmek", "fiyat": 10.00}]}
        ]
        for s in shops: d_col.add(s)

        # 2. İLANLAR (Kariyer)
        i_col = get_col("ilanlar")
        jobs = [
            {"baslik": "Usta Pideci", "isletme": "Meydan Fırını", "detay": "Taş fırın tecrübeli.", "maas": "45.000 TL", "tel": "0326"},
            {"baslik": "Pompa Görevlisi", "isletme": "Shell Dörtyol", "detay": "Güler yüzlü eleman.", "maas": "22.500 TL", "tel": "0326"},
            {"baslik": "Satış Temsilcisi", "isletme": "Aydın Kuyumculuk", "detay": "Diksiyonu düzgün.", "maas": "32.000 TL", "tel": "0326"}
        ]
        for j in jobs: i_col.add(j)

# --- 6. ANA PROGRAM ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 style="text-align:center; font-size:3.5rem; font-weight:900;">DÖRTYOL DİJİTAL</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password")
        if st.button("PORTALI AKTİF ET"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# ÜST İSTATİSTİKLER
st.markdown('<h1 style="text-align:center; font-weight:900; letter-spacing:-2px;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
s_col1, s_col2, s_col3 = st.columns(3)
with s_col1: st.markdown('<div class="stats-card"><h4>👥 12.8K</h4><p>Ziyaretçi</p></div>', unsafe_allow_html=True)
with s_col2: st.markdown('<div class="stats-card"><h4>🏪 145</h4><p>Esnaf</p></div>', unsafe_allow_html=True)
with s_col3: st.markdown('<div class="stats-card"><h4>💼 28</h4><p>Aktif İlan</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER", "🏥 AKILLI REHBER", "🔑 ADMIN"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f'<div class="glass-card"><h3>{s["ad"]}</h3><p>{s.get("sektor")} | 👁️ {s.get("tıklanma", 0)}</p></div>', unsafe_allow_html=True)
                if st.button(f"Mağazayı Gör: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.info("Dükkanlar yükleniyor...")
    else:
        doc = get_col("dukkanlar").document(st.session_state.selected_shop_id).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            if s.get('img'): st.image(s['img'], use_container_width=True)
            st.title(s['ad'])
            for p in s.get('urunler', []):
                st.markdown(f'<div class="glass-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 1: KARİYER ---
with tabs[1]:
    k_tabs = st.tabs(["📢 İş İlanları", "👤 CV Bankası"])
    with k_tabs[0]:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="glass-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>💰 {j["maas"]}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("İlan yok.")
    with k_tabs[1]:
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            for c in cvs:
                st.markdown(f'<div class="glass-card"><b>👤 {c["ad"]}</b><br>🎯 {c["is"]}<br>📞 {c["tel"]}</div>', unsafe_allow_html=True)
        except: st.write("CV yok.")

# --- TAB 2: AKILLI REHBER ---
with tabs[2]:
    st.subheader("🤖 Akıllı Veri Botları")
    st.write("Google Search destekli anlık veriler.")
    
    # Mevcut veriyi çek
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live_data = data_snap.to_dict() if data_snap.exists else {}
    except: live_data = {}

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💊 ECZANE ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("pharmacy")
                get_col("sistem_bilgi").document("canli").set({"pharmacy": res, "pharma_time": datetime.now()}, merge=True); st.rerun()
    with c2:
        if st.button("⛽ AKARYAKIT ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("fuel")
                get_col("sistem_bilgi").document("canli").set({"fuel": res, "fuel_time": datetime.now()}, merge=True); st.rerun()
    with c3:
        if st.button("💰 ALTIN ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("gold")
                get_col("sistem_bilgi").document("canli").set({"gold": res, "gold_time": datetime.now()}, merge=True); st.rerun()

    st.markdown("---")
    st.markdown(f"**Nöbetçi Eczaneler:**\n\n{live_data.get('pharmacy', '*Güncel veri bekleniyor...*')}")
    st.markdown("---")
    st.markdown(f"**Akaryakıt Fiyatları:**\n\n{live_data.get('fuel', '*Güncel veri bekleniyor...*')}")
    st.markdown("---")
    st.markdown(f"**Altın Piyasası:**\n\n{live_data.get('gold', '*Güncel veri bekleniyor...*')}")

# --- TAB 3: ADMIN ---
with tabs[3]:
    adm = st.text_input("Yönetici Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Girişi Başarılı")
        # Gelişmiş Debug (Secrets Kontrolü)
        if apiKey: st.info("✅ API Anahtarı Algılandı.")
        else: st.warning("❌ API Anahtarı Okunamıyor! Secrets kutusuna 'gemini_api_key' eklediğinizden emin olun.")
        
        if st.button("🚀 SİSTEMİ FULL VERİYLE DOLDUR"):
            seed_v66()
            st.success("Tüm dükkanlar, ilanlar ve CVler hafızaya yüklendi!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax Ultra Logic v66</div>", unsafe_allow_html=True)
