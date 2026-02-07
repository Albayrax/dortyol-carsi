import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Contrast Edition",
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

# --- MASTERPIECE VERI SETI ---
DORTYOL_DATABASE = [
    {
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 5.0, "tıklanma": 0,
        "icerik": "İleri teknoloji, robotik sistemler ve AI yazılım çözümleri merkezi.",
        "tel": "0531 000 00 00", "adres": "Dijital Vadi No:1", "saatler": "09:00 - 20:00",
        "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800",
        "urunler": [{"ad": "AI Sunucu Paketi", "fiyat": 15000}, {"ad": "Teknik Servis", "fiyat": 500}]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 4.9, "tıklanma": 0,
        "icerik": "Tescilli kral hasırı ve odun ateşinde Hatay künefesi.",
        "tel": "0532 111 22 33", "adres": "Atatürk Cad.", "saatler": "10:00 - 01:00",
        "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800",
        "urunler": [{"ad": "Kral Hasırı", "fiyat": 240}, {"ad": "Peynirli Künefe", "fiyat": 180}]
    },
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 4.7, "tıklanma": 0,
        "icerik": "Güvenli yakıt ve 24 saat kesintisiz market hizmeti.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu", "saatler": "24 Saat Açık",
        "img": "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800",
        "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}, {"ad": "V-Pro Dizel", "fiyat": 50.25}]
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 4.8, "tıklanma": 0,
        "icerik": "Has altın ve pırlantada Dörtyol'un güven kapısı.",
        "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı", "saatler": "08:30 - 18:30",
        "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=800",
        "urunler": [{"ad": "Gram Altın (24A)", "fiyat": 3150}]
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

# --- HIGH CONTRAST UI (TURUNCU & MAVİ) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap');
    
    /* Tüm Sayfa Arka Planı Turuncu */
    .stApp {{ 
        background-color: #FF8C00; 
        font-family: 'Poppins', sans-serif; 
    }}

    /* Ana Başlık Derin Mavi */
    .main-title {{ 
        font-weight: 900; 
        color: #001F3F; 
        font-size: 3.5rem; 
        text-align: center; 
        letter-spacing: -2px; 
        margin-top: -80px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}

    /* Alt Başlıklar ve Yazılar Mavi */
    h1, h2, h3, p, span, label {{
        color: #001F3F !important;
    }}

    /* Dükkan Kartları (Fark Edilmesi İçin Açık Mavi/Beyaz Karışımı) */
    .business-card {{ 
        background: #F0F8FF; 
        border-radius: 25px; 
        border: 3px solid #001F3F; 
        padding: 25px; 
        margin-bottom: 20px; 
        transition: 0.3s;
    }}
    
    .business-card:hover {{ 
        transform: scale(1.02); 
        box-shadow: 0 15px 30px rgba(0,31,63,0.2); 
    }}

    /* Fiyat Etiketi (Canlı ve Net) */
    .price-tag {{ 
        background: #001F3F; 
        color: #FF8C00 !important; 
        padding: 6px 15px; 
        border-radius: 12px; 
        font-weight: 900; 
        font-size: 1.2rem; 
    }}

    /* Butonlar */
    .stButton>button {{
        background-color: #001F3F !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: 0.3s !important;
    }}
    .stButton>button:hover {{
        background-color: #003366 !important;
        transform: translateY(-2px);
    }}

    /* Input Alanları */
    input {{
        border: 2px solid #001F3F !important;
        border-radius: 10px !important;
    }}

    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (MAVİ YAZILI GİRİŞ) ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:120px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown(f'''
            <div style="background:#F0F8FF; padding:40px; border-radius:30px; border:4px solid #001F3F; text-align:center;">
                <h3 style="color:#001F3F;">Elite Portal Girişi</h3>
            </div>
        ''', unsafe_allow_html=True)
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="Şifrenizi mavi kutuya yazın")
        if st.button("PORTALI AÇ", use_container_width=True):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="main_search")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Hizmet", "Yatırım", "Teknoloji"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"c_{c}", use_container_width=True):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    st.divider()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        
        for s in filtered:
            col1, col2 = st.columns([1, 2.5])
            with col1:
                st.image(s.get('img', ""), use_container_width=True)
            with col2:
                st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#001F3F; font-weight:900; font-size:0.8rem; text-transform:uppercase; background:#FF8C00; padding:2px 10px; border-radius:50px;">{s.get('sektor','')}</span>
                        <span style="font-weight:900; color:#001F3F;">⭐ {s.get('puan', 0)} / 5</span>
                    </div>
                    <h2 style="margin:10px 0; color:#001F3F; font-weight:900;">{s.get('ad','')}</h2>
                    <p style="color:#001F3F; font-size:1rem; font-weight:500;">{s.get('icerik','')[:150]}...</p>
                    <small style="color:#003366; font-weight:700;">👁️ {s.get('tıklanma', 0)} Kez Bakıldı</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 {s.get('ad')} İncele", key=f"v_{s.get('id', s.get('ad'))}", use_container_width=True):
                    st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                    if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
    else:
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("⬅️ LİSTEYE DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.image(shop.get('img',''), use_container_width=True)
            st.markdown(f"<h1 style='color:#001F3F; font-weight:900;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<div style='background:#001F3F; color:white; padding:15px; border-radius:15px;'>📍 {shop.get('adres','')} | 🕒 {shop.get('saatler','')}</div>", unsafe_allow_html=True)
            
            st.write("### Ürün Kataloğu")
            for item in shop.get('urunler', []):
                st.markdown(f"""
                <div style="background:#F0F8FF; border:2px solid #001F3F; padding:20px; border-radius:20px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:900; color:#001F3F; font-size:1.1rem;">{item['ad']}</span>
                    <span class="price-tag">{item['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.button("💬 WHATSAPP İLE SİPARİŞ VER", use_container_width=True)

# --- 2. KAYIT (YÜKSEK KONTRAST) ---
with tabs[1]:
    st.markdown("<h3 style='color:#001F3F;'>📝 Yeni İşletme Kayıt Formu</h3>", unsafe_allow_html=True)
    with st.form("reg_v38"):
        n_ad = st.text_input("Dükkan Resmi Adı*")
        n_sek = st.selectbox("Sektör Seçin*", cats[1:])
        n_pwd = st.text_input("Yönetim Şifreniz*", type="password")
        n_icr = st.text_area("Müşterilere Gösterilecek Tanıtım Yazısı")
        if st.form_submit_button("📜 BAŞVURUYU SİSTEME GÖNDER"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": n_icr, "adres": "", "saatler": "", "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"})
                st.success("Tebrikler! Dükkanınız Dörtyol Çarşı'ya eklendi."); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='color:#001F3F;'>🔐 Esnaf Yönetim Girişi</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Kayıtlı Dükkan Adı", placeholder="Örn: Kadir Teknoloji")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'U AÇ"):
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Bilgiler uyuşmuyor!")
    else:
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Yönetim Merkezi")
            with st.expander("➕ Ürün/Hizmet Ekle"):
                u_n = st.text_input("Ürün İsmi")
                u_p = st.number_input("Satış Fiyatı", min_value=0.0)
                if st.button("VİTRİNE EKLE"):
                    prods = d.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p})
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Ürün anında yayına alındı!"); time.sleep(1); st.rerun()
            if st.button("🚪 GÜVENLİ ÇIKIŞ"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Süper Yönetici Şifresi", type="password", key="admin_pwd_v38")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Kontrolü Onaylandı.")
        for i in all_shops:
            with st.expander(f"⚙️ {i.get('ad','')} Denetle"):
                st.write(f"Şifre: **{i.get('sifre')}**")
                if st.button(f"KAYDI SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; font-weight:800; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Dijital Network | v38.0 High Contrast Edition</div>", unsafe_allow_html=True)
