import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı 2026 | Elite Portal",
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
    'sort_filter': "Elite Puan"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- MOCK DATA (YENİ NESİL KURUMSAL TANITIMLAR) ---
MOCK_SHOPS = [
    {"ad": "Fıstıkzade Gurme", "sektor": "Tatlıcı", "urun": "Antep Fıstıklı Özel Hasır", "tel": "0532 000 00 31", "icerik": "Dörtyol'un kalbinde, geleneksel yöntemlerle hazırlanan en taze fıstıklı lezzetlerin buluşma noktası.", "puan": 9.8, "tıklanma": 450, "indirim": "%15", "yildizli": True},
    {"ad": "Dörtyol Kebap Sarayı", "sektor": "Kebapçı", "urun": "Özel Zırh Kıyma Kebap", "tel": "0532 111 22 33", "icerik": "Yılların tecrübesiyle, meşe odununda pişen gerçek kebap lezzetini sofranıza taşıyoruz.", "puan": 9.5, "tıklanma": 320, "indirim": None, "yildizli": True},
    {"ad": "Merkez Şifa Eczanesi", "sektor": "Sağlık", "urun": "Kişisel Bakım & Sağlık Danışmanlığı", "tel": "0326 712 00 00", "icerik": "Sağlığınız için güvenilir ilaç temini ve uzman danışmanlık hizmetiyle 7/24 yanınızdayız.", "puan": 10.0, "tıklanma": 600, "indirim": None, "yildizli": False},
    {"ad": "Elite Otomotiv Plazası", "sektor": "Ulaşım", "urun": "Lüks Segment Araç Portföyü", "tel": "0505 505 50 50", "icerik": "Geleceğin otomobil dünyasında, premium araç seçenekleri ve güvenli ticaretin tek adresi.", "puan": 9.2, "tıklanma": 180, "indirim": "Özel Oranlar", "yildizli": False},
    {"ad": "Mücevher Köşesi", "sektor": "Yatırım", "urun": "Has Altın & Değerli Taşlar", "tel": "0533 333 33 33", "icerik": "Birikimlerinizi sanata dönüştüren tasarımlar ve güvenilir yatırım danışmanlığı.", "puan": 9.9, "tıklanma": 290, "indirim": None, "yildizli": True},
    {"ad": "Zerafet Moda Evi", "sektor": "Giyim", "urun": "Yeni Sezon Elite Koleksiyon", "tel": "0533 444 55 66", "icerik": "Dünya modasını Dörtyol'a getiren çizgilerle tarzınızı baştan yaratın.", "puan": 8.9, "tıklanma": 210, "indirim": "%30", "yildizli": False}
]

# --- FONKSİYONLAR ---
def verileri_yukle():
    data = []
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: pass
    if not data: return MOCK_SHOPS
    
    if st.session_state.sort_filter == "Elite Puan":
        return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
    elif st.session_state.sort_filter == "Popülerlik":
        return sorted(data, key=lambda x: x.get('tıklanma', 0), reverse=True)
    return data

# --- ELITE MOTION UI (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    /* Ana Arka Plan Görseli (Canlı Renkler) */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.85)), 
                    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Login Hero Section */
    .hero-container {{
        text-align: center;
        padding-top: 50px;
        margin-bottom: 30px;
    }}
    .welcome-text {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.5rem;
        color: #ffcc00;
        margin-top: -10px;
        opacity: 0.9;
    }}

    /* Giriş Kartı */
    .login-box {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 35px;
        padding: 40px;
        border: 1px solid rgba(255, 204, 0, 0.3);
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
    }}

    /* Kategori Kartları */
    .cat-motion-card {{
        background: rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: 0.4s;
        cursor: pointer;
        margin-bottom: 15px;
    }}
    .cat-motion-card:hover {{
        border: 1px solid #ffcc00;
        transform: translateY(10px);
        background: rgba(255, 204, 0, 0.1);
    }}

    .portal-title {{
        font-family: 'Cinzel', serif;
        color: #ffcc00;
        font-size: 3.2rem;
        letter-spacing: 15px;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.5);
    }}

    /* Dükkan Kartı */
    .portal-shop-card {{
        background: rgba(0,0,0,0.5);
        border-radius: 25px;
        border-left: 6px solid #ffcc00;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* Butonlar */
    .stButton>button {{
        background: linear-gradient(90deg, #ffcc00, #ffaa00) !important;
        color: #000 !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown("""
        <div class="hero-container">
            <h1 class="portal-title">DÖRTYOL ÇARŞI</h1>
            <p class="welcome-text">Hoş geldiniz, Dörtyol'un En Seçkin Portalı Sizi Bekliyor</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([2, 1.5, 2])
    with col_login:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.write("<p style='text-align:center; font-size:0.9rem; color:#ddd;'>Erişim için lütfen anahtar kodunuzu girin.</p>", unsafe_allow_html=True)
        key_input = st.text_input("", type="password", placeholder="Anahtar Kodu")
        if st.button("PORTALI AKTİF ET"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Erişim Kodu Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#666; font-size:0.7rem; margin-top:20px;'>© 2026 Albayrax Premium Ecosystem</p>", unsafe_allow_html=True)
    st.stop()

# --- ANA PORTAL ---
st.markdown('<h1 class="portal-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# ARAMA & FİLTRELEME
c_search, c_filter = st.columns([3, 1])
with c_search:
    search_q = st.text_input("", placeholder="🔍 Aradığınız dükkan, hizmet veya meşhur ürün...", key="search_v17")
with c_filter:
    st.session_state.sort_filter = st.selectbox("", ["Elite Puan", "Popülerlik"])

# SEKMELER
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# KATEGORİLER
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
    st.markdown("### 🏷️ Sektör Seçin")
    for i in range(0, len(kategoriler), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(kategoriler):
                cat = kategoriler[i + j]
                active = st.session_state.selected_cat == cat['ad']
                with cols[j]:
                    st.markdown(f"""
                        <div class="cat-motion-card" style="border-color: {'#ffcc00' if active else 'rgba(255,255,255,0.1)'};">
                            <span style="font-size:2.5rem; display:block; margin-bottom:10px;">{cat['ikon']}</span>
                            <span style="font-size:0.8rem; font-weight:800; color:#ffcc00; letter-spacing:1px;">{cat['ad'].upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Keşfet: {cat['ad']}", key=f"cat_{cat['ad']}"):
                        st.session_state.selected_cat = cat['ad']
                        st.session_state.selected_id = None
                        st.rerun()

    st.divider()

    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        filtered = [d for d in dukkanlar if (search_q.lower() in d['ad'].lower() or search_q.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        st.write(f"🔍 **{st.session_state.selected_cat}** kategorisinde **{len(filtered)}** dükkan listeleniyor.")
        
        for d in filtered:
            st.markdown(f"""
            <div class="portal-shop-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="display:flex; gap:10px;">
                        {f'<span style="background:#ffcc00; color:black; padding:2px 10px; border-radius:50px; font-size:0.7rem; font-weight:900;">🏆 ELİTE</span>' if d.get('yildizli') else ''}
                        {f'<span style="background:#00ffcc; color:black; padding:2px 10px; border-radius:50px; font-size:0.7rem; font-weight:900;">🔥 {d["indirim"]}</span>' if d.get('indirim') else ''}
                    </div>
                    <span style="color:#ffcc00; font-weight:800;">⭐ {d.get('puan', 0)} / 10</span>
                </div>
                <h2 style="margin:0; color:white; font-family:'Cinzel', serif;">{d['ad']}</h2>
                <p style="color:#aaa; font-size:1rem; margin:10px 0;">{d['urun']}</p>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#555; font-size:0.8rem;">📍 Dörtyol / Hatay</span>
                    <span style="color:#444; font-size:0.8rem;">👁️ {d.get('tıklanma', 0)} Ziyaret</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"MAĞAZAYI İNCELE: {d['ad']}", key=f"sh_{d['ad']}"):
                st.session_state.selected_id = d
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_id
        if st.button("⬅️ PORTALA GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:60px; border-radius:40px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif; font-size:3.5rem; margin:0;">{d['ad']}</h1>
            <p style="font-size:1.8rem; font-weight:700; color:#ddd;">{d['urun']}</p>
            <hr style="border-color:#333; width:40%; margin:40px auto;">
            <p style="font-size:1.3rem; line-height:1.8; color:#ccc; font-style:italic;">"{d['icerik']}"</p>
            <br>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:500px; background:#25D366; color:white; border:none; padding:20px; border-radius:20px; font-weight:bold; font-size:1.4rem; cursor:pointer; box-shadow: 0 0 30px rgba(37,211,102,0.4);">
                    🟢 WHATSAPP İLE İLETİŞİME GEÇ
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- DİĞER SEKMELER (GÜNCELLENMİŞ) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("elite_reg_v17"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("WhatsApp İletişim*")
        with c2:
            n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Panel Şifresi*", type="password")
        n_urn = st.text_input("Ana Ürün/Hizmet")
        n_tanitim = st.text_area("İşletme Tanıtım Yazısı")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "yildizli": False}
                col_ref.add(data)
                st.success("Tebrikler! Dükkanınız sisteme dahil edildi.")
                time.sleep(1); st.rerun()

with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF PANELİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Yönetim")
        st.write(f"Popülerlik: {d.get('tıklanma', 0)} Ziyaret")
        if st.button("ÇIKIŞ YAP"): st.session_state.owner_shop_id = None; st.rerun()

with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(i['ad']):
                    if st.button(f"Yıldızlı Yap/Kaldır: {i['ad']}", key=f"star_{i['id']}"):
                        col_ref.document(i['id']).update({"yildizli": not i.get('yildizli', False)})
                        st.rerun()
                    if st.button(f"SİSTEMDEN SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Premium Ecosystem | v17.0 Vivid Edition</div>", unsafe_allow_html=True)
