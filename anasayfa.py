import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Dynamic Edition",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- FIREBASE BAĞLANTISI (GÜVENLİ STORAGE MODU) ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            p_id = key_dict.get("project_id")
            b_name = st.secrets["firebase"].get("storage_bucket", f"{p_id}.firebasestorage.app")
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': b_name})
    except Exception as e:
        st.error(f"Sistem hatası: {e}")

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
    'sort_by': "Elite Puan"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- DÖRTYOL GERÇEK VERİ TABANI (DETAYLI AKARYAKIT) ---
DORTYOL_DATABASE = [
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 9.5, "tıklanma": 0,
        "icerik": "Günün her saati kaliteli yakıt, geniş market alanı ve temiz hizmet.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu Üzeri No:44", "saatler": "24 Saat Açık",
        "urunler": [
            {"ad": "V-Max Kurşunsuz 95", "fiyat": 60.50, "detay": "Performans arttırıcı katkılı benzin."},
            {"#ad": "V-Pro Dizel", "fiyat": 50.20, "detay": "Yeni nesil temiz motorin."},
            {"ad": "PO Gaz / LPG", "fiyat": 30.15, "detay": "Ekonomik ve güvenli otogaz."}
        ]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 9.9, "tıklanma": 0,
        "icerik": "Dörtyol'un tescilli lezzet durağı.",
        "tel": "0532 111 22 33", "adres": "Atatürk Caddesi", "saatler": "10:00 - 00:00",
        "urunler": [
            {"ad": "Künefe", "fiyat": 180, "detay": "Klasik Hatay peynirli."},
            {"ad": "Hasır", "fiyat": 240, "detay": "Özel tereyağlı çıtır hasır."}
        ]
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
    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 6px solid #ffcc00; padding: 25px; margin-bottom: 15px; transition: 0.3s; }}
    .business-card:hover {{ background: rgba(255, 204, 0, 0.05); transform: translateY(-3px); }}
    .price-box {{ background: #ffcc00; color: #000; padding: 5px 15px; border-radius: 10px; font-weight: 900; font-size: 1.2rem; }}
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.6); padding:30px; border-radius:30px; border:1px solid #ffcc0033; text-align:center;">', unsafe_allow_html=True)
        st.write("<p style='color:#ffcc00; font-style:italic;'>Sisteme Giriş Yapın</p>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod (dortyol2026)")
        if st.button("PORTALI AKTİF ET"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Kod")
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
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem; border:1px solid #444; padding:2px 8px; border-radius:5px;">{s.get('sektor','').upper()}</span>
                        <span style="color:#ffcc00;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:5px 0;">{s.get('ad','')}</h2>
                    <p style="color:#ddd; font-size:0.9rem;">{s.get('icerik','')[:150]}...</p>
                    <small style="color:#666;">👁️ {s.get('tıklanma', 0)} Görüntülenme</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s.get('ad')} Detaylarını Gör", key=f"v_{s.get('id', s.get('ad'))}"):
                st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("⬅️ LİSTEYE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.markdown(f"""
                <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:35px; border:2px solid #ffcc00; text-align:center;">
                    <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{shop['ad']}</h1>
                    <p style="color:#ddd; font-style:italic;">"{shop.get('icerik','')}"</p>
                    <p style="font-size:0.8rem; color:#888; margin-top:10px;">🕒 {shop.get('saatler','')} | 📍 {shop.get('adres','')}</p>
                </div>
                <h3 style="color:#ffcc00; margin-top:40px; font-family:Cinzel; text-align:center;">📋 GÜNCEL FİYAT LİSTESİ</h3>
            """, unsafe_allow_html=True)
            
            for item in shop.get('urunler', []):
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border:1px solid #444; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#ffcc00;">{item.get('ad','')}</h4>
                            <p style="margin:5px 0 0 0; font-size:0.8rem; color:#aaa;">{item.get('detay','')}</p>
                        </div>
                        <div class="price-box">{item.get('fiyat', 0)} ₺</div>
                    </div>
                """, unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİMİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Örn: Dörtyol Petrol Ofisi)")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s.get('ad','').lower() == l_ad.lower() and str(s.get('sifre')) == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Giriş Hatalı!")
    else:
        shop_id = st.session_state.owner_shop_id
        all_s = verileri_yukle()
        d = next((s for s in all_s if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
            
            with st.expander("⛽ Fiyatları / Ürünleri Güncelle"):
                st.write("Mevcut ürünlerinizi buradan yönetin.")
                current_prods = d.get('urunler', [])
                new_prods = []
                for idx, item in enumerate(current_prods):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        p_name = st.text_input(f"Ürün {idx+1} Adı", value=item.get('ad',''), key=f"pname_{idx}")
                    with c2:
                        p_price = st.number_input(f"Fiyat (₺)", value=float(item.get('fiyat',0)), key=f"pprice_{idx}")
                    new_prods.append({"ad": p_name, "fiyat": p_price, "detay": item.get('detay','')})
                
                if st.button("TÜM FİYATLARI GÜNCELLE"):
                    col_ref.document(d['id']).update({"urunler": new_prods})
                    st.success("Fiyatlar saniyeler içinde tüm Dörtyol'a yansıdı!")
                    time.sleep(1); st.rerun()

            with st.expander("➕ Yeni Ürün Ekle"):
                u_ad = st.text_input("Yeni Ürün Adı")
                u_fiy = st.number_input("Yeni Ürün Fiyatı", min_value=0.0)
                if st.button("LİSTEYE EKLE"):
                    current_prods.append({"ad": u_ad, "fiyat": u_fiy, "detay": "Yeni ürün."})
                    col_ref.document(d['id']).update({"urunler": current_prods})
                    st.success("Yeni ürün listeye eklendi!"); st.rerun()

            if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- DİĞER SEKMELER (ADMİN & KAYIT) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_v32"):
        n_ad = st.text_input("İşletme Adı*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        if st.form_submit_button("📜 KAYDOL"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Dörtyol Esnafı.", "adres": "", "saatler": ""})
                st.success("Kaydedildi!"); time.sleep(1); st.rerun()

with tabs[3]:
    pwd = st.text_input("Admin", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(f"⚙️ {i.get('ad','')}"):
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('id', i.get('ad'))}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v32.0 Dynamic Pricing</div>", unsafe_allow_html=True)
