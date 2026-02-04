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
    page_title="Dörtyol Esnaf Portalı | 2026 Elite Marketplace",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- FIREBASE BAĞLANTISI VE STORAGE AYARI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            project_id = key_dict.get("project_id")
            # Hem .appspot.com hem de .firebasestorage.app formatlarını desteklemek için
            bucket_name = f"{project_id}.firebasestorage.app" 
            
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': bucket_name
            })
    except Exception as e:
        pass # Sessizce geçiyoruz, hata mesajlarını UI'da yönetiyoruz

db = None
col_ref = None
bucket = None

try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
    # Bucket'ı tekrar kontrol ederek güvenli şekilde bağlıyoruz
    firebase_config = json.loads(st.secrets["firebase"]["key"])
    p_id = firebase_config.get('project_id')
    bucket = storage.bucket(f"{p_id}.firebasestorage.app")
except:
    try:
        bucket = storage.bucket(f"{p_id}.appspot.com")
    except:
        pass

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop_id': None,
    'owner_shop_id': None,
    'sort_by': "En Yüksek Puan"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- KÜFÜR FİLTRESİ ---
KOTU_SOZLER = ["argo1", "kufur2"] 
def icerik_temizle(metin):
    if not metin: return ""
    for kelime in KOTU_SOZLER:
        metin = re.sub(re.escape(kelime), "***", metin, flags=re.IGNORECASE)
    return metin

# --- FONKSİYONLAR ---
def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            return [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: return []
    return []

def resim_yukle(shop_name, file_obj):
    if bucket and file_obj:
        try:
            file_ext = file_obj.name.split('.')[-1]
            blob_path = f"shops/{shop_name}/{int(time.time())}.{file_ext}"
            blob = bucket.blob(blob_path)
            blob.upload_from_string(file_obj.getvalue(), content_type=file_obj.type)
            blob.make_public()
            return blob.public_url
        except Exception:
            return None
    return None

# --- PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)), 
                    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }}
    .main-title {{ font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 12px; text-shadow: 0 0 30px rgba(255,204,0,0.5); }}
    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 5px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }}
    .product-box {{ background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid #444; margin-bottom: 15px; }}
    .discount-tag {{ background: #ff0000; color: #fff; padding: 3px 10px; border-radius: 5px; font-weight: 900; font-size: 0.8rem; }}
    .price-tag {{ color: #00ff00; font-weight: 900; font-size: 1.3rem; }}
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
        st.write("<p style='font-family:Playfair Display; font-style:italic; color:#ffcc00; font-size:1.2rem;'>Hoş Geldiniz, Elite Portal Girişi</p>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod")
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
        if not filtered:
            st.info(f"{st.session_state.selected_cat} kategorisinde henüz dükkan bulunmuyor.")
        for s in filtered:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem;">{s.get('sektor','DİĞER').upper()}</span>
                        <span style="color:#ffcc00;">⭐ {s.get('puan', 0)} / 10</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:10px 0;">{s.get('ad','İsimsiz')}</h2>
                    <p style="color:#ddd;">{s.get('icerik','')[:120]}...</p>
                    <small style="color:#666;">👁️ {s.get('tıklanma', 0)} Ziyaret</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s.get('ad')} Mağazasına Gir", key=f"v_{s['id']}"):
                st.session_state.selected_shop_id = s['id']
                if col_ref: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        shop = next((s for s in all_shops if s['id'] == st.session_state.selected_shop_id), None)
        if st.button("⬅️ LİSTEYE GERİ DÖN"): 
            st.session_state.selected_shop_id = None
            st.rerun()
        
        if shop:
            st.markdown(f"""
                <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:35px; border:2px solid #ffcc00; text-align:center;">
                    <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{shop.get('ad','')}</h1>
                    <p style="font-style:italic; color:#bbb;">"{shop.get('icerik','')}"</p>
                    <div style="display:flex; justify-content:center; gap:15px; margin-top:15px;">
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">📍 {shop.get('adres','Belirtilmemiş')}</span>
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">🕒 {shop.get('saatler','Belirtilmemiş')}</span>
                    </div>
                </div>
                <h3 style="color:#ffcc00; margin-top:40px; font-family:Cinzel;">📋 ÜRÜN KATALOĞU</h3>
            """, unsafe_allow_html=True)
            
            for item in shop.get('urunler', []):
                u1, u2 = st.columns([1, 4])
                with u1:
                    if item.get('img'): st.image(item['img'], use_container_width=True)
                    else: st.markdown("🖼️ Fotoğraf Yok")
                with u2:
                    disc = 0
                    fiy = float(item.get('fiyat', 0))
                    e_fiy = float(item.get('eski_fiyat', 0))
                    if e_fiy > fiy:
                        disc = int((1 - (fiy / e_fiy)) * 100)
                    
                    st.markdown(f"""
                        <div class="product-box">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h4 style="margin:0; color:#ffcc00;">{item.get('ad','')}</h4>
                                <div>
                                    {f'<span style="text-decoration:line-through; color:#777; font-size:0.8rem; margin-right:10px;">{int(e_fiy)} ₺</span>' if disc > 0 else ''}
                                    {f'<span class="discount-tag">%{disc} İNDİRİM</span>' if disc > 0 else ''}
                                    <span class="price-tag">{int(fiy)} ₺</span>
                                </div>
                            </div>
                            <p style="color:#ccc; font-size:0.9rem; margin-top:5px;">{item.get('detay','')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📜 Bilgi & Tarihçe"): st.write(item.get('tarihce', '-'))
            
            st.divider()
            st.markdown("### 💬 Müşteri Yorumları")
            for y in shop.get('yorumlar', []):
                st.markdown(f"**👤 Misafir:** {y.get('metin','')} <br><small style='color:#666;'>{y.get('tarih','')}</small>", unsafe_allow_html=True)
            
            with st.form("comment_v26"):
                y_text = st.text_area("Yorum Yazın")
                if st.form_submit_button("GÖNDER"):
                    if y_text:
                        current_y = shop.get('yorumlar', [])
                        current_y.append({"metin": icerik_temizle(y_text), "tarih": datetime.now().strftime("%d/%m/%Y %H:%M")})
                        col_ref.document(shop['id']).update({"yorumlar": current_y})
                        st.success("Yorumunuz paylaşıldı!"); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Duyarsız)", key="login_shop_name")
        l_pwd = st.text_input("Şifre", type="password", key="login_shop_pwd")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s.get('ad','').lower() == l_ad.lower() and str(s.get('sifre')) == l_pwd), None)
            if match: st.session_state.owner_shop_id = match['id']; st.rerun()
            else: st.error("Hatalı Giriş!")
    else:
        shop_id = st.session_state.owner_shop_id
        current_data = verileri_yukle()
        d = next((s for s in current_data if s['id'] == shop_id), None)
        
        if d:
            st.subheader(f"📊 {d.get('ad')} Kontrol Merkezi")
            
            with st.expander("🏠 Profil Bilgilerini Güncelle"):
                u_adr = st.text_input("Adres", value=d.get('adres',''))
                u_saat = st.text_input("Çalışma Saatleri", value=d.get('saatler',''))
                u_icr = st.text_area("Tanıtım Yazısı", value=d.get('icerik',''))
                if st.button("PROFİLİ KAYDET"):
                    col_ref.document(shop_id).update({"adres": u_adr, "saatler": u_saat, "icerik": u_icr})
                    st.success("Profil güncellendi!"); time.sleep(1); st.rerun()

            with st.expander("➕ Yeni Ürün Ekle"):
                u_ad = st.text_input("Ürün Adı")
                u_fiy = st.number_input("Satış Fiyatı (₺)", min_value=0, value=0)
                u_efiy = st.number_input("Eski Fiyat (İsteğe Bağlı)", min_value=0, value=0)
                u_file = st.file_uploader("Ürün Fotoğrafı", type=['png', 'jpg', 'jpeg'])
                u_det = st.text_input("Kısa Özet")
                u_tar = st.text_area("Teknik Bilgiler / Tarihçe")
                
                if st.button("ÜRÜNÜ YAYINLA"):
                    with st.spinner("İşleniyor..."):
                        img_url = resim_yukle(d.get('ad','shop'), u_file) if u_file else None
                        prods = d.get('urunler', [])
                        prods.append({
                            "ad": u_ad, "fiyat": float(u_fiy), "eski_fiyat": float(u_efiy), 
                            "img": img_url, "detay": u_det, "tarihce": u_tar
                        })
                        col_ref.document(shop_id).update({"urunler": prods})
                        st.success("Ürün vitrine çıktı!"); time.sleep(1); st.rerun()

            if st.button("🚪 PANELİ KAPAT"):
                st.session_state.owner_shop_id = None
                st.rerun()

# --- DİĞERLERİ ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_v26"):
        n_ad = st.text_input("İşletme Adı*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_pwd = st.text_input("Giriş Şifresi*", type="password")
        if st.form_submit_button("📜 KAYIT OL"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({
                    "ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, 
                    "tıklanma": 0, "urunler": [], "yorumlar": [], "icerik": "Elite Mağaza.", 
                    "adres": "", "saatler": ""
                })
                st.success("Başarılı!"); time.sleep(1); st.rerun()

with tabs[3]:
    pwd = st.text_input("Admin", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(i.get('ad','İsimsiz')):
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i['id']}"):
                    col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v26.0 Global Fix</div>", unsafe_allow_html=True)
