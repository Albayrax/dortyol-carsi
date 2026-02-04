import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI (PORTAL READY) ---
st.set_page_config(
    page_title="Dörtyol Çarşı 2026 | Esnaf Portalı",
    page_icon="🍊",
    layout="wide",
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
            firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Sistem Bağlantı Hatası: {e}")

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'is_admin': False,
    'owner_shop_id': None,
    'selected_cat': "Tümü",
    'selected_id': None,
    'sort_filter': "Puan (Yüksek)"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            if st.session_state.sort_filter == "Puan (Yüksek)":
                return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
            elif st.session_state.sort_filter == "En Çok İncelenen":
                return sorted(data, key=lambda x: x.get('tıklanma', 0), reverse=True)
            return data
        except: return []
    return []

# --- PORTAL UI & SAHİBİNDEN STYLE (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    /* Global Stil */
    .stApp {{
        background-color: #050505;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Hero & Login Section (Sea View Background) */
    .hero-login {{
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920");
        background-size: cover;
        background-position: center;
        height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-bottom: 3px solid #ffcc00;
        margin-top: -110px;
        text-align: center;
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(255, 204, 0, 0.3);
        width: 350px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }}

    /* Başlık */
    .portal-title {{
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        color: #ffcc00;
        letter-spacing: 15px;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
    }}

    /* Kategori Kartları (Sahibinden Style) */
    .category-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 20px;
        padding: 40px 0;
    }}

    .category-card {{
        background: #111;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border: 1px solid #222;
        transition: 0.3s;
        cursor: pointer;
    }}

    .category-card:hover {{
        border: 1px solid #ffcc00;
        background: #1a1a1a;
        transform: translateY(-5px);
    }}

    .category-icon {{
        font-size: 2.5rem;
        margin-bottom: 15px;
        display: block;
    }}

    /* Dükkan Kartları */
    .shop-portal-card {{
        background: #111;
        border-radius: 20px;
        border-left: 5px solid #ffcc00;
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
    }}

    .shop-portal-card:hover {{
        background: #181818;
        padding-left: 30px;
    }}

    /* Butonlar */
    .stButton>button {{
        background: #ffcc00 !important;
        color: black !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HERO & LOGIN SECTION ---
if not st.session_state.is_site_unlocked:
    st.markdown(f"""
        <div class="hero-login">
            <h1 class="portal-title">DÖRTYOL ÇARŞI</h1>
            <p style="letter-spacing:3px; color:#ddd; margin-bottom:20px;">2026 ELİTE ESNAF PORTALI</p>
            <div class="login-card">
                <p style="font-size:0.8rem; color:#aaa; margin-bottom:15px;">Lütfen giriş anahtarını yazın</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([2, 1, 2])
    with col_login:
        key_input = st.text_input("", type="password", placeholder="Anahtar Kodu...")
        if st.button("PORTALA GİRİŞ YAP"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else:
                st.error("Anahtar hatalı.")
    st.stop()

# --- ANA PORTAL İÇERİĞİ ---

st.markdown("""
    <div style="text-align:center; padding: 40px 0; border-bottom: 1px solid #222;">
        <h1 style="font-family:'Cinzel', serif; color:#ffcc00; letter-spacing:10px;">DÖRTYOL PORTAL</h1>
    </div>
""", unsafe_allow_html=True)

# ARAMA ÇUBUĞU
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_q = st.text_input("", placeholder="🔍 Dükkan, hizmet veya ürün ara...", key="portal_search")

# SEKMELER
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# KATEGORİLER (YENİ SİSTEM)
kategoriler = [
    {"ad": "Tümü", "ikon": "🌐", "renk": "#ffcc00"},
    {"ad": "Tatlıcı", "ikon": "🍯", "renk": "#ffa500"},
    {"ad": "Kebapçı", "ikon": "🔥", "renk": "#ff4500"},
    {"ad": "Sağlık", "ikon": "🏥", "renk": "#00ffcc"}, # Eczane / Klinik
    {"ad": "Ulaşım", "ikon": "🚗", "renk": "#ffffff"}, # Otomotiv / Transfer
    {"ad": "Hizmet", "ikon": "🛠️", "renk": "#aaaaaa"}, # Hırdavat / Tamir
    {"ad": "Yatırım", "ikon": "💎", "renk": "#d4af37"}, # Emlak / Kuyumcu
    {"ad": "Giyim", "ikon": "👕", "renk": "#ff66cc"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # KATEGORİ GRID
    st.markdown("### 🏷️ Sektör Seçin")
    cols = st.columns(len(kategoriler))
    for i, cat in enumerate(kategoriler):
        with cols[i]:
            active = st.session_state.selected_cat == cat['ad']
            st.markdown(f"""
                <div style="text-align:center; padding:15px; border-radius:15px; background:{'#222' if active else '#111'}; border: 1px solid {'#ffcc00' if active else '#222'};">
                    <span style="font-size:2rem;">{cat['ikon']}</span>
                    <p style="font-size:0.7rem; font-weight:700; color:{cat['renk']};">{cat['ad'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Seç", key=f"btn_{cat['ad']}"):
                st.session_state.selected_cat = cat['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME
    if st.session_state.selected_id is None:
        all_data = verileri_yukle()
        filtered = [d for d in all_data if (search_q.lower() in d['ad'].lower() or search_q.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        if not filtered:
            st.info("Bu sektörde henüz kayıtlı dükkan bulunmuyor.")
        
        for d in filtered:
            st.markdown(f"""
            <div class="shop-portal-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#ffcc00; font-weight:800; font-size:0.7rem;">{d['sektor'].upper()}</span>
                    <span style="color:#ffcc00;">⭐ {d.get('puan', 0)}</span>
                </div>
                <h3 style="margin:5px 0;">{d['ad']}</h3>
                <p style="color:#888; font-size:0.9rem;">{d['urun']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Detayları Gör: {d['ad']}", key=f"sh_{d['id']}"):
                st.session_state.selected_id = d
                if db and col_ref: col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_id
        if st.button("⬅️ PORTALA GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:#111; padding:50px; border-radius:30px; border:1px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif;">{d['ad']}</h1>
            <p style="font-size:1.5rem; font-weight:700;">{d['urun']}</p>
            <hr style="border-color:#222;">
            <p style="font-style:italic; line-height:1.8; color:#aaa;">"{d['icerik']}"</p>
            <div style="display:flex; justify-content:center; gap:30px; margin:30px 0;">
                <div style="background:#000; padding:15px; border-radius:15px; border:1px solid #333;">Skor: ⭐ {d.get('puan', 0)}</div>
                <div style="background:#000; padding:15px; border-radius:15px; border:1px solid #333;">İlgi: 👁️ {d.get('tıklanma', 0)}</div>
            </div>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:400px; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; font-weight:bold; cursor:pointer;">
                    🟢 WHATSAPP İLE İLETİŞİME GEÇ
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- Diğer Sekmeler (Aynı Mantık) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("portal_reg"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("İletişim*")
        with c2:
            n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Panel Şifresi*", type="password")
        n_urn = st.text_input("İmza Hizmet/Ürün")
        n_tanitim = st.text_area("Tanıtım Metni")
        if st.form_submit_button("SİSTEME KAYDET"):
            if n_ad and n_pwd:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0}
                col_ref.add(data)
                st.success("Kayıt başarılı!")
                time.sleep(1); st.rerun()

with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF GİRİŞİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("PANELE GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Kontrol Paneli")
        u_urn = st.text_input("Ürün Güncelle", value=d['urun'])
        u_icr = st.text_area("Tanıtım Güncelle", value=d['icerik'])
        if st.button("GÜNCELLE"):
            col_ref.document(d['id']).update({"urun": u_urn, "icerik": u_icr})
            st.success("Güncellendi!"); time.sleep(1); st.rerun()
        if st.button("ÇIKIŞ"): st.session_state.owner_shop_id = None; st.rerun()

with tabs[3]:
    pwd = st.text_input("Admin Şifre", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(i['ad']):
                if st.button(f"SİL: {i['ad']}", key=f"del_{i['id']}"):
                    col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Premium Portal | Dörtyol / Hatay</div>", unsafe_allow_html=True)
