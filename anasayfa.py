import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | Ultra Professional",
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
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 5.0, "tıklanma": 1240,
        "icerik": "İleri teknoloji, robotik sistemler ve yapay zeka (AI) yazılım çözümleri merkezi.",
        "tel": "0531 000 00 00", "adres": "Dijital Vadi No:1", "saatler": "09:00 - 20:00",
        "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800",
        "urunler": [{"ad": "AI Sunucu Paketi", "fiyat": 15000, "desc": "Kadir AI Altyapısı"}, {"ad": "Teknik Servis", "fiyat": 500, "desc": "Hızlı Çözüm"}]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 4.9, "tıklanma": 3500,
        "icerik": "Tescilli kral hasırı ve odun ateşinde hazırlanan eşsiz Hatay künefesi.",
        "tel": "0532 111 22 33", "adres": "Atatürk Cad.", "saatler": "10:00 - 01:00",
        "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800",
        "urunler": [{"ad": "Kral Hasırı", "fiyat": 240, "desc": "Bol Fıstıklı"}, {"ad": "Peynirli Künefe", "fiyat": 180, "desc": "Sıcak Servis"}]
    },
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 4.7, "tıklanma": 850,
        "icerik": "Güvenli yakıt, 24 saat açık market ve ultra hızlı servis noktası.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu", "saatler": "24 Saat Açık",
        "img": "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800",
        "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50, "desc": "V-Max Performans"}, {"ad": "V-Pro Dizel", "fiyat": 50.25, "desc": "Temiz Motor"}]
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 4.8, "tıklanma": 2100,
        "icerik": "Has altın ve pırlantada Dörtyol'un yarım asırlık güven kapısı.",
        "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı", "saatler": "08:30 - 18:30",
        "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=800",
        "urunler": [{"ad": "Gram Altın (24 Ayar)", "fiyat": 3150, "desc": "Sertifikalı Yatırım"}]
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

# --- ULTRA PROFESSIONAL CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800;900&display=swap');
    
    .stApp {{ 
        background-color: #FF8C00; /* İstediğin Turuncu Arka Plan */
        font-family: 'Poppins', sans-serif; 
    }}

    /* Global Yazı Rengi - Derin Mavi (En Yüksek Okunabilirlik) */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small {{
        color: #001F3F !important;
    }}

    /* Ana Başlık */
    .main-title {{ 
        font-weight: 900; 
        color: #001F3F !important; 
        font-size: 3.8rem; 
        text-align: center; 
        margin-top: -80px;
        text-transform: uppercase;
        letter-spacing: -3px;
        line-height: 1;
    }}

    /* Profesyonel Kartlar */
    .business-card {{ 
        background: white; 
        border-radius: 30px; 
        padding: 0; 
        margin-bottom: 30px; 
        transition: 0.4s ease;
        border: 4px solid #001F3F;
        overflow: hidden;
        box-shadow: 12px 12px 0px #001F3F; /* Retro-Modern Çizgi */
    }}
    .business-card:hover {{ 
        transform: translate(-4px, -4px);
        box-shadow: 18px 18px 0px #001F3F;
    }}

    .card-content {{ padding: 30px; }}

    /* Kategori Butonları - Her Zaman Görünür ve Okunaklı */
    .stButton>button {{
        background-color: #001F3F !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 18px 25px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        border: 3px solid #001F3F !important;
        transition: 0.3s !important;
        width: 100%;
        display: block;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stButton>button:hover {{
        background-color: #FFFFFF !important;
        color: #001F3F !important;
        border: 3px solid #001F3F !important;
        transform: translateY(-3px);
    }}

    /* Seçili Kategori / Tab İyileştirmesi */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #001F3F;
        border-radius: 25px;
        padding: 8px;
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #FF8C00 !important;
        font-weight: 800 !important;
        padding: 10px 20px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #FF8C00 !important;
        color: #001F3F !important;
        border-radius: 18px;
    }}

    /* Input Alanları - Google Temizliğinde */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: white !important;
        color: #001F3F !important;
        border: 4px solid #001F3F !important;
        border-radius: 20px !important;
        padding: 15px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    /* Fiyat Kutusu */
    .price-tag {{ 
        background: #001F3F; 
        color: #FFFFFF !important; 
        padding: 10px 20px; 
        border-radius: 15px; 
        font-weight: 900; 
        font-size: 1.3rem; 
        display: inline-block;
    }}

    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ EKRANI (FULL PROFESYONEL) ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.8, 2])
    with col_log:
        st.markdown(f'''
            <div style="background:white; padding:50px; border-radius:40px; border:6px solid #001F3F; box-shadow: 20px 20px 0px #001F3F; text-align:center;">
                <h2 style="font-weight:900; margin-bottom:20px;">Elite Giriş</h2>
                <p style="font-weight:700; margin-bottom:30px;">Dörtyol'un dijital anahtarıyla içeri girin.</p>
            </div>
        ''', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kodu Buraya Yazın")
        if st.button("PORTALI AÇ VE KEŞFET"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Erişim Reddedildi!")
    st.stop()

# --- ANA PORTAL ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["🏛️ ÇARŞI MEYDANI", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET (ÇARŞI MEYDANI) ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ürün, dükkan veya kategori adı yazın...", key="search_v41")
    
    st.markdown("<h4 style='font-weight:900; margin-bottom:15px;'>HIZLI KATEGORİLER</h4>", unsafe_allow_html=True)
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Hizmet", "Yatırım", "Teknoloji"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"c_v41_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    st.divider()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        
        for s in filtered:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2.5])
            with c1:
                st.image(s.get('img', ""), use_container_width=True)
            with c2:
                st.markdown(f"""
                <div class="card-content">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="background:#FF8C00; color:#001F3F; font-weight:900; font-size:0.8rem; padding:6px 15px; border-radius:50px; border:2px solid #001F3F;">{s.get('sektor','').upper()}</span>
                        <span style="font-weight:900; font-size:1.2rem;">⭐ {s.get('puan', 0)}</span>
                    </div>
                    <h2 style="margin:15px 0; font-weight:900; font-size:2.4rem; letter-spacing:-2px;">{s.get('ad','')}</h2>
                    <p style="font-size:1.1rem; font-weight:600; margin-bottom:20px; color:#333;">{s.get('icerik','')[:160]}...</p>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <small style="font-weight:900; opacity:0.7;">👁️ {s.get('tıklanma', 0)} GÖRÜNTÜLENME</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Mağazayı Gez: {s.get('ad')} →", key=f"v_v41_{s.get('id', s.get('ad'))}"):
                    st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                    if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DETAY SAYFASI
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("← KEŞFETE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.image(shop.get('img',''), use_container_width=True)
            st.markdown(f"<h1 style='font-weight:900; font-size:4rem; margin-top:20px;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:#001F3F; padding:30px; border-radius:30px; border:4px solid #001F3F; display:flex; gap:40px;">
                    <span style="color:#FF8C00 !important; font-weight:900; font-size:1.2rem;">📍 {shop.get('adres','')}</span> 
                    <span style="color:#FF8C00 !important; font-weight:900; font-size:1.2rem;">🕒 {shop.get('saatler','')}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='margin-top:40px; font-weight:900;'>📦 GÜNCEL ÜRÜN VE FİYAT KATALOĞU</h3>", unsafe_allow_html=True)
            for item in shop.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; border:4px solid #001F3F; padding:30px; border-radius:30px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; box-shadow: 8px 8px 0px #001F3F;">
                    <div>
                        <span style="font-weight:900; font-size:1.5rem; display:block;">{item['ad']}</span>
                        <p style="font-weight:700; opacity:0.7; margin:0;">{item.get('desc','Mevcut Ürün')}</p>
                    </div>
                    <span class="price-tag">{item['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.button(f"💬 WHATSAPP SİPARİŞ HATTI: {shop.get('tel','0326')}", use_container_width=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown('<div style="background:white; padding:60px; border-radius:40px; border:8px solid #001F3F; box-shadow: 25px 25px 0px #001F3F;">', unsafe_allow_html=True)
    st.markdown("<h2 style='font-weight:900; font-size:3rem; margin-bottom:10px;'>İşletmenizi Elite Sisteme Dahil Edin</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; margin-bottom:40px;'>Dörtyol'un en büyük dijital pazar yerinde yerinizi alarak kazancınızı artırın.</p>", unsafe_allow_html=True)
    with st.form("reg_v41"):
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("Dükkan Resmi Adı*")
        n_sek = c2.selectbox("Sektör*", cats[1:])
        n_pwd = c1.text_input("Yönetim Şifresi*", type="password")
        n_tel = c2.text_input("WhatsApp İletişim No*")
        n_icr = st.text_area("İşletme Tanıtım Yazısı (En az 30 kelime)")
        if st.form_submit_button("📜 KURUMSAL BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({
                    "ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "tel": n_tel, "puan": 0, "tıklanma": 0, 
                    "urunler": [], "icerik": n_icr, "adres": "Dörtyol Merkez", "saatler": "09:00-19:00", 
                    "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"
                })
                st.success("Tebrikler! Dükkanınız Elite ağımıza başarıyla eklendi."); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
        st.markdown("### 🔐 Esnaf Dashboard Girişi")
        l_ad = st.text_input("Dükkan İsminiz", placeholder="Antik Kral Künefe...")
        l_pwd = st.text_input("Panel Şifreniz", type="password")
        if st.button("YÖNETİM PANELİNİ AÇ"):
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Giriş bilgileri hatalı!")
    else:
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
            with st.expander("➕ Menüye Yeni Ürün/Hizmet Ekle"):
                u_n = st.text_input("Ürün Adı")
                u_p = st.number_input("Satış Fiyatı (TL)", min_value=0.0)
                if st.button("YAYINLA VE VİTRİNE KOY"):
                    prods = d.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p})
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Ürün anında müşterilere sunuldu!"); time.sleep(1); st.rerun()
            if st.button("🚪 PANELİ GÜVENLİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Süper Admin Modu Aktif.")
        for i in all_shops:
            with st.expander(f"⚙️ {i.get('ad','')} Denetim"):
                st.write(f"Şifre: **{i.get('sifre')}** | Toplam Tıklanma: **{i.get('tıklanma')}**")
                if st.button(f"KAYDI SİL: {i.get('ad')}", key=f"del_v41_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; font-weight:900; color:#001F3F;'>© {GUNCEL_YIL} Albayrax Dijital Hub | v41.0 Ultra Professional Edition</div>", unsafe_allow_html=True)
