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
    page_title="Dörtyol Portal | v63 Elite Empire",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

MAHALLELER = ["Tümü", "Numuneevler", "Çaylı", "Ocaklı", "Yeşilköy", "Kuzuculu", "Yeniyurt", "Altınçağ", "Özerli", "Sanayi"]
KATEGORILER = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Gıda", "Hizmet", "Teknoloji"]

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

# --- 3. GÖRSEL TASARIM (MIRROR AI STYLE) ---
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
    .premium-border { border: 4px solid #FFD700 !important; box-shadow: 8px 8px 0px #FFD700 !important; }
    .stButton>button {
        background-color: white !important;
        color: #001F3F !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: 3px solid #001F3F !important;
        width: 100%;
    }
    .news-badge {
        padding: 4px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 900; text-transform: uppercase;
    }
    .badge-vefat { background: #001F3F; color: white !important; }
    .badge-indirim { background: #2E7D32; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SİSTEM BAŞLATICI (MANDATORY DATA) ---
def seed_v63():
    if db:
        # 1. DÜKKANLAR (EKMEK FİYATI GÜNCELLENDİ)
        d_col = get_col("dukkanlar")
        shops = [
            {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "img": "https://images.unsplash.com/photo-1621230181431-7e8790089851?w=800", "icerik": "7/24 Güvenli Yakıt", "is_premium": True, "tıklanma": 1250, "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}]},
            {"ad": "Meydan Fırını", "sektor": "Gıda", "sifre": "123", "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800", "icerik": "Sıcak Taş Fırın Ekmeği", "is_premium": False, "tıklanma": 800, "urunler": [{"ad": "Ekmek", "fiyat": 15.00}]},
            {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?w=800", "icerik": "Tescilli Hatay Lezzeti", "is_premium": True, "tıklanma": 3400, "urunler": [{"ad": "Kral Hasırı", "fiyat": 280.0}]}
        ]
        for s in shops: d_col.add(s)
        # 2. NABIZ (MAHALLE BAZLI BOŞLUKLAR DOLUYOR)
        n_col = get_col("haberler")
        notices = [
            {"tip": "vefat", "baslik": "Vefat Haberi", "mahalle": "Numuneevler", "detay": "Salih Yılmaz vefat etmiştir.", "tarih": datetime.now()},
            {"tip": "kesinti", "baslik": "Sanayi Elektrik Kesintisi", "mahalle": "Sanayi", "detay": "Bakım çalışması nedeniyle akşam kesinti olacaktır.", "tarih": datetime.now()},
            {"tip": "indirim", "baslik": "Altınçağ Market Fırsatı", "mahalle": "Altınçağ", "detay": "Tüm deterjanlarda %30 indirim.", "tarih": datetime.now()}
        ]
        for n in notices: n_col.add(n)

# --- 5. ANA MANTIK VE GİRİŞ ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 style="text-align:center; font-size:3rem; font-weight:900;">DÖRTYOL DİJİTAL</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 3, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password")
        if st.button("PORTALI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 style="text-align:center; font-weight:900; letter-spacing:-2px;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["📢 NABIZ", "🏛️ ÇARŞI", "🏆 SKOR TABLOSU", "💼 KARİYER", "🔑 ADMIN"])

# --- TAB 0: NABIZ (MAHALLE ODAKLI) ---
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    m_filtre = col1.selectbox("Kendi Mahallenizi Seçin:", MAHALLELER)
    t_filtre = col2.selectbox("Tip:", ["Tümü", "vefat", "kesinti", "indirim"])
    
    try:
        query = get_col("haberler").order_by("tarih", direction="DESCENDING").limit(20).stream()
        docs = [d.to_dict() for d in query]
        
        if m_filtre != "Tümü": docs = [d for d in docs if d.get('mahalle') == m_filtre]
        if t_filtre != "Tümü": docs = [d for d in docs if d.get('tip') == t_filtre]
        
        if not docs: st.info(f"{m_filtre} mahallesinde şu an güncel bir olay bulunmuyor.")
        for d in docs:
            st.markdown(f"""
            <div class="content-card">
                <span class="news-badge badge-{d.get('tip','vefat')}">{d.get('tip','duyuru')}</span>
                <small style="float:right; color:gray;">{d['tarih'].strftime('%d.%m.%Y')}</small>
                <h4 style="margin:5px 0;">{d['baslik']}</h4>
                <p>📍 <b>Mahalle:</b> {d.get('mahalle')} | {d['detay']}</p>
            </div>
            """, unsafe_allow_html=True)
    except: st.info("Haberler yükleniyor...")

# --- TAB 1: ÇARŞI (KATEGORİ & PREMİUM) ---
with tabs[1]:
    if st.session_state.selected_shop_id is None:
        c_filtre = st.selectbox("Sektör Seçin:", KATEGORILER)
        search = st.text_input("🔍 Mağaza Ara...")
        
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            if c_filtre != "Tümü": shops = [s for s in shops if s.get('sektor') == c_filtre]
            if search: shops = [s for s in shops if search.lower() in s.get('ad','').lower()]
            
            # Premiumları En Üste Al
            shops = sorted(shops, key=lambda x: x.get('is_premium', False), reverse=True)
            
            for s in shops:
                p_class = "premium-border" if s.get('is_premium') else ""
                st.markdown(f"""
                <div class="content-card {p_class}">
                    <h3 style="margin:0;">{s['ad']} {'⭐' if s.get('is_premium') else ''}</h3>
                    <p style="margin:5px 0; font-size:0.8rem; color:gray;">{s.get('sektor')} | 👁️ {s.get('tıklanma', 0)} Görüntülenme</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 Mağazayı Gez: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        except: st.write("Yükleniyor...")
    else:
        # DETAY SAYFASI
        doc = get_col("dukkanlar").document(st.session_state.selected_shop_id).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            if s.get('img'): st.image(s['img'], use_container_width=True)
            st.title(s['ad'])
            for p in s.get('urunler', []):
                st.markdown(f'<div class="content-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 2: SKOR TABLOSU (LEADERBOARD) ---
with tabs[2]:
    st.subheader("🏆 Dörtyol Esnaf Liderleri")
    s_tab = st.selectbox("Sektöre Göre Sırala:", KATEGORILER[1:])
    try:
        all_s = [doc.to_dict() for doc in get_col("dukkanlar").stream()]
        filtered_s = [s for s in all_s if s.get('sektor') == s_tab]
        sorted_s = sorted(filtered_s, key=lambda x: x.get('tıklanma', 0), reverse=True)
        
        for i, s in enumerate(sorted_s[:10]):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"""
            <div class="content-card" style="display:flex; justify-content:space-between; align-items:center;">
                <b>{medal} {s['ad']}</b>
                <span>{s.get('tıklanma', 0)} İlgi Skoru</span>
            </div>
            """, unsafe_allow_html=True)
    except: pass

# --- TAB 3: KARİYER (EŞLEŞTİRME MANTIĞI) ---
with tabs[3]:
    k_mode = st.radio("", ["İş İlanları", "CV Bankası"], horizontal=True)
    if k_mode == "İş İlanları":
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in jobs:
                st.markdown(f"""<div class="content-card"><h4>{j['baslik']}</h4><p>🏢 {j['isletme']}<br>🎯 Aranan: {j.get('detay','')}</p></div>""", unsafe_allow_html=True)
        except: st.write("İlan yok.")
    else:
        st.write("Dörtyol CV Havuzu")
        with st.form("cv_v63"):
            c_ad = st.text_input("Ad Soyad")
            c_uz = st.text_input("Uzmanlık (Usta, Şoför, Kasiyer vb.)")
            c_te = st.text_input("Telefon")
            if st.form_submit_button("CV'mi Yayınla (Elite Üyelik Gerekebilir)"):
                get_col("cvler").add({"ad": c_ad, "is": c_uz, "tel": c_te, "tarih": datetime.now()})
                st.success("CV'niz sisteme işlendi!")

# --- TAB 4: ADMIN (ANALYTICS & CONTROL) ---
with tabs[4]:
    adm = st.text_input("Yönetici", type="password")
    if adm == ADMIN_SIFRE:
        st.write("📊 **Dükkan Performans Analizi**")
        try:
            perf = [doc.to_dict() for doc in get_col("dukkanlar").stream()]
            for p in perf:
                intent_score = (p.get('tıklanma', 0) * 1.2) # Basit bir niyet simülasyonu
                st.write(f"🏢 {p['ad']} | Tıklanma: {p.get('tıklanma')} | Tahmini Alım Niyeti: %{min(100, int(intent_score/10))}")
        except: pass
        
        if st.button("🚀 SİSTEMİ 2026 VERİLERİYLE GÜNCELLE"):
            seed_v63()
            st.success("Tüm mahalleler ve güncel fiyatlar yüklendi!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; color:white;'>© {GUNCEL_YIL} Albayrax Elite Empire v63</div>", unsafe_allow_html=True)
