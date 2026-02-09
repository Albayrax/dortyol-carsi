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
    page_title="Dörtyol Çarşı | v67 Ultra Resilience",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- SECRETS KONTROLÜ (ULTRA ESNEK DEDEKTÖR) ---
def find_api_key():
    # 1. Ana seviyede ara
    key = st.secrets.get("gemini_api_key") or st.secrets.get("gemini-api-key")
    if key: return key
    
    # 2. Firebase bloğunun içine yanlışlıkla yazıldıysa oradan çek
    fb = st.secrets.get("firebase")
    if isinstance(fb, dict):
        key = fb.get("gemini_api_key") or fb.get("gemini-api-key")
        if key: return key
    
    return ""

apiKey = find_api_key()

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            # key verisi string mi yoksa direkt dict mi kontrol et
            fb_data = st.secrets["firebase"]["key"]
            if isinstance(fb_data, str):
                key_dict = json.loads(fb_data)
            else:
                key_dict = fb_data # Bazı durumlarda dict olarak gelir
            
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Firebase Bağlantı Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. SMART AI ENGINE ---
def get_live_info(query_type):
    if not apiKey:
        return "⚠️ API Anahtarı bulunamadı."

    user_query = ""
    if query_type == "gold":
        user_query = "Bugün için güncel Çeyrek Altın, Gram Altın ve 22 Ayar Bilezik satış fiyatlarını Dörtyol/Hatay piyasasına göre listele."
    elif query_type == "fuel":
        user_query = "Bugün Hatay Dörtyol'daki Shell, Petrol Ofisi ve BP güncel Benzin ve Motorin (Dizel) litre fiyatlarını ver."
    elif query_type == "pharmacy":
        user_query = f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol ilçesindeki nöbetçi eczanelerin isim ve telefonlarını liste şeklinde ver."

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri bulunamadı.")
        return f"⚠️ Hata: {res.status_code}"
    except: return "⚠️ Bağlantı hatası."

# --- 4. TASARIM ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%); background-image: url('https://www.transparenttextures.com/patterns/cubes.png'); background-attachment: fixed; }
    h1, h2, h3, h4, p, span, b, label { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    .glass-card { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(15px); padding: 20px; border-radius: 20px; border: 2px solid #001F3F; box-shadow: 10px 10px 0px #001F3F; margin-bottom: 20px; }
    .glass-card h3, .glass-card h4, .glass-card p, .glass-card b, .glass-card span { color: #001F3F !important; text-shadow: none !important; }
    .stats-card { background: #001F3F; padding: 15px; border-radius: 15px; border: 2px solid #FF8C00; text-align: center; }
    .stButton>button { background-color: white !important; color: #001F3F !important; font-weight: 800 !important; border-radius: 12px !important; border: 3px solid #001F3F !important; height: 3.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA SEEDER ---
def seed_v67():
    if db:
        d_col = get_col("dukkanlar")
        shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?w=800", "icerik": "7/24 Güvenli Yakıt.", "tel":"0326", "tıklanma": 1550, "urunler": [{"ad": "Benzin 95", "fiyat": 60.50}]},
            {"ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "123", "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800", "icerik": "Altın ve Mücevher.", "tel":"0326", "tıklanma": 980, "urunler": [{"ad": "Gram Altın", "fiyat": 3150.0}]},
            {"ad": "Meydan Fırını", "sektor": "Gıda", "sifre": "123", "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800", "icerik": "Sıcak Ekmek.", "tel":"0326", "tıklanma": 2250, "urunler": [{"ad": "Ekmek", "fiyat": 10.00}]}
        ]
        for s in shops: d_col.add(s)

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

st.markdown('<h1 style="text-align:center; font-weight:900;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
s_col1, s_col2, s_col3 = st.columns(3)
with s_col1: st.markdown('<div class="stats-card"><h4>👥 13.1K</h4><p>Ziyaretçi</p></div>', unsafe_allow_html=True)
with s_col2: st.markdown('<div class="stats-card"><h4>🏪 148</h4><p>Esnaf</p></div>', unsafe_allow_html=True)
with s_col3: st.markdown('<div class="stats-card"><h4>💼 32</h4><p>Aktif İlan</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER", "🏥 AKILLI REHBER", "🔑 ADMIN"])

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

with tabs[1]:
    k_tabs = st.tabs(["📢 İş İlanları", "👤 CV Bankası"])
    with k_tabs[0]:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="glass-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>💰 {j["maas"]}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("İlan yok.")

with tabs[2]:
    st.subheader("🤖 Akıllı Veri Botları")
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live_data = data_snap.to_dict() if data_snap.exists else {}
    except: live_data = {}

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💊 ECZANE ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("pharmacy")
                get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.rerun()
    with c2:
        if st.button("⛽ AKARYAKIT ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("fuel")
                get_col("sistem_bilgi").document("canli").set({"fuel": res}, merge=True); st.rerun()
    with c3:
        if st.button("💰 ALTIN ÇEK"):
            with st.spinner("Taranıyor..."):
                res = get_live_info("gold")
                get_col("sistem_bilgi").document("canli").set({"gold": res}, merge=True); st.rerun()

    st.markdown("---")
    st.markdown(f"**Nöbetçi Eczaneler:**\n\n{live_data.get('pharmacy', '*Veri bekleniyor...*')}")
    st.markdown(f"**Akaryakıt Fiyatları:**\n\n{live_data.get('fuel', '*Veri bekleniyor...*')}")
    st.markdown(f"**Altın Piyasası:**\n\n{live_data.get('gold', '*Veri bekleniyor...*')}")

with tabs[3]:
    adm = st.text_input("Yönetici Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Girişi Başarılı")
        
        # --- TEKNİK TANI ARAÇLARI ---
        st.write("🔍 **Sistem Tanı Aracı**")
        all_keys = list(st.secrets.keys())
        st.write(f"Tespit Edilen Anahtar Grupları: `{all_keys}`")
        
        if "firebase" in st.secrets:
            fb_subkeys = list(st.secrets["firebase"].keys())
            st.write(f"Firebase İçindeki Alt Anahtarlar: `{fb_subkeys}`")
        
        if apiKey:
            st.info(f"✅ API Anahtarı aktif. (İlk 5 hane: `{apiKey[:5]}...`)")
        else:
            st.warning("❌ API Anahtarı hiçbir yerde bulunamadı!")
            st.write("Öneri: Secrets kutusuna gidin ve `gemini_api_key = \"...\"` satırını en üste, yani `[firebase]` yazısından daha yukarıya taşıyın.")
        
        if st.button("🚀 SİSTEMİ FULL VERİYLE DOLDUR"):
            seed_v67()
            st.success("Hafıza başarıyla dolduruldu!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax Ultra Resilience v67</div>", unsafe_allow_html=True)
