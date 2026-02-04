import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | Dijital Esnaf Portalı",
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
            firebase_admin.initialize_app(cred)
    except Exception as e:
        pass # Hataları kullanıcıya yansıtmıyoruz, sadece sessizce geçiyoruz

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_id' not in st.session_state: st.session_state.selected_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- DÖRTYOL GERÇEK ESNAF VERİLERİ (MOCK DATA) ---
DORTYOL_ESNAFLARI = [
    {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "urun": "Meşhur Kral Hasırı", "tel": "0532 123 45 67", "icerik": "Dörtyol'un en köklü lezzet durağında, gerçek peynir ve taze kadayıfın buluşması.", "puan": 9.9, "tıklanma": 850, "yildizli": True},
    {"ad": "Ferah Kebap", "sektor": "Kebapçı", "urun": "Zırh Kıyma Kebap", "tel": "0533 987 65 43", "icerik": "Yılların eskitemediği lezzet. El kıyması kebabın Dörtyol'daki adresi.", "puan": 9.7, "tıklanma": 620, "yildizli": True},
    {"ad": "Dörtyol Devlet Hastanesi", "sektor": "Sağlık", "urun": "Sağlık Hizmetleri", "tel": "0326 712 12 12", "icerik": "Bölge halkına kesintisiz ve güvenilir sağlık hizmeti sunan merkezimiz.", "puan": 10.0, "tıklanma": 1200, "yildizli": False},
    {"ad": "Dörtyol Taksi", "sektor": "Ulaşım", "urun": "7/24 Şehir İçi & Dışı Ulaşım", "tel": "0544 555 44 33", "icerik": "Güvenli, konforlu ve hızlı ulaşımın Dörtyol'daki tek adresi.", "puan": 9.4, "tıklanma": 430, "yildizli": False},
    {"ad": "Kadir Usta Tamirhane", "sektor": "Hizmet", "urun": "Teknik Servis & Bakım", "tel": "0505 111 22 33", "icerik": "Her türlü teknik arıza ve bakım işlerinizde usta işi çözümler.", "puan": 9.1, "tıklanma": 310, "yildizli": False},
    {"ad": "Mavi / LC Waikiki", "sektor": "Giyim", "urun": "Yeni Sezon Koleksiyonları", "tel": "0326 713 00 00", "icerik": "En trend moda ürünleri ve her bütçeye uygun kaliteli giyim seçenekleri.", "puan": 8.8, "tıklanma": 540, "yildizli": False},
    {"ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "urun": "Has Altın & Mücevherat", "tel": "0532 000 00 00", "icerik": "Dörtyol'da güvenin adresi. Yatırımlarınızı değerinde koruyan kuyumcu mağazası.", "puan": 9.8, "tıklanma": 710, "yildizli": True}
]

# --- FONKSİYONLAR ---
def verileri_yukle():
    data = []
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: pass
    return sorted(data if data else DORTYOL_ESNAFLARI, key=lambda x: x.get('puan', 0), reverse=True)

# --- PREMIUM UI DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    /* Arka Plan */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }

    /* Başlık Alanı */
    .hero-title {
        font-family: 'Cinzel', serif;
        color: #ffcc00;
        font-size: 3.5rem;
        letter-spacing: 15px;
        text-align: center;
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.4);
        margin-top: -100px;
    }

    /* Kategori Izgarası (3'lü) */
    .cat-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 204, 0, 0.2);
        transition: 0.4s;
        cursor: pointer;
        margin-bottom: 10px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .cat-box:hover {
        background: rgba(255, 204, 0, 0.1);
        border: 1px solid #ffcc00;
        transform: translateY(-5px);
    }

    /* Dükkan Kartları */
    .shop-card-pro {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 25px;
        border-left: 6px solid #ffcc00;
        padding: 25px;
        margin-bottom: 20px;
        border-top: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    /* Input Alanları */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 15px !important;
    }

    /* Gereksiz kod yazılarını gizleme */
    .stMarkdown div p code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SİTE KİLİDİ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="hero-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-style:italic; color:#ffcc00; margin-bottom:30px;">Elite Esnaf Portalı - Hoş geldiniz</p>', unsafe_allow_html=True)
    
    _, col_log, _ = st.columns([2, 1, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.4); padding:30px; border-radius:30px; border:1px solid #ffcc0033;">', unsafe_allow_html=True)
        key_try = st.text_input("Giriş Anahtarı", type="password", placeholder="••••••")
        if st.button("SİSTEME GİRİŞ YAP"):
            if key_try == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı kod!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- ANA PORTAL ---
st.markdown('<h1 class="hero-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# ARAMA
_, s_col, _ = st.columns([1, 4, 1])
with s_col:
    q = st.text_input("", placeholder="🔍 Aradığınız her şey burada... (Dükkan, Kebap, Altın vb.)", key="search_top")

# SEKMELER
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [
    {"ad": "Tümü", "ikon": "🌐"},
    {"ad": "Tatlıcı", "ikon": "🍯"},
    {"ad": "Kebapçı", "ikon": "🔥"},
    {"ad": "Sağlık", "ikon": "🏥"},
    {"ad": "Ulaşım", "ikon": "🚗"},
    {"ad": "Hizmet", "ikon": "🛠️"},
    {"ad": "Yatırım", "ikon": "💎"},
    {"ad": "Giyim", "ikon": "👕"}
]

# --- 1. KEŞFET ---
with tabs[0]:
    st.markdown("### 🏷️ Sektör Seçin")
    for i in range(0, len(kategoriler), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(kategoriler):
                cat = kategoriler[i + j]
                with cols[j]:
                    border_c = "#ffcc00" if st.session_state.selected_cat == cat['ad'] else "rgba(255,204,0,0.2)"
                    st.markdown(f"""
                        <div class="cat-box" style="border-color: {border_c};">
                            <span style="font-size:2.5rem;">{cat['ikon']}</span>
                            <span style="font-size:0.8rem; font-weight:800; color:#ffcc00; letter-spacing:1px;">{cat['ad'].upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Gör: {cat['ad']}", key=f"cat_{cat['ad']}"):
                        st.session_state.selected_cat = cat['ad']
                        st.session_state.selected_id = None
                        st.rerun()

    st.divider()

    if st.session_state.selected_id is None:
        shops = verileri_yukle()
        filtered = [s for s in shops if (q.lower() in s['ad'].lower() or q.lower() in s['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or s['sektor'] == st.session_state.selected_cat)]
        
        for s in filtered:
            st.markdown(f"""
            <div class="shop-card-pro">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; gap:10px;">
                        {f'<span style="background:#ffcc00; color:black; padding:2px 10px; border-radius:50px; font-size:0.7rem; font-weight:900;">🏆 ELİTE</span>' if s.get('yildizli') else ''}
                        <span style="border:1px solid #444; color:#aaa; padding:2px 10px; border-radius:50px; font-size:0.7rem;">{s['sektor']}</span>
                    </div>
                    <span style="color:#ffcc00; font-weight:800;">⭐ {s.get('puan', 0)}</span>
                </div>
                <h2 style="margin:10px 0; color:white; font-family:Cinzel, serif;">{s['ad']}</h2>
                <p style="color:#ddd; margin-bottom:5px;"><b>İmza Ürün:</b> {s['urun']}</p>
                <p style="color:#666; font-size:0.8rem;">📍 Dörtyol / Hatay | 👁️ {s.get('tıklanma', 0)} Ziyaret</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"DETAYLARI İNCELE: {s['ad']}", key=f"sh_{s['ad']}"):
                st.session_state.selected_id = s
                if db and col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        d = st.session_state.selected_id
        if st.button("⬅️ LİSTEYE GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:60px; border-radius:40px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif; font-size:4rem; margin:0;">{d['ad']}</h1>
            <p style="font-size:1.8rem; font-weight:700; color:#ddd;">{d['urun']}</p>
            <hr style="border-color:#333; width:40%; margin:40px auto;">
            <p style="font-size:1.4rem; line-height:1.8; color:#ccc; font-style:italic;">"{d['icerik']}"</p>
            <br>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:400px; background:#25D366; color:white; border:none; padding:20px; border-radius:20px; font-weight:bold; font-size:1.5rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_v18"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("Resmi WhatsApp*")
        with c2:
            n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_urn = st.text_input("Ana Ürün/Hizmet")
        n_tanitim = st.text_area("İşletme Hikayesi")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "yildizli": False}
                col_ref.add(data)
                st.success("Tebrikler! Dörtyol Çarşı ailesine katıldınız."); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF PORTAL GİRİŞİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("PANELE GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
            else: st.error("Giriş bilgileri hatalı.")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Yönetim Paneli")
        st.write(f"Toplam Ziyaret: {d.get('tıklanma', 0)}")
        if st.button("ÇIKIŞ YAP"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Admin Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Aktif.")
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(f"⚙️ {i['ad']}"):
                    if st.button(f"SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Premium Architecture | v18.0 Commercial Elite</div>", unsafe_allow_html=True)
