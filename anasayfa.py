import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
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

# --- TEST VERİSİ EKLEME (MOCK DATA) ---
# Eğer veri tabanı boşsa sistemi test etmek için bu dükkanlar görünür
MOCK_SHOPS = [
    {"ad": "Fıstıkzade Gurme", "sektor": "Tatlıcı", "urun": "Antep Fıstıklı Hasır", "tel": "0532 000 00 31", "icerik": "Dörtyol'un en çıtır lezzeti.", "puan": 9.8, "tıklanma": 120},
    {"ad": "Dörtyol Kebap Sarayı", "sektor": "Kebapçı", "urun": "Kıyma Kebap", "tel": "0532 111 22 33", "icerik": "Zırh kıymasıyla gerçek lezzet.", "puan": 9.5, "tıklanma": 85},
    {"ad": "Şifa Eczanesi", "sektor": "Sağlık", "urun": "Nöbetçi Eczane Hizmeti", "tel": "0326 712 00 00", "icerik": "Sağlığınız bizim için değerli.", "puan": 10.0, "tıklanma": 200},
    {"ad": "Albayrax Galeri", "sektor": "Ulaşım", "urun": "Premium Araç Alım-Satım", "tel": "0505 505 50 50", "icerik": "2026 model elit araçlar.", "puan": 9.2, "tıklanma": 45},
    {"ad": "Demir Hırdavat", "sektor": "Hizmet", "urun": "Profesyonel El Aletleri", "tel": "0544 444 44 44", "icerik": "Tamir ve tadilatın tek adresi.", "puan": 8.7, "tıklanma": 30},
    {"ad": "Altın Köşem", "sektor": "Yatırım", "urun": "24 Ayar Yatırımlık Altın", "tel": "0533 333 33 33", "icerik": "Geleceğinizi sağlama alın.", "puan": 9.9, "tıklanma": 150}
]

# --- FONKSİYONLAR ---
def verileri_yukle():
    data = []
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: pass
    
    # Eğer veri tabanından veri gelmezse (ilk kurulum), mock datayı göster
    if not data:
        return MOCK_SHOPS
    
    # Sıralama
    if st.session_state.sort_filter == "Puan (Yüksek)":
        return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
    return data

# --- PORTAL GRID UI (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background-color: #080808;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Giriş Ekranı (Hero) */
    .hero-login {{
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1920");
        background-size: cover;
        background-position: center;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-bottom: 2px solid #ffcc00;
        margin-top: -100px;
        text-align: center;
    }}

    /* Kategori Kartları (3'lü Izgara) */
    .cat-card-grid {{
        background: #121212;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #222;
        transition: 0.3s;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        margin-bottom: 10px;
    }}
    .cat-card-grid:hover {{
        border: 1px solid #ffcc00;
        background: #1a1a1a;
        transform: translateY(-5px);
    }}
    .cat-icon {{ font-size: 2rem; margin-bottom: 8px; }}
    .cat-label {{ font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; color: #ffcc00; }}

    /* Dükkan Kartı */
    .shop-portal-card {{
        background: #111;
        border-radius: 20px;
        border-left: 6px solid #ffcc00;
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
        border-top: 1px solid #222;
        border-right: 1px solid #222;
        border-bottom: 1px solid #222;
    }}
    .shop-portal-card:hover {{
        background: #181818;
        transform: translateX(10px);
    }}

    /* Arama Çubuğu */
    .stTextInput>div>div>input {{
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        color: white !important;
        height: 45px;
    }}

    /* Başlıklar */
    .portal-main-title {{
        font-family: 'Cinzel', serif;
        color: #ffcc00;
        font-size: 2.2rem;
        letter-spacing: 8px;
        text-align: center;
        margin-bottom: 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown("""
        <div class="hero-login">
            <h1 style="font-family:'Cinzel', serif; color:#ffcc00; font-size:3rem; letter-spacing:10px;">DÖRTYOL ÇARŞI</h1>
            <p style="color:#aaa; letter-spacing:3px;">ELİTE ESNAF PORTALI GİRİŞİ</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([2, 1, 2])
    with col_login:
        key_input = st.text_input("", type="password", placeholder="Giriş Anahtarı...")
        if st.button("PORTALI ATEŞLE"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı anahtar!")
    st.stop()

# --- ANA PORTAL ---
st.markdown('<h1 class="portal-main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:0.7rem; color:#666; letter-spacing:3px;">DİJİTAL ÇARŞI EKOSİSTEMİ</p>', unsafe_allow_html=True)

# ARAMA ÇUBUĞU (TEPEDE)
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_q = st.text_input("", placeholder="🔍 Dükkan, hizmet veya imza ürün ara...", key="portal_search_v15")

# SEKMELER
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# KATEGORİLER (3'LÜ GRID İÇİN)
kategoriler = [
    {"ad": "Tümü", "ikon": "🌐"},
    {"ad": "Tatlıcı", "ikon": "🍯"},
    {"ad": "Kebapçı", "ikon": "🔥"},
    {"ad": "Sağlık", "ikon": "🏥"},
    {"ad": "Ulaşım", "ikon": "🚗"},
    {"ad": "Hizmet", "ikon": "🛠️"},
    {"ad": "Yatırım", "ikon": "💎"},
    {"ad": "Giyim", "ikon": "👕"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # 3x3 KATEGORİ GRID SİSTEMİ
    st.markdown("### 🏷️ Sektör Seçin")
    
    # Kategorileri 3'lü sütunlara bölüyoruz
    for i in range(0, len(kategoriler), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(kategoriler):
                cat = kategoriler[i + j]
                active = st.session_state.selected_cat == cat['ad']
                with cols[j]:
                    st.markdown(f"""
                        <div class="cat-card-grid" style="border-color: {'#ffcc00' if active else '#222'};">
                            <span class="cat-icon">{cat['ikon']}</span>
                            <span class="cat-label">{cat['ad'].upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Gör: {cat['ad']}", key=f"cat_btn_{cat['ad']}"):
                        st.session_state.selected_cat = cat['ad']
                        st.session_state.selected_id = None
                        st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME
    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        filtered = [d for d in dukkanlar if (search_q.lower() in d['ad'].lower() or search_q.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        st.write(f"🔍 **{st.session_state.selected_cat}** kategorisinde **{len(filtered)}** sonuç bulundu.")
        
        for d in filtered:
            st.markdown(f"""
            <div class="shop-portal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#ffcc00; font-weight:800; font-size:0.7rem; border:1px solid #444; padding:2px 8px; border-radius:5px;">{d['sektor'].upper()}</span>
                    <span style="color:#ffcc00; font-weight:800;">⭐ {d.get('puan', 0)}</span>
                </div>
                <h3 style="margin:10px 0; color:white;">{d['ad']}</h3>
                <p style="color:#aaa; font-size:0.9rem; margin-bottom:5px;"><b>İmza Ürün:</b> {d['urun']}</p>
                <p style="color:#555; font-size:0.75rem;">📍 Dörtyol / Hatay</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Dükkanı İncele: {d['ad']}", key=f"sh_{d['ad']}"):
                st.session_state.selected_id = d
                if db and col_ref and 'id' in d: # Mock data değilse tık artır
                    col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY GÖRÜNÜMÜ
        d = st.session_state.selected_id
        if st.button("⬅️ LİSTEYE GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:#111; padding:40px; border-radius:30px; border:2px solid #ffcc00; text-align:center; box-shadow: 0 0 40px rgba(255,204,0,0.1);">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif; margin:0;">{d['ad']}</h1>
            <p style="font-size:1.4rem; color:#ddd; font-weight:700;">{d['urun']}</p>
            <hr style="border-color:#333; width:50%; margin:20px auto;">
            <p style="font-style:italic; line-height:1.8; color:#aaa; font-size:1.1rem; padding:0 20px;">"{d['icerik']}"</p>
            <div style="display:flex; justify-content:center; gap:30px; margin:30px 0;">
                <div style="background:#000; padding:15px 30px; border-radius:15px; border:1px solid #ffcc00;">Skor: ⭐ {d.get('puan', 0)}</div>
                <div style="background:#000; padding:15px 30px; border-radius:15px; border:1px solid #ffcc00;">İlgi: 👁️ {d.get('tıklanma', 0)}</div>
            </div>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:400px; background:#25D366; color:white; border:none; padding:18px; border-radius:15px; font-weight:bold; cursor:pointer; font-size:1.1rem;">
                    🟢 WHATSAPP SİPARİŞ HATTI
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- DİĞER SEKMELER (SABİT) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("portal_reg_v15"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("Resmi WhatsApp*")
        with c2:
            n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_urn = st.text_input("İmza Ürün/Hizmet")
        n_tanitim = st.text_area("İşletme Hikayesi")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0}
                col_ref.add(data)
                st.success("Başvuru alındı! Sektörünüzde dükkanınız görünecektir.")
                time.sleep(1); st.rerun()

with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF GİRİŞİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Kayıtlı Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Paneli")
        st.write(f"Görüntülenme: {d.get('tıklanma', 0)}")
        if st.button("ÇIKIŞ YAP"): st.session_state.owner_shop_id = None; st.rerun()

with tabs[3]:
    pwd = st.text_input("Yönetici Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Aktif.")
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(i['ad']):
                    if st.button(f"SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.2; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Portal Grid | v15.0 Elite Architecture</div>", unsafe_allow_html=True)
