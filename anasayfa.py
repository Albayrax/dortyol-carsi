import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re
import io

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite Security",
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
            # Storage Bucket ismini de secrets içinden alıyoruz
            firebase_admin.initialize_app(cred, {
                'storageBucket': st.secrets["firebase"].get("storage_bucket", f"{APP_ID}.appspot.com")
            })
    except:
        pass

db = firestore.client() if firebase_admin._apps else None
col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar") if db else None
bucket = storage.bucket() if firebase_admin._apps else None

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- GERÇEKÇİ DÖRTYOL BAŞLANGIÇ VERİLERİ ---
def ilk_kurulum():
    # Eğer DB tamamen boşsa bu dükkanları bir kez yükle
    test_data = [
        {"ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "icerik": "Dörtyol'un yazılım ve donanım merkezi.", "tel": "0531 000 00 00", "puan": 10.0, "tıklanma": 0, "urunler": []},
        {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "icerik": "Kral hasırının tek adresi.", "tel": "0532 000 00 00", "puan": 9.9, "tıklanma": 0, "urunler": []},
        {"ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "icerik": "Has altın ve mücevherat güvencesi.", "tel": "0533 000 00 00", "puan": 9.8, "tıklanma": 0, "urunler": []}
    ]
    if col_ref:
        docs = col_ref.limit(1).get()
        if len(docs) == 0:
            for item in test_data: col_ref.add(item)

if col_ref: ilk_kurulum()

# --- FONKSİYONLAR ---
def verileri_yukle():
    if col_ref:
        docs = col_ref.stream()
        return [dict(doc.to_dict(), id=doc.id) for doc in docs]
    return []

def resim_yukle(shop_name, file_obj):
    if bucket and file_obj:
        file_ext = file_obj.name.split('.')[-1]
        blob_path = f"shops/{shop_name}/{int(time.time())}.{file_ext}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(file_obj.getvalue(), content_type=file_obj.type)
        blob.make_public()
        return blob.public_url
    return None

# --- PREMIUM UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("https://images.unsplash.com/photo-1439405326854-014607f694d7?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }
    .main-title { font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 12px; text-shadow: 0 0 30px rgba(255,204,0,0.4); }
    .business-card { background: rgba(255,255,255,0.03); border-radius: 20px; border-left: 6px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }
    .product-box { background: rgba(0,0,0,0.4); padding: 15px; border-radius: 20px; border: 1px solid #333; margin-bottom: 15px; }
    .price-tag { background: #ffcc00; color: #000; padding: 2px 10px; border-radius: 5px; font-weight: 800; }
    .discount-tag { background: #ff0000; color: #fff; padding: 2px 10px; border-radius: 5px; font-size: 0.7rem; font-weight: 900; }
    code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, log_col, _ = st.columns([2, 1.2, 2])
    with log_col:
        st.markdown('<div style="background:rgba(0,0,0,0.6); padding:30px; border-radius:30px; border:1px solid #ffcc0044; text-align:center;">', unsafe_allow_html=True)
        st.write("<i style='color:#ffcc00;'>Hoş Geldiniz, Elite Portal Kapısı</i>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod")
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
        # Filtreleme
        filtered = [s for s in all_shops if st.session_state.selected_cat == "Tümü" or s['sektor'] == st.session_state.selected_cat]
        for s in filtered:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem;">{s['sektor'].upper()}</span>
                        <span style="color:#ffcc00;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:5px 0;">{s['ad']}</h2>
                    <p style="color:#ddd;">{s.get('icerik','')[:100]}...</p>
                    <small style="color:#666;">👁️ {s.get('tıklanma', 0)} Ziyaret</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s['ad']} Mağazasına Gir", key=f"v_{s['id']}"):
                st.session_state.selected_shop_id = s['id']
                if col_ref: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # Dükkan Detay
        shop = next((s for s in all_shops if s['id'] == st.session_state.selected_shop_id), None)
        if st.button("⬅️ LİSTEYE GERİ DÖN"): 
            st.session_state.selected_shop_id = None
            st.rerun()
        
        if shop:
            st.markdown(f"""
                <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:30px; border:2px solid #ffcc00; text-align:center;">
                    <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{shop['ad']}</h1>
                    <p style="font-style:italic; color:#bbb;">"{shop.get('icerik','')}"</p>
                </div>
                <h3 style="color:#ffcc00; margin-top:40px;">📋 ÜRÜN KATALOĞU</h3>
            """, unsafe_allow_html=True)
            
            for item in shop.get('urunler', []):
                u_col1, u_col2 = st.columns([1, 4])
                with u_col1:
                    if item.get('img'): st.image(item['img'], use_container_width=True)
                    else: st.markdown("🖼️ Fotoğraf Yok")
                with u_col2:
                    disc_pct = 0
                    if item.get('eski_fiyat') and item.get('eski_fiyat') > item['fiyat']:
                        disc_pct = int((1 - (item['fiyat'] / item['eski_fiyat'])) * 100)
                    
                    st.markdown(f"""
                        <div class="product-box">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h4 style="margin:0; color:#ffcc00;">{item['ad']}</h4>
                                <div>
                                    {f'<span style="text-decoration:line-through; color:#777; font-size:0.8rem; margin-right:10px;">{item["eski_fiyat"]} ₺</span>' if disc_pct > 0 else ''}
                                    {f'<span class="discount-tag">%{disc_pct} İNDİRİM</span>' if disc_pct > 0 else ''}
                                    <span class="price-tag">{item['fiyat']} ₺</span>
                                </div>
                            </div>
                            <p style="color:#ccc; font-size:0.9rem; margin-top:5px;">{item.get('detay','')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📜 Teknik Bilgiler & Tarihçe"): st.write(item.get('tarihce', 'Bilgi girilmemiş.'))

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Büyük/Küçük harf duyarsız)")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'].lower() == l_ad.lower() and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match['id']; st.rerun()
            else: st.error("Hatalı giriş!")
    else:
        # ESNAF DASHBOARD
        shop_id = st.session_state.owner_shop_id
        current_shops = verileri_yukle()
        d = next((s for s in current_shops if s['id'] == shop_id), None)
        
        st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
        
        with st.expander("➕ Menüye Yeni Ürün Ekle (Görsel Yükleme Destekli)"):
            u_ad = st.text_input("Ürün Adı")
            u_fiy = st.number_input("Güncel Satış Fiyatı (₺)", min_value=0)
            u_efiy = st.number_input("Eski Fiyat (İsteğe Bağlı)", min_value=0)
            u_file = st.file_uploader("Ürün Fotoğrafı Seç (Sadece senin dükkanında saklanır)", type=['png', 'jpg', 'jpeg'])
            u_det = st.text_input("Kısa Özet")
            u_tar = st.text_area("Teknik Bilgiler / Açıklama")
            
            if st.button("ÜRÜNÜ YAYINLA"):
                with st.spinner("Dosya güvenli bölgeye yükleniyor..."):
                    img_url = resim_yukle(d['ad'], u_file) if u_file else None
                    prods = d.get('urunler', [])
                    prods.append({
                        "ad": u_ad, "fiyat": u_fiy, "eski_fiyat": u_efiy, 
                        "img": img_url, "detay": u_det, "tarihce": u_tar
                    })
                    col_ref.document(shop_id).update({"urunler": prods})
                    st.success("Tebrikler! Ürün vitrine çıktı.")
                    time.sleep(1)
                    st.rerun()

        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- DİĞER SEKMELER (SABİT) ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_v24"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_pwd = st.text_input("Giriş Şifresi*", type="password")
        if st.form_submit_button("📜 KAYIT OL"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Dörtyol Elite Mağazası."})
                st.success("Başarılı!"); time.sleep(1); st.rerun()

with tabs[3]:
    pwd = st.text_input("Admin", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(i['ad']):
                if st.button(f"SİL: {i['ad']}", key=f"del_{i['id']}"):
                    col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v24.0 Secure Storage</div>", unsafe_allow_html=True)
