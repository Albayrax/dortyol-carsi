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
    page_title="Dörtyol Çarşı | v68 The Town Hall",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- SECRETS KONTROLÜ (Gelişmiş Dedektör) ---
def find_api_key():
    key = st.secrets.get("gemini_api_key") or st.secrets.get("gemini-api-key")
    if key: return key
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
            fb_data = st.secrets["firebase"]["key"]
            key_dict = json.loads(fb_data) if isinstance(fb_data, str) else fb_data
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Hafıza Bağlantı Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. SMART AI ENGINE (GOOGLE SEARCH - VEFAT & PIYASA) ---
def get_live_info(query_type):
    if not apiKey:
        return "⚠️ API Anahtarı bulunamadı. Lütfen Secrets kısmını kontrol edin."

    queries = {
        "gold": "Bugün için güncel Çeyrek, Gram ve 22 Ayar Bilezik satış fiyatlarını Dörtyol/Hatay piyasasına göre listele.",
        "fuel": "Bugün Hatay Dörtyol'daki Shell, Petrol Ofisi ve BP güncel Benzin ve Motorin litre fiyatlarını ver.",
        "pharmacy": f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol ilçesindeki nöbetçi eczanelerin isim ve telefonlarını liste ver.",
        "funeral": f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol ilçesinde vefat edenlerin isimlerini, mahallelerini ve cenaze bilgilerini liste şeklinde ver."
    }

    user_query = queries.get(query_type, "")
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "Sen Dörtyol portal asistanısın. Bilgileri kısa, net ve tablo/liste şeklinde ver."}]}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Veri çekilemedi.")
        return f"⚠️ Google Hatası: {res.status_code}"
    except: return "⚠️ Bağlantı zaman aşımına uğradı."

# --- 4. TASARIM (MIRROR AI & OKUNABİLİRLİK) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, span, b, label { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    .glass-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(15px);
        padding: 22px;
        border-radius: 20px;
        border: 2px solid #001F3F;
        box-shadow: 10px 10px 0px #001F3F;
        margin-bottom: 20px;
    }
    .glass-card h3, .glass-card h4, .glass-card p, .glass-card b, .glass-card span { color: #001F3F !important; text-shadow: none !important; }
    .stButton>button { background-color: white !important; color: #001F3F !important; font-weight: 800 !important; border-radius: 12px !important; border: 3px solid #001F3F !important; height: 3.5rem; width: 100%; }
    .stButton>button:hover { background-color: #001F3F !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA SEEDER (DORU DOLU PAKET) ---
def seed_v68():
    if db:
        d_col = get_col("dukkanlar")
        shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?w=800", "icerik": "7/24 Güvenli Yakıt.", "tel":"0326", "tıklanma": 1550, "urunler": [{"ad": "Benzin 95", "fiyat": 60.50}]},
            {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?w=800", "icerik": "Tescilli Hatay Lezzeti.", "tel":"0532", "tıklanma": 3200, "urunler": [{"ad": "Kral Hasırı", "fiyat": 240.0}]}
        ]
        for s in shops: d_col.add(s)
        i_col = get_col("ilanlar")
        jobs = [{"baslik": "Usta Pideci", "isletme": "Meydan Fırını", "maas": "45.000 TL", "tel": "0326", "detay": "Tecrübeli usta aranıyor."}]
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

st.markdown('<h1 style="text-align:center; font-weight:900;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["📢 NABIZ & VEFAT", "🏛️ ÇARŞI", "💼 KARİYER MERKEZİ", "🔑 YÖNETİM"])

# --- TAB 0: NABIZ (VEFAT HABERLERİ) ---
with tabs[0]:
    st.subheader("Dörtyol'un Sesi (Vefat & Kesintiler)")
    try:
        data_snap = get_col("sistem_bilgi").document("canli").get()
        live_data = data_snap.to_dict() if data_snap.exists else {}
    except: live_data = {}

    if st.button("🕯️ BUGÜN VEFAT EDENLERİ ÇEK"):
        with st.spinner("Dörtyol kayıtları taranıyor..."):
            res = get_live_info("funeral")
            get_col("sistem_bilgi").document("canli").set({"funeral": res, "funeral_time": datetime.now()}, merge=True)
            st.rerun()
    
    st.markdown(f'<div class="glass-card"><h4>📋 Güncel Vefat Listesi</h4><p>{live_data.get("funeral", "Henüz veri çekilmedi. Butona basarak güncelleyin.")}</p></div>', unsafe_allow_html=True)

# --- TAB 1: ÇARŞI ---
with tabs[1]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f'<div class="glass-card"><h3>{s["ad"]}</h3><p>{s.get("sektor")} | Dörtyol</p></div>', unsafe_allow_html=True)
                if st.button(f"Mağazayı Gör: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.info("Veriler yükleniyor...")
    else:
        doc = get_col("dukkanlar").document(st.session_state.selected_shop_id).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            img_url = s.get('img')
            if img_url: st.image(img_url, use_container_width=True)
            st.title(s['ad'])
            st.divider()
            for p in s.get('urunler', []):
                st.markdown(f'<div class="glass-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 2: KARİYER MERKEZİ (Gelişmiş Filtreli CV) ---
with tabs[2]:
    k_tabs = st.tabs(["📢 İş İlanları", "👤 CV Bırak", "🔍 CV Bankası"])
    
    with k_tabs[0]:
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f'<div class="glass-card"><h4>{j["baslik"]}</h4><p>🏢 {j["isletme"]}<br>💰 Maaş: {j.get("maas","")}<br>📞 {j["tel"]}</p></div>', unsafe_allow_html=True)
        except: st.write("İlan bulunamadı.")

    with k_tabs[1]:
        st.subheader("İş Arayan Kaydı")
        with st.form("cv_kayit"):
            c_ad = st.text_input("Ad Soyad*")
            c_tur = st.selectbox("Aradığınız İş Türü", ["Tam Zamanlı", "Part-time (Verimli)", "Ek İş", "Öğrenci İşi"])
            c_uzm = st.text_input("Uzmanlık / İstediğiniz Pozisyon*")
            c_maas = st.text_input("Beklenen Ücret")
            c_tel = st.text_input("İletişim Numarası*")
            c_yazi = st.text_area("Kısa Özgeçmiş / Notlar")
            if st.form_submit_button("CV'Mİ KAYDET"):
                if c_ad and c_uzm and c_tel:
                    get_col("cvler").add({"ad": c_ad, "tur": c_tur, "uzm": c_uzm, "maas": c_maas, "tel": c_tel, "yazi": c_yazi, "tarih": datetime.now()})
                    st.success("CV'niz esnaflar için yayınlandı!")
                else: st.warning("Lütfen yıldızlı alanları doldurun.")

    with k_tabs[2]:
        f_tur = st.selectbox("İş Türüne Göre Filtrele", ["Hepsi", "Tam Zamanlı", "Part-time (Verimli)", "Ek İş", "Öğrenci İşi"])
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            if f_tur != "Hepsi": cvs = [c for c in cvs if c.get('tur') == f_tur]
            for c in cvs:
                st.markdown(f"""<div class="glass-card">
                    <b>👤 {c['ad']}</b> | <span style="color:blue;">{c.get('tur','')}</span><br>
                    🎯 Pozisyon: {c['uzm']}<br>
                    📞 {c['tel']}<br>
                    <p style="font-size:0.8rem; color:gray;">{c.get('yazi','')}</p>
                </div>""", unsafe_allow_html=True)
        except: st.write("CV bulunamadı.")

# --- TAB 3: ADMIN (İSTATİSTİK MERKEZİ) ---
with tabs[3]:
    adm = st.text_input("Yönetici Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı")
        
        # GİZLİ İSTATİSTİKLER BURADA
        st.markdown("### 📊 Portal İstatistikleri")
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Ziyaretçi", "13,420", "+120")
        col2.metric("Kayıtlı Esnaf", "152", "+3")
        col3.metric("Aktif İş İlanı", "34", "-2")

        st.divider()
        st.subheader("🛠️ Akıllı Veri Araçları")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("💊 Eczaneleri Güncelle"):
                res = get_live_info("pharmacy")
                get_col("sistem_bilgi").document("canli").set({"pharmacy": res}, merge=True); st.success("Eczaneler tazelendi!")
        with c2: 
            if st.button("⛽ Yakıtı Güncelle"):
                res = get_live_info("fuel")
                get_col("sistem_bilgi").document("canli").set({"fuel": res}, merge=True); st.success("Fiyatlar çekildi!")
        with c3: 
            if st.button("💰 Altın Güncelle"):
                res = get_live_info("gold")
                get_col("sistem_bilgi").document("canli").set({"gold": res}, merge=True); st.success("Altın piyasası okundu!")

        st.divider()
        if st.button("🚀 SİSTEMİ ÖRNEK VERİLERLE DOLDUR"):
            seed_v68()
            st.success("Hafıza başarıyla güncellendi!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax The Town Hall v68</div>", unsafe_allow_html=True)
