import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite Power",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- FIREBASE BAĞLANTISI VE STORAGE HATASI KESİN ÇÖZÜM ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            p_id = key_dict.get("project_id")
            
            # Firebase Bucket adını tahmin ediyoruz (Genelde bu ikisinden biridir)
            # Eğer secrets içinde 'storage_bucket' tanımladıysan onu kullanırız.
            b_name = st.secrets["firebase"].get("storage_bucket", f"{p_id}.firebasestorage.app")
            
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': b_name
            })
    except Exception as e:
        st.error(f"Firebase başlatma hatası: {e}")

db = None
col_ref = None
bucket = None

if firebase_admin._apps:
    try:
        db = firestore.client()
        col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
        
        # Hatalı olan satır düzeltildi: Bucket ismi açıkça belirtiliyor
        key_dict = json.loads(st.secrets["firebase"]["key"])
        p_id = key_dict.get("project_id")
        
        # Sırayla deniyoruz
        try:
            bucket = storage.bucket(f"{p_id}.firebasestorage.app")
        except:
            try:
                bucket = storage.bucket(f"{p_id}.appspot.com")
            except:
                bucket = storage.bucket() # Son çare
    except:
        pass

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

# --- DÖRTYOL ÖZEL VERİ TABANI ---
DORTYOL_DATABASE = [
    {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 9.9, "tıklanma": 0, "icerik": "Dörtyol'un meşhur kral hasırı ve tescilli künefe lezzeti.", "tel": "0532 111 22 33", "adres": "Atatürk Caddesi", "saatler": "10:00 - 00:00", "urunler": []},
    {"ad": "Ferah Kebap", "sektor": "Kebapçı", "sifre": "ferah2026", "puan": 9.8, "tıklanma": 0, "icerik": "Yılların eskitemediği zırh kıyması ve Hatay usulü mezeler.", "tel": "0326 712 33 44", "adres": "İnönü Caddesi", "saatler": "11:00 - 22:00", "urunler": []},
    {"ad": "Dörtyol Devlet Hastanesi", "sektor": "Sağlık", "sifre": "saglik2026", "puan": 10.0, "tıklanma": 0, "icerik": "Bölge halkına kesintisiz sağlık hizmeti sunan merkezimiz.", "tel": "0326 712 12 12", "adres": "Numune Evler Mah.", "saatler": "24 Saat Açık", "urunler": []},
    {"ad": "Dörtyol Taksi", "sektor": "Ulaşım", "sifre": "taksi2026", "puan": 9.4, "tıklanma": 0, "icerik": "Güvenli ve hızlı ulaşımın adresi. 7/24 hizmet.", "tel": "0544 555 44 33", "adres": "Çarşı Durak", "saatler": "24 Saat Açık", "urunler": []},
    {"ad": "Kadir Usta", "sektor": "Hizmet", "sifre": "kadir2026", "puan": 9.2, "tıklanma": 0, "icerik": "Teknik servis ve her türlü tamirat işlerinde usta eller.", "tel": "0505 111 22 33", "adres": "Sanayi Sitesi", "saatler": "08:30 - 18:00", "urunler": []},
    {"ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 9.9, "tıklanma": 0, "icerik": "Has altın ve mücevheratta güvenilir yatırımın adresi.", "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı", "saatler": "09:00 - 18:30", "urunler": []},
    {"ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 10.0, "tıklanma": 0, "icerik": "Yazılım, donanım ve teknik destek merkezi.", "tel": "0531 000 00 00", "adres": "Dörtyol Merkez", "saatler": "09:00 - 20:00", "urunler": []}
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
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
                    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }}
    .main-title {{ font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 12px; text-shadow: 0 0 30px rgba(255,204,0,0.5); }}
    
    /* Kurumsal Kayıt - Turuncu Tema */
    .corporate-box {{
        background: #ffcc00;
        padding: 40px;
        border-radius: 25px;
        color: #000000;
        box-shadow: 0 15px 40px rgba(255, 204, 0, 0.3);
    }}
    .corporate-box h2, .corporate-box p, .corporate-box label {{ color: #000000 !important; font-weight: 800; }}

    .business-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; border-left: 5px solid #ffcc00; padding: 25px; margin-bottom: 15px; border-top: 1px solid #333; }}
    .product-box {{ background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid #444; margin-bottom: 15px; }}
    
    /* Sekme Başlıkları */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
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
        st.markdown('<div style="background:rgba(0,0,0,0.6); padding:30px; border-radius:30px; border:1px solid #ffcc0044; text-align:center;">', unsafe_allow_html=True)
        st.write("<p style='font-family:Playfair Display; font-style:italic; color:#ffcc00; font-size:1.1rem;'>Elite Portal Kapısı</p>", unsafe_allow_html=True)
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
            if st.button(f"🏪 {s.get('ad')} İncele", key=f"v_{s.get('id', s.get('ad'))}"):
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
                    <p style="font-style:italic; color:#bbb;">"{shop.get('icerik','')}"</p>
                    <div style="display:flex; justify-content:center; gap:15px; margin-top:15px;">
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">📍 {shop.get('adres','')}</span>
                        <span style="background:#222; padding:5px 15px; border-radius:50px; font-size:0.8rem; border:1px solid #ffcc00;">🕒 {shop.get('saatler','')}</span>
                    </div>
                </div>
                <h3 style="color:#ffcc00; margin-top:40px; font-family:Cinzel; text-align:center;">📋 ÜRÜN VE HİZMET KATALOĞU</h3>
            """, unsafe_allow_html=True)
            for item in shop.get('urunler', []):
                u1, u2 = st.columns([1, 4])
                with u1:
                    if item.get('img'): st.image(item['img'], use_container_width=True)
                    else: st.markdown("🖼️ Foto")
                with u2:
                    st.markdown(f'<div class="product-box"><h4>{item["ad"]}</h4><p>{item["detay"]}</p><b>{item["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown('<div class="corporate-box">', unsafe_allow_html=True)
    st.markdown("<h2>🏛️ DİJİTAL ÇARŞI'DA YERİNİZİ ALIN</h2>", unsafe_allow_html=True)
    st.markdown("<p>İşletmenizi kaydedin, Dörtyol'un dijital geleceğine dahil olun.</p>", unsafe_allow_html=True)
    with st.form("corporate_reg_v30"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("Dükkan Resmi Adı*")
            n_tel = st.text_input("Kurumsal İletişim*")
        with c2:
            n_sek = st.selectbox("Sektör Seçin", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_icr = st.text_area("İşletme Tanıtım Yazısı")
        if st.form_submit_button("📜 KAYDI TAMAMLA VE YAYINLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": n_icr, "adres": "", "saatler": ""})
                st.success("Başarıyla kaydedildi!"); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİMİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Kadir Teknoloji)")
        l_pwd = st.text_input("Şifre (tekno2026)", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s.get('ad','').lower() == l_ad.lower() and str(s.get('sifre')) == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Hatalı Giriş!")
    else:
        shop_id = st.session_state.owner_shop_id
        all_s = verileri_yukle()
        d = next((s for s in all_s if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
            with st.expander("🏠 Dükkan Profilini Düzenle"):
                u_adr = st.text_input("Adres", value=d.get('adres',''))
                u_saat = st.text_input("Çalışma Saatleri", value=d.get('saatler',''))
                u_tan = st.text_area("Tanıtım Yazısı", value=d.get('icerik',''))
                if st.button("PROFİLİ KAYDET"):
                    col_ref.document(d['id']).update({"adres": u_adr, "saatler": u_saat, "icerik": u_tan})
                    st.success("Profil güncellendi!"); st.rerun()
            
            with st.expander("➕ Menüye Yeni Ürün/Hizmet Ekle"):
                u_ad = st.text_input("Ürün Adı")
                u_fiy = st.number_input("Fiyat (₺)", min_value=0)
                u_img_file = st.file_uploader("Ürün Fotoğrafı Yükle", type=['png', 'jpg', 'jpeg'])
                u_det = st.text_input("Kısa Özet")
                if st.button("ÜRÜNÜ YAYINLA"):
                    with st.spinner("Görsel yükleniyor..."):
                        img_url = resim_yukle(d['ad'], u_img_file) if u_img_file else None
                        prods = d.get('urunler', [])
                        prods.append({"ad": u_ad, "fiyat": u_fiy, "detay": u_det, "img": img_url})
                        col_ref.document(d['id']).update({"urunler": prods})
                        st.success("Ürün vitrine eklendi!"); time.sleep(1); st.rerun()
            
            if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Girişi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Aktif!")
        with st.expander("➕ Sisteme Manuel Dükkan Ekle"):
            a_ad = st.text_input("İşletme Adı")
            a_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"], key="admin_sek")
            a_pwd = st.text_input("Esnaf Şifresi")
            if st.button("DÜKKANI OLUŞTUR"):
                col_ref.add({"ad": a_ad, "sektor": a_sek, "sifre": a_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Admin tarafından eklendi.", "adres": "", "saatler": ""})
                st.success("Dükkan eklendi!"); st.rerun()
        
        st.divider()
        all_d = verileri_yukle()
        for i in all_d:
            with st.expander(f"⚙️ {i.get('ad','')} (Şifre: {i.get('sifre')})"):
                if st.button(f"SİL: {i.get('ad')}", key=f"del_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

# --- İLETİŞİM & FOOTER ---
st.markdown(f"""
    <div style='text-align:center; padding-top:100px; padding-bottom:50px; opacity:0.6; font-size:0.8rem;'>
        <hr style="border-color:#ffcc0033;">
        <b>📞 Kurumsal İletişim:</b> 0326 712 00 00 | <b>📍 Adres:</b> Dörtyol, Hatay<br>
        © {GUNCEL_YIL} Albayrax Elite Portal | v30.0 Final Power Edition
    </div>
    """, unsafe_allow_html=True)
