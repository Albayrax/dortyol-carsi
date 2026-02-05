import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Price War",
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

# --- VERİ TABANI YÜKLEME ---
def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            # Eğer DB boşsa statik verileri döndür
            if not data:
                return [
                    {"ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 9.5, "tıklanma": 0, "icerik": "Kaliteli yakıtın adresi.", "tel": "0326 712 00 00", "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}]},
                    {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "shell2026", "puan": 9.2, "tıklanma": 0, "icerik": "V-Power Farkı.", "tel": "0326 712 11 11", "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 61.20}]},
                    {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 9.9, "tıklanma": 0, "icerik": "Efsane lezzet.", "tel": "0532 111 22 33", "urunler": [{"ad": "Künefe", "fiyat": 180}]}
                ]
            return data
        except: return []
    return []

# --- PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), 
                    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }}
    .main-title {{ font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 10px; }}
    .war-box {{ background: linear-gradient(90deg, #ff4b2b, #ff416c); color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 2px solid white; }}
    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 6px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }}
    .price-tag {{ background: #ffcc00; color: #000; padding: 5px 15px; border-radius: 10px; font-weight: 900; font-size: 1.2rem; }}
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.6); padding:30px; border-radius:30px; border:1px solid #ffcc0033; text-align:center;">', unsafe_allow_html=True)
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("SİSTEME GİR"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- ANA SAYFA ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI MEYDANI", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # REKABET VİTRİNİ (PRICE WAR)
    st.markdown("### 🔥 Dörtyol'un En Ucuzu (Günün Savaşçıları)")
    fuel_prices = []
    for s in all_shops:
        for u in s.get('urunler', []):
            if "Benzin" in u['ad'] or "95" in u['ad']:
                fuel_prices.append({"dükkan": s['ad'], "fiyat": u['fiyat']})
    
    if fuel_prices:
        cheapest = min(fuel_prices, key=lambda x: x['fiyat'])
        st.markdown(f"""
            <div class="war-box">
                <h2 style="margin:0;">⛽ EN UCUZ BENZİN ŞU AN BURADA!</h2>
                <p style="font-size:1.5rem; font-weight:900; margin:10px 0;">{cheapest['dükkan']}: {cheapest['fiyat']} ₺</p>
                <small>Fiyatlar anlık esnaf güncellemeleridir.</small>
            </div>
        """, unsafe_allow_html=True)

    # KATEGORİLER
    kategoriler = ["Tümü", "Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Hizmet", "Yatırım", "Teknoloji"]
    cols = st.columns(len(kategoriler))
    for i, cat in enumerate(kategoriler):
        if cols[i].button(cat, key=f"cat_{cat}"):
            st.session_state.selected_cat = cat
            st.session_state.selected_shop_id = None
            st.rerun()

    st.divider()

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
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 Mağazayı İncele: {s.get('ad')}", key=f"v_{s.get('id', s.get('ad'))}"):
                st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("⬅️ LİSTEYE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.markdown(f"<h1 style='color:#ffcc00; text-align:center;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            for item in shop.get('urunler', []):
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0;">{item['ad']}</h4>
                        <div class="price-tag">{item['fiyat']} ₺</div>
                    </div>
                """, unsafe_allow_html=True)

# --- 3. ESNAF PANELİ (GİRİŞ DÜZELTİLDİ) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("### 🔐 Esnaf Yönetim Paneli")
        l_ad = st.text_input("Dükkan Adınız (Kayıtlı isim)")
        l_pwd = st.text_input("Panel Şifreniz", type="password")
        st.info("Test için: Dörtyol Petrol Ofisi / petrol2026")
        if st.button("DASHBOARD'A GİR"):
            # Girişi garantilemek için temizleme yapıyoruz
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match:
                st.session_state.owner_shop_id = match.get('id', match.get('ad'))
                st.rerun()
            else: st.error("Giriş bilgileri hatalı. Lütfen büyük/küçük harfe dikkat edin.")
    else:
        # PANEL İÇERİĞİ
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Yönetim Paneli")
            
            with st.expander("💰 Fiyat Savaşı: Ürün ve Fiyat Güncelle"):
                st.warning("Dikkat: Fiyatı düşürürseniz ana sayfadaki 'En Ucuz' vitrinine çıkabilirsiniz!")
                current_prods = d.get('urunler', [])
                updated_prods = []
                for idx, item in enumerate(current_prods):
                    c1, c2 = st.columns([3, 1])
                    p_name = c1.text_input(f"Ürün {idx+1}", value=item.get('ad',''), key=f"edit_name_{idx}")
                    p_price = c2.number_input(f"Fiyat ₺", value=float(item.get('fiyat',0)), key=f"edit_price_{idx}")
                    updated_prods.append({"ad": p_name, "fiyat": p_price, "detay": item.get('detay','')})
                
                if st.button("DEĞİŞİKLİKLERİ YAYINLA"):
                    if col_ref and 'id' in d:
                        col_ref.document(d['id']).update({"urunler": updated_prods})
                        st.success("Fiyatlar güncellendi ve rekabet kızıştı!")
                        time.sleep(1); st.rerun()

            if st.button("🚪 PANELİ KAPAT"):
                st.session_state.owner_shop_id = None
                st.rerun()

# --- DİĞERLERİ (ADMİN & KAYIT) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center;'>🏛️ YENİ ESNAF KAYDI</h3>", unsafe_allow_html=True)
    with st.form("reg_v33"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör", ["Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Hizmet", "Yatırım", "Teknoloji"])
        n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        if st.form_submit_button("📜 PORTALA KATIL"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Dörtyol Portalı Üyesi.", "adres": "", "saatler": ""})
                st.success("Kaydedildi!"); st.rerun()

with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Onaylandı.")
        for i in all_shops:
            with st.expander(i.get('ad','')):
                st.write(f"Şifre: {i.get('sifre')}")
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v33.0 Price War Edition</div>", unsafe_allow_html=True)
