import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite Leaderboard",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- FIREBASE BAĞLANTISI (STORAGE SAFE MODE) ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            p_id = key_dict.get("project_id")
            b_name = st.secrets["firebase"].get("storage_bucket", f"{p_id}.firebasestorage.app")
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': b_name})
    except Exception as e:
        st.error(f"Firebase başlatma hatası: {e}")

db = firestore.client() if firebase_admin._apps else None
col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar") if db else None
bucket = None
if firebase_admin._apps:
    try:
        key_dict = json.loads(st.secrets["firebase"]["key"])
        bucket = storage.bucket(f"{key_dict.get('project_id')}.firebasestorage.app")
    except: pass

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop_id': None,
    'owner_shop_id': None,
    'sort_by': "Elite Puan",
    'product_sort': "Önerilen"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- DÖRTYOL ÖZEL VERİ TABANI (GÜNCELLENMİŞ MENÜLER) ---
DORTYOL_DATABASE = [
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 9.9, "tıklanma": 0,
        "icerik": "Dörtyol'un tescilli lezzet durağı. Meşhur kral hasırı ve sıcak servis künefe.",
        "tel": "0532 111 22 33", "adres": "Atatürk Caddesi", "saatler": "10:00 - 00:00",
        "urunler": [
            {"ad": "Künefe", "fiyat": 180, "detay": "Klasik Hatay peynirli."},
            {"ad": "Hasır", "fiyat": 240, "detay": "Özel tereyağlı çıtır hasır."},
            {"ad": "Fıstıkzade", "fiyat": 280, "detay": "Dışı fıstık içi kaymak dolgulu."},
            {"ad": "Katmer", "fiyat": 300, "detay": "Bol antep fıstıklı ve kaymaklı."},
            {"ad": "Kabak Tatlısı", "fiyat": 120, "detay": "Tahinli ve cevizli servis."},
            {"ad": "Midye Baklava", "fiyat": 200, "detay": "Kaymaklı özel porsiyon."},
            {"ad": "Şöbiyet", "fiyat": 200, "detay": "Geleneksel şöbiyet lezzeti."},
            {"ad": "Fıstık Sarma", "fiyat": 240, "detay": "En taze fıstıklardan sarma."}
        ]
    },
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 9.2, "tıklanma": 0,
        "icerik": "Günün her saati kaliteli yakıt ve market hizmeti.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu Üzeri", "saatler": "24 Saat Açık",
        "urunler": [
            {"ad": "Kurşunsuz Benzin (Litre)", "fiyat": 60, "detay": "V-Max Performans Serisi."},
            {"ad": "Motorin / Dizel (Litre)", "fiyat": 50, "detay": "Pro-Diesel Yakıt."},
            {"ad": "Otogaz / LPG (Litre)", "fiyat": 30, "detay": "Ekonomik ve temiz yakıt."}
        ]
    },
    {
        "ad": "Ferah Kebap", "sektor": "Kebapçı", "sifre": "ferah2026", "puan": 9.8, "tıklanma": 0,
        "icerik": "Zırh kıyması ve Hatay usulü mezeler.",
        "tel": "0326 712 33 44", "adres": "İnönü Caddesi", "saatler": "11:00 - 22:00", "urunler": []
    },
    {
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 10.0, "tıklanma": 0,
        "icerik": "Dörtyol'un yazılım ve teknoloji üssü.",
        "tel": "0531 000 00 00", "adres": "Merkez", "saatler": "09:00 - 20:00", "urunler": []
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

# --- PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
                    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }}
    .main-title {{ font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 12px; text-shadow: 0 0 30px rgba(255,204,0,0.5); }}
    
    /* Leaderboard / Skor Tablosu */
    .leaderboard-box {{
        background: rgba(255, 204, 0, 0.1);
        border: 1px solid #ffcc00;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
    }}
    .leader-row {{
        display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,204,0,0.2);
    }}
    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 6px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }}
    .product-box {{ background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid #444; margin-bottom: 15px; transition: 0.3s; }}
    .product-box:hover {{ background: rgba(255, 204, 0, 0.05); border-color: #ffcc00; }}
    
    .stTabs [data-baseweb="tab"] {{ font-weight: 800; color: #aaa; }}
    .stTabs [aria-selected="true"] {{ color: #ffcc00 !important; }}
    
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.6); padding:40px; border-radius:30px; border:1px solid #ffcc0033; text-align:center;">', unsafe_allow_html=True)
        st.write("<p style='font-family:Playfair Display; font-style:italic; color:#ffcc00; font-size:1.1rem;'>Elite Portal Kapısı 2026</p>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod (dortyol2026)")
        if st.button("PORTALI AKTİF ET"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Kod Hatalı")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["💎 ÇARŞIYI GEZ", "🏛️ KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [{"ad": "Tümü", "ikon": "🌐"}, {"ad": "Tatlıcı", "ikon": "🍯"}, {"ad": "Kebapçı", "ikon": "🔥"}, {"ad": "Sağlık", "ikon": "🏥"}, {"ad": "Ulaşım", "ikon": "🚗"}, {"ad": "Hizmet", "ikon": "🛠️"}, {"ad": "Yatırım", "ikon": "💎"}, {"ad": "Teknoloji", "ikon": "💻"}]

# --- 1. KEŞFET ---
with tabs[0]:
    # Kategori Filtresi
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
        # SKOR TABLOSU (LEADERBOARD)
        filtered_for_leader = [s for s in all_shops if st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat]
        if filtered_for_leader:
            st.markdown(f"### 🏆 {st.session_state.selected_cat} Elite Skor Tablosu")
            st.markdown('<div class="leaderboard-box">', unsafe_allow_html=True)
            top_shops = sorted(filtered_for_leader, key=lambda x: x.get('puan', 0), reverse=True)[:5]
            for idx, s in enumerate(top_shops):
                st.markdown(f"""
                <div class="leader-row">
                    <span><b>{idx+1}.</b> {s.get('ad')}</span>
                    <span style="color:#ffcc00;">⭐ {s.get('puan', 0)} Puan</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # DÜKKAN LİSTESİ
        for s in filtered_for_leader:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem;">{s.get('sektor','').upper()}</span>
                        <span style="color:#ffcc00;">👁️ {s.get('tıklanma', 0)} Ziyaret</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:10px 0;">{s.get('ad','')}</h2>
                    <p style="color:#ddd;">{s.get('icerik','')[:150]}...</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s.get('ad')} Mağazasına Gir", key=f"v_{s.get('id', s.get('ad'))}"):
                st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
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
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:30px;">
                    <h3 style="color:#ffcc00; font-family:Cinzel;">📋 ÜRÜN VE FİYAT LİSTESİ</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Ürün Sıralama
            p_sort = st.selectbox("Sırala", ["Önerilen", "Fiyat: Ucuzdan Pahalıya", "Fiyat: Pahalıdan Ucuza"])
            urun_listesi = shop.get('urunler', [])
            
            if p_sort == "Fiyat: Ucuzdan Pahalıya":
                urun_listesi = sorted(urun_listesi, key=lambda x: x['fiyat'])
            elif p_sort == "Fiyat: Pahalıdan Ucuza":
                urun_listesi = sorted(urun_listesi, key=lambda x: x['fiyat'], reverse=True)

            for item in urun_listesi:
                st.markdown(f"""
                    <div class="product-box">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#ffcc00; letter-spacing:1px;">{item["ad"]}</h4>
                            <span style="background:#ffcc00; color:black; padding:5px 15px; border-radius:10px; font-weight:900;">{item["fiyat"]} ₺</span>
                        </div>
                        <p style="color:#ccc; margin-top:10px; font-size:0.9rem;">{item.get('detay', '')}</p>
                    </div>
                """, unsafe_allow_html=True)

# --- DİĞER SEKMELER (GÜÇLENDİRİLMİŞ) ---
with tabs[1]:
    st.markdown('<div style="background:#ffcc00; padding:40px; border-radius:25px; color:black;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>🏛️ KURUMSAL KAYIT</h2><p style='color:black;'>İşletmenizi kaydedin, profesyonel vitrininizi oluşturun.</p>", unsafe_allow_html=True)
    with st.form("reg_v31"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_pwd = st.text_input("Şifre*", type="password")
        if st.form_submit_button("📜 KAYDI TAMAMLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Elite Mağaza.", "adres": "", "saatler": ""})
                st.success("Başarıyla eklendi!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("### 🔐 Esnaf Paneli Girişi")
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("GİRİŞ YAP"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s.get('ad','').lower() == l_ad.lower() and str(s.get('sifre')) == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
    else:
        st.subheader("📊 Yönetim Dashboard")
        if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Onaylandı.")
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(i.get('ad','')):
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v31.0 Elite Leaderboard</div>", unsafe_allow_html=True)
