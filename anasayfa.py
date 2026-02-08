import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | Orange Elite",
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
            p_id = key_dict.get("project_id")
            b_name = st.secrets["firebase"].get("storage_bucket", f"{p_id}.firebasestorage.app")
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': b_name})
    except Exception as e:
        pass

db = firestore.client() if firebase_admin._apps else None
col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar") if db else None

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop_id': None,
    'owner_shop_id': None
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- HAYALİ VE ESTETİK VERİ SETİ ---
DORTYOL_DATABASE = [
    {
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 5.0, "tıklanma": 1240,
        "icerik": "Geleceğin teknolojisi Dörtyol'a geldi. Robotik sistemler ve akıllı AI yazılımlar.",
        "tel": "0531 000 00 00", "adres": "Dijital Vadi No:1", "saatler": "09:00 - 20:00",
        "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800",
        "urunler": [{"ad": "AI Otomasyon", "fiyat": 15000, "desc": "İşletme zekası."}, {"ad": "Teknik Servis", "fiyat": 750, "desc": "7/24 destek."}]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 4.9, "tıklanma": 3500,
        "icerik": "Odun ateşinde, tescilli Hatay lezzeti ile hazırlanan künefe şöleni.",
        "tel": "0532 111 22 33", "adres": "Atatürk Cad. Merkez", "saatler": "10:00 - 01:00",
        "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800",
        "urunler": [{"ad": "Kral Hasırı", "fiyat": 240, "desc": "Efsane lezzet."}, {"ad": "Peynirli Künefe", "fiyat": 180, "desc": "Sıcak servis."}]
    },
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 4.7, "tıklanma": 850,
        "icerik": "24 saat kesintisiz, yüksek standartlarda yakıt ve market hizmeti.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu", "saatler": "24 Saat Açık",
        "img": "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800",
        "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50, "desc": "Performans serisi."}, {"ad": "V-Pro Dizel", "fiyat": 50.25, "desc": "Temiz motor."}]
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 4.8, "tıklanma": 2100,
        "icerik": "Has altın ve mücevheratta yarım asırlık güvenin adresi.",
        "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı No:12", "saatler": "08:30 - 18:30",
        "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=800",
        "urunler": [{"ad": "Gram Altın (24A)", "fiyat": 3200, "desc": "Sertifikalı yatırım."}]
    }
]

def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            return data if data else DORTYOL_DATABASE
        except: return DORTYOL_DATABASE
    return DORTYOL_DATABASE

# --- ORANGE ELITE CUSTOM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');
    
    /* Full Orange Background */
    .stApp {{ 
        background-color: #FF8C00; 
        font-family: 'Outfit', sans-serif;
    }}

    /* Global Text Visibility - Deep Navy Blue */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small {{
        color: #001F3F !important;
    }}

    /* Top Bar & Title */
    .main-title {{ 
        font-weight: 900; 
        color: #001F3F !important; 
        font-size: 3.5rem; 
        text-align: center; 
        letter-spacing: -2px; 
        margin-top: -80px;
        text-shadow: 2px 2px 0px rgba(255,255,255,0.2);
    }}

    /* Card Styling - High Contrast */
    .business-card {{ 
        background: white; 
        border-radius: 28px; 
        padding: 0; 
        margin-bottom: 25px; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 4px solid #001F3F;
        overflow: hidden;
        box-shadow: 10px 10px 0px #001F3F;
    }}
    .business-card:hover {{ 
        transform: translate(-5px, -5px);
        box-shadow: 15px 15px 0px #001F3F;
    }}

    .card-content {{ padding: 25px; background: white; }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #001F3F;
        border-radius: 50px;
        padding: 5px 20px;
        margin-bottom: 30px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #FF8C00 !important;
        font-weight: 900 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #FF8C00 !important;
        color: #001F3F !important;
        border-radius: 40px;
    }}

    /* Price Tag */
    .price-tag {{ 
        background: #001F3F; 
        color: #FF8C00 !important; 
        padding: 10px 20px; 
        border-radius: 15px; 
        font-weight: 900; 
        font-size: 1.2rem; 
    }}

    /* Modern Blue Buttons */
    .stButton>button {{
        background-color: #001F3F !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        font-weight: 800 !important;
        border: 2px solid #001F3F !important;
        transition: 0.3s !important;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: #FF8C00 !important;
        color: #001F3F !important;
        transform: scale(1.02);
    }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: white !important;
        color: #001F3F !important;
        border: 3px solid #001F3F !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
    }}

    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        st.markdown(f'''
            <div style="background:white; padding:40px; border-radius:32px; border:5px solid #001F3F; text-align:center;">
                <h2 style="color:#001F3F; margin-bottom:10px;">Elite Giriş</h2>
                <p style="color:#001F3F; font-weight:600;">Portala erişmek için anahtar kodu girin.</p>
            </div>
        ''', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod (dortyol2026)")
        if st.button("SİSTEMİ ATEŞLE"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["💎 KEŞFET", "🏛️ DÜKKAN AÇ", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ne aramıştınız? (Künefe, Altın, Benzin...)", key="search_v40")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Yatırım", "Teknoloji"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"c_v40_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    st.divider()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        
        for s in filtered:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(s.get('img', ""), use_container_width=True)
            with c2:
                st.markdown(f"""
                <div class="card-content">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="background:#001F3F; color:#FF8C00; font-weight:900; font-size:0.7rem; padding:5px 15px; border-radius:50px;">{s.get('sektor','').upper()}</span>
                        <span style="color:#001F3F; font-weight:900;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="margin:0; font-weight:900; font-size:2rem;">{s.get('ad','')}</h2>
                    <p style="margin:15px 0; font-size:1.1rem; font-weight:600; line-height:1.4;">{s.get('icerik','')[:140]}...</p>
                    <small style="font-weight:800; opacity:0.6;">👁️ {s.get('tıklanma', 0)} Görüntülenme</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{s.get('ad')} Mağazasına Gir →", key=f"v_v40_{s.get('id', s.get('ad'))}"):
                    st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                    if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DETAY SAYFASI
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("← LİSTEYE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.image(shop.get('img',''), use_container_width=True)
            st.markdown(f"<h1 style='font-weight:900; font-size:3.5rem; margin-top:20px;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:#001F3F; color:#FF8C00 !important; padding:25px; border-radius:25px; display:flex; gap:30px; border:4px solid #001F3F;">
                    <span style="color:#FF8C00 !important; font-weight:900;">📍 {shop.get('adres','')}</span> 
                    <span style="color:#FF8C00 !important; font-weight:900;">🕒 {shop.get('saatler','')}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='margin-top:30px; font-weight:900;'>📦 ÜRÜN VE HİZMET LİSTESİ</h3>", unsafe_allow_html=True)
            for item in shop.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; border:4px solid #001F3F; padding:25px; border-radius:25px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; box-shadow: 5px 5px 0px #001F3F;">
                    <div>
                        <span style="font-weight:900; font-size:1.3rem; display:block;">{item['ad']}</span>
                        <small style="font-weight:700; opacity:0.7;">{item.get('desc','Hemen Sipariş Ver')}</small>
                    </div>
                    <span class="price-tag">{item['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.button(f"💬 WHATSAPP: {shop.get('tel','0000')}", use_container_width=True)

# --- 2. DÜKKAN AÇ ---
with tabs[1]:
    st.markdown('<div style="background:white; padding:50px; border-radius:40px; border:6px solid #001F3F; box-shadow: 15px 15px 0px #001F3F;">', unsafe_allow_html=True)
    st.markdown("<h2>🏛️ İşletmenizi Elite Sisteme Dahil Edin</h2>", unsafe_allow_html=True)
    with st.form("reg_v40"):
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("Dükkan Adı*")
        n_sek = c2.selectbox("Sektör*", cats[1:])
        n_pwd = c1.text_input("Şifre Belirleyin*", type="password")
        n_tel = c2.text_input("WhatsApp No*")
        n_icr = st.text_area("Tanıtım Metni")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "tel": n_tel, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": n_icr, "adres": "Dörtyol", "saatler": "09:00-19:00", "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"})
                st.success("Başarılı! Kaydınız alındı."); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("### 🔐 Esnaf Yönetim Girişi")
        l_ad = st.text_input("Kayıtlı Dükkan İsmi")
        l_pwd = st.text_input("Panel Şifresi", type="password")
        if st.button("KONTROL PANELİNİ AÇ"):
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Bilgiler uyuşmuyor!")
    else:
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Yönetim")
            with st.expander("📝 Yeni Ürün/Hizmet Ekle"):
                u_n = st.text_input("Ürün Adı")
                u_p = st.number_input("Fiyat", min_value=0.0)
                if st.button("VİTRİNE EKLE"):
                    prods = d.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p})
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Eklendi!"); time.sleep(1); st.rerun()
            if st.button("🚪 ÇIKIŞ YAP"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Süper Admin Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Sistem Denetimi Aktif.")
        for i in all_shops:
            with st.expander(f"⚙️ {i.get('ad','')} Kaydı"):
                st.write(f"Şifre: **{i.get('sifre')}**")
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; font-weight:900; color:#001F3F;'>© {GUNCEL_YIL} Albayrax Elite Portal | v40.0 Orange Elite</div>", unsafe_allow_html=True)
