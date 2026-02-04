import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite",
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
            project_id = key_dict.get("project_id")
            bucket_name = f"{project_id}.firebasestorage.app" 
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})
    except:
        pass

db = firestore.client() if firebase_admin._apps else None
col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar") if db else None
bucket = storage.bucket() if firebase_admin._apps else None

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop_id': None,
    'owner_shop_id': None,
    'sort_by': "Elite Puan"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- DÖRTYOL GERÇEK VERİ TABANI (DETAYLI) ---
DORTYOL_DATABASE = [
    {
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 10.0, "tıklanma": 0,
        "icerik": "Dörtyol'un dijital dönüşüm merkezi. Yazılım çözümleri ve donanım desteği.",
        "tel": "0531 000 00 00", "adres": "Çarşı Merkezi", "saatler": "09:00 - 19:00", "urunler": []
    },
    {
        "ad": "Dörtyol Devlet Hastanesi", "sektor": "Sağlık", "sifre": "saglik2026", "puan": 10.0, "tıklanma": 0,
        "icerik": "Bölge halkına uzman kadrosuyla 7/24 hizmet veren tam teşekküllü sağlık merkezi.",
        "tel": "0326 712 12 12", "adres": "Numune Evler Mah.", "saatler": "24 Saat Açık", "urunler": []
    },
    {
        "ad": "Has Turizm / Jet Turizm", "sektor": "Ulaşım", "sifre": "ulasim2026", "puan": 9.5, "tıklanma": 0,
        "icerik": "Dörtyol Otogarı'ndan Türkiye'nin her yerine konforlu ulaşım ve bilet işlemleri.",
        "tel": "0326 712 00 00", "adres": "Dörtyol Otogarı", "saatler": "06:00 - 00:00", "urunler": []
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 9.9, "tıklanma": 0,
        "icerik": "Güvenilir altın ticareti ve yatırım danışmanlığı. Çeyrek, tam ve gram altın seçenekleri.",
        "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı", "saatler": "08:30 - 18:30", "urunler": []
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 9.8, "tıklanma": 0,
        "icerik": "Tescilli Dörtyol lezzeti. Odun ateşinde sıcak servis künefe.",
        "tel": "0532 111 22 33", "adres": "Atatürk Caddesi", "saatler": "10:00 - 23:00", "urunler": []
    },
    {
        "ad": "Ferah Kebap Salonu", "sektor": "Kebapçı", "sifre": "ferah2026", "puan": 9.7, "tıklanma": 0,
        "icerik": "Gerçek zırh kıyması ve Hatay usulü mezeleriyle kebap şöleni.",
        "tel": "0326 712 33 44", "adres": "İnönü Caddesi", "saatler": "11:00 - 22:00", "urunler": []
    },
    {
        "ad": "Ziraat / İş Bankası / Akbank", "sektor": "Yatırım", "sifre": "banka2026", "puan": 9.4, "tıklanma": 0,
        "icerik": "Dörtyol Şubeleri; kredi, mevduat ve tüm finansal yatırım hizmetleri.",
        "tel": "444 00 00", "adres": "Çarşı Meydanı", "saatler": "09:00 - 17:00", "urunler": []
    }
]

# --- FONKSİYONLAR ---
def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            if not data: return DORTYOL_DATABASE
            return data
        except: return DORTYOL_DATABASE
    return DORTYOL_DATABASE

def resim_yukle(shop_name, file_obj):
    if bucket and file_obj:
        try:
            file_ext = file_obj.name.split('.')[-1]
            blob_path = f"shops/{shop_name}/{int(time.time())}.{file_ext}"
            blob = bucket.blob(blob_path)
            blob.upload_from_string(file_obj.getvalue(), content_type=file_obj.type)
            blob.make_public()
            return blob.public_url
        except: return None
    return None

# --- PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
                    url("https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }}
    .main-title {{ font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 12px; text-shadow: 0 0 30px rgba(255,204,0,0.5); }}
    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 6px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }}
    .product-box {{ background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid #444; margin-bottom: 15px; }}
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        st.markdown('<div style="background:rgba(255,255,255,0.05); padding:40px; border-radius:30px; border:1px solid #ffcc0033; text-align:center;">', unsafe_allow_html=True)
        st.write("<p style='font-family:Playfair Display; font-style:italic; color:#ffcc00; font-size:1.2rem;'>Dörtyol'un En Seçkin Portalı Sizi Bekliyor</p>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod (dortyol2026)")
        if st.button("PORTALI AKTİF ET"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Erişim Kodu Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["💎 ÇARŞIYI GEZ", "🏛️ KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [{"ad": "Tümü", "ikon": "🌐"}, {"ad": "Tatlıcı", "ikon": "🍯"}, {"ad": "Kebapçı", "ikon": "🔥"}, {"ad": "Sağlık", "ikon": "🏥"}, {"ad": "Ulaşım", "ikon": "🚗"}, {"ad": "Hizmet", "ikon": "🛠️"}, {"ad": "Yatırım", "ikon": "💎"}, {"ad": "Teknoloji", "ikon": "💻"}]

# --- 1. KEŞFET ---
with tabs[0]:
    cat_cols = st.columns(len(kategoriler))
    for i, cat in enumerate(kategoriler):
        with cat_cols[i]:
            if st.button(f"{cat['ikon']} {cat['ad']}", key=f"cat_{cat['ad']}"):
                st.session_state.selected_cat = cat['ad']
                st.session_state.selected_shop_id = None
                st.rerun()

    st.divider()
    all_shops = verileri_yukle()
    
    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat]
        for s in filtered:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem;">{s.get('sektor','').upper()}</span>
                        <span style="color:#ffcc00;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:10px 0;">{s.get('ad','')}</h2>
                    <p style="color:#ddd;">{s.get('icerik','')[:150]}...</p>
                    <small style="color:#666;">📍 {s.get('adres','')} | 👁️ {s.get('tıklanma', 0)} Ziyaret</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s.get('ad')} Detaylarını Gör", key=f"v_{s.get('id', s.get('ad'))}"):
                st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                st.rerun()
    else:
        # Shop Detail
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("⬅️ LİSTEYE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.markdown(f"""
                <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:35px; border:2px solid #ffcc00; text-align:center;">
                    <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{shop['ad']}</h1>
                    <p style="font-style:italic; color:#bbb;">"{shop.get('icerik','')}"</p>
                    <div style="display:flex; justify-content:center; gap:15px; margin-top:15px;">
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">📍 {shop.get('adres','')}</span>
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">🕒 {shop.get('saatler','')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            for item in shop.get('urunler', []):
                st.markdown(f'<div class="product-box"><h4>{item["ad"]}</h4><p>{item["detay"]}</p><b>{item["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Kadir Teknoloji)")
        l_pwd = st.text_input("Şifre (tekno2026)", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s.get('ad','').lower() == l_ad.lower() and str(s.get('sifre')) == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Giriş Hatalı!")
    else:
        st.subheader("📊 Kontrol Merkezi")
        if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Girişi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Onaylandı!")
        st.write("Buradan dükkanları denetleyebilir ve performans verilerini takip edebilirsin.")
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(i.get('ad','')):
                st.write(f"Sektör: {i.get('sektor')} | Şifre: {i.get('sifre')}")
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v27.0 Dörtyol Edition</div>", unsafe_allow_html=True)
