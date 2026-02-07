import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Masterpiece",
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

# --- FONKSİYONLAR ---
def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            return data if data else DORTYOL_DATABASE
        except: return DORTYOL_DATABASE
    return DORTYOL_DATABASE

# --- PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    .stApp {{ background-color: #FDFDFD; font-family: 'Inter', sans-serif; color: #1D1D1F; }}
    .main-title {{ font-weight: 900; color: #f97316; font-size: 3rem; text-align: center; letter-spacing: -2px; margin-top: -80px; }}
    .business-card {{ background: white; border-radius: 30px; border: 1px solid #F3F4F6; padding: 25px; margin-bottom: 20px; transition: 0.3s; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .business-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border-color: #f97316; }}
    .price-tag {{ background: #f97316; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 1.1rem; }}
    .category-pill {{ background: #F3F4F6; padding: 10px 20px; border-radius: 50px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.2s; }}
    .category-pill:hover {{ background: #f97316; color: white; }}
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:120px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown('<div style="background:white; padding:40px; border-radius:30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); text-align:center;">', unsafe_allow_html=True)
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("PORTALI AKTİF ET", use_container_width=True):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ne aramıştınız? (Künefe, Altın, Benzin...)", key="main_search")
    
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
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(s.get('img', "https://images.unsplash.com/photo-1555066931-4365d14bab8c"), use_container_width=True)
            with col2:
                st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#f97316; font-weight:800; font-size:0.7rem; text-transform:uppercase;">{s.get('sektor','')}</span>
                        <span style="font-weight:800;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="margin:10px 0; color:#111; letter-spacing:-1px;">{s.get('ad','')}</h2>
                    <p style="color:#666; font-size:0.9rem;">{s.get('icerik','')[:150]}...</p>
                    <small style="color:#999;">👁️ {s.get('tıklanma', 0)} Görüntülenme</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🏪 {s.get('ad')} İncele", key=f"v_{s.get('id', s.get('ad'))}"):
                    st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                    if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
    else:
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("⬅️ GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.image(shop.get('img',''), use_container_width=True)
            st.markdown(f"<h1 style='color:#111; letter-spacing:-2px;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            st.info(f"📍 {shop.get('adres','')} | 🕒 {shop.get('saatler','')}")
            
            for item in shop.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; border:1px solid #EEE; padding:20px; border-radius:20px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#333;">{item['ad']}</span>
                    <span class="price-tag">{item['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.button("💬 WHATSAPP İLE SİPARİŞ VER", use_container_width=True)

# --- 2. KAYIT ---
with tabs[1]:
    st.markdown("### 📝 İşletmenizi Kaydedin")
    with st.form("reg_v37"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör*", cats[1:])
        n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_icr = st.text_area("Tanıtım Yazısı")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": n_icr, "adres": "", "saatler": "", "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"})
                st.success("Başarıyla eklendi!"); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("### 🔐 Esnaf Yönetim Girişi")
        l_ad = st.text_input("Dükkan Adı", placeholder="Kadir Teknoloji...")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'A GİR"):
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Bilgiler hatalı!")
    else:
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
            with st.expander("📝 Ürün Ekle"):
                u_n = st.text_input("Ürün Adı")
                u_p = st.number_input("Fiyat", min_value=0.0)
                if st.button("YAYINLA"):
                    prods = d.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p})
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Eklendi!"); st.rerun()
            if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password", key="admin_pwd")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Onaylandı.")
        for i in all_shops:
            with st.expander(i.get('ad','')):
                st.write(f"Şifre: {i.get('sifre')}")
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Dijital Network | v37.0 Masterpiece Python</div>", unsafe_allow_html=True)
