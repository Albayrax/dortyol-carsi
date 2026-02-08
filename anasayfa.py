import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | 2026 Logic Core",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        pass

db = firestore.client() if firebase_admin._apps else None

# --- FIREBASE HELPERS ---
def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- CSS: SADE VE İŞLEVSEL (TASARIM DEĞİL, YAPI) ---
st.markdown("""
    <style>
    .stApp { background-color: #F5F5F7; }
    .main-title { font-weight: 900; color: #1D1D1F; text-align: center; margin-top: -50px; }
    .feature-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #DDD; margin-bottom: 10px; }
    .stats-box { background: #001F3F; color: #FF8C00 !important; padding: 15px; border-radius: 10px; text-align: center; }
    .job-badge { background: #E1F5FE; color: #01579B !important; padding: 4px 8px; border-radius: 5px; font-size: 0.7rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
    pwd = st.text_input("Giriş Kodu", type="password")
    if st.button("SİSTEME GİR"):
        if pwd == SITE_GIRIS_SIFRESI:
            st.session_state.is_site_unlocked = True
            st.rerun()
    st.stop()

# --- VERİ ÇEKME ---
all_shops = []
try:
    shops_docs = get_col("dukkanlar").stream()
    all_shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_docs]
except: pass

# --- ANA EKRAN ---
st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 İŞ İLANLARI", "🎟️ KUPONLAR", "🔐 ESNAF", "🔑 ADM"])

# --- TAB 1: ÇARŞI (ESNAF LİSTESİ) ---
with tabs[0]:
    if st.session_state.selected_shop_id is None:
        search = st.text_input("🔍 Dükkan veya Hizmet Ara...")
        filtered = [s for s in all_shops if search.lower() in s.get('ad','').lower()]
        for s in filtered:
            with st.container():
                st.markdown(f"""
                <div class="feature-card">
                    <h3 style="margin:0;">{s['ad']}</h3>
                    <p style="font-size:0.8rem; color:gray;">👁️ {s.get('tıklanma', 0)} kişi inceledi</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Detayı Gör: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
    else:
        # DETAY SAYFASI
        sid = st.session_state.selected_shop_id
        shop = next((s for s in all_shops if s['id'] == sid), None)
        if st.button("⬅️ Geri"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.title(shop['ad'])
            st.info(f"📞 WhatsApp: {shop.get('tel',' Belirtilmedi')}")
            st.write(shop.get('icerik', 'Açıklama yok.'))
            st.subheader("Ürünler")
            for p in shop.get('urunler', []):
                st.write(f"✅ {p['ad']} - **{p['fiyat']} ₺**")

# --- TAB 2: İŞ İLANLARI (YENİ - PARA KAZANDIRIR) ---
with tabs[1]:
    st.subheader("Dörtyol İş Dünyası")
    st.write("Esnafımız eleman arıyor, gençler iş buluyor.")
    
    # İş İlanlarını Çek
    try:
        jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
        for job in jobs:
            st.markdown(f"""
            <div class="feature-card">
                <span class="job-badge">{job.get('tip', 'Tam Zamanlı')}</span>
                <h4 style="margin:5px 0;">{job.get('baslik')}</h4>
                <p style="font-size:0.9rem;">🏢 {job.get('isletme')}</p>
                <p style="font-size:0.8rem; color:gray;">📞 İletişim: {job.get('tel')}</p>
            </div>
            """, unsafe_allow_html=True)
    except: st.info("Henüz ilan yok.")

# --- TAB 3: KUPONLAR (YENİ - REKABET) ---
with tabs[2]:
    st.subheader("Dörtyol İndirim Kodları")
    st.write("Sadece bu portal kullanıcılarına özel fırsatlar.")
    st.warning("Bu kodları dükkanda söyleyerek indiriminizi alın!")
    
    st.markdown("""
    <div class="feature-card" style="border-left: 5px solid #FF8C00;">
        <h4>ANTİK KRAL KÜNEFE</h4>
        <p>Kod: <b>KRAL31</b></p>
        <p>Fırsat: Künefe yanında dondurma bedava!</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 4: ESNAF PANELİ (ANALİZLİ) ---
with tabs[3]:
    if st.session_state.owner_shop_id is None:
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("PANELE GİR"):
            match = next((s for s in all_shops if s.get('ad') == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match['id']; st.rerun()
    else:
        sid = st.session_state.owner_shop_id
        s_data = next((s for s in all_shops if s['id'] == sid), None)
        st.success(f"Hoş geldin {s_data['ad']}")
        
        # --- ANALİZ KISMI (BU ESNAFI SİTEYE BAĞLAR) ---
        col1, col2 = st.columns(2)
        col1.markdown(f"""<div class="stats-box"><h3>{s_data.get('tıklanma', 0)}</h3><p>Toplam Görüntülenme</p></div>""", unsafe_allow_html=True)
        col2.markdown(f"""<div class="stats-box"><h3>{len(s_data.get('urunler', []))}</h3><p>Aktif Ürün Sayısı</p></div>""", unsafe_allow_html=True)
        
        with st.expander("💼 İş İlanı Ver"):
            j_t = st.text_input("Aranan Pozisyon (Örn: Garson)")
            j_n = st.text_input("İletişim Numarası")
            if st.button("İLAN YAYINLA"):
                get_col("ilanlar").add({"baslik": j_t, "isletme": s_data['ad'], "tel": j_n, "tarih": datetime.now()})
                st.success("İlan Çarşı Meydanında Yayında!")
        
        if st.button("Çıkış Yap"): st.session_state.owner_shop_id = None; st.rerun()

# --- TAB 5: ADMİN ---
with tabs[4]:
    adm_pwd = st.text_input("Admin", type="password")
    if adm_pwd == ADMIN_SIFRE:
        st.write("Tüm sistem kontrolün altında.")
        for d in all_shops:
            st.write(f"Dükkan: {d['ad']} | Şifre: {d.get('sifre')}")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3;'>© {GUNCEL_YIL} Albayrax Power Logic v52</div>", unsafe_allow_html=True)
