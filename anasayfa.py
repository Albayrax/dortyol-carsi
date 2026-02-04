import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import random

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı 2026",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AYARLAR ---
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
        st.error(f"Sistem Bağlantı Hatası: {e}")

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state:
    st.session_state.is_site_unlocked = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'selected_cat' not in st.session_state:
    st.session_state.selected_cat = "Tümü"
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            return [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except:
            return []
    return []

# --- TASARIM & E-TICARET UI (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background: linear-gradient(180deg, #0a0a0a 0%, #1c0000 100%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Üst Başlık ve Navigasyon */
    .header-box {{
        text-align: center;
        margin-top: -95px;
        padding-bottom: 5px;
    }}
    .header-box h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        color: #ffcc00;
        margin: 0;
        letter-spacing: 8px;
        text-shadow: 0 0 20px rgba(255, 204, 0, 0.4);
    }}

    /* Tabs (Sekmeler) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        border-bottom: 2px solid rgba(255, 204, 0, 0.3);
        margin-bottom: 20px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 800;
        color: #888;
        padding: 10px 30px;
    }}
    .stTabs [aria-selected="true"] {{
        color: #ffcc00 !important;
    }}

    /* Instagram/Trendyol Stili Kategori Barı */
    .story-container {{
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 10px 0;
        scrollbar-width: none;
    }}
    .story-item {{
        flex: 0 0 auto;
        text-align: center;
        width: 110px;
        cursor: pointer;
    }}
    .story-img {{
        width: 100px;
        height: 100px;
        border-radius: 20px;
        object-fit: cover;
        border: 3px solid rgba(255, 204, 0, 0.2);
        transition: 0.3s;
    }}
    .story-img:hover {{
        border: 3px solid #ffcc00;
        transform: scale(1.05);
    }}
    .story-text {{
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 8px;
        color: #ddd;
    }}

    /* Günün Fırsatı Banner */
    .highlight-banner {{
        background: linear-gradient(90deg, #b30000 0%, #ffcc00 100%);
        padding: 20px;
        border-radius: 25px;
        margin: 20px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: black;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}

    /* Premium Kartlar */
    .dukkan-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 15px;
        border: 1px solid rgba(255, 204, 0, 0.1);
        transition: 0.4s;
    }}
    .dukkan-card:hover {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid #ffcc00;
        transform: translateY(-5px);
    }}

    /* Butonlar */
    .stButton>button {{
        border-radius: 12px !important;
        font-weight: 800 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SİTE KİLİDİ ---
if not st.session_state.is_site_unlocked:
    _, lock_col, _ = st.columns([1, 1.5, 1])
    with lock_col:
        st.markdown("<br><br><br><br><h2 style='text-align:center; color:#ffcc00;'>🔒 PRESTİJ ERİŞİMİ</h2>", unsafe_allow_html=True)
        st.write("<p style='text-align:center;'>Geleceğin Dörtyol'u inşa ediliyor. Giriş anahtarını kullanın.</p>", unsafe_allow_html=True)
        key_input = st.text_input("Giriş Anahtarı", type="password")
        if st.button("SİSTEME GİR"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else:
                st.error("Hatalı anahtar.")
    st.stop()

# --- ANA İÇERİK ---

st.markdown('<div class="header-box"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)

# SEKME YERLEŞİMİ (NAVİGASYON)
tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔑 YÖNETİM"])

# KATEGORİ LİSTESİ (PREMIUM KARE GÖRSELLER)
kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?q=80&w=300"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1519676867240-f03562e64548?q=80&w=300"},
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544148103-0773bf10d330?q=80&w=300"},
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=300"},
    {"ad": "Giyim", "img": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=300"},
    {"ad": "Teknoloji", "img": "https://images.unsplash.com/photo-1550009158-9ebf69173e03?q=80&w=300"},
    {"ad": "Kasap", "img": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?q=80&w=300"},
    {"ad": "Manav", "img": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?q=80&w=300"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?q=80&w=300"},
    {"ad": "Çiçekçi", "img": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=300"},
    {"ad": "Mobilya", "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=300"},
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=300"},
    {"ad": "Züccaciye", "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?q=80&w=300"},
    {"ad": "Emlak", "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=300"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=300"},
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=300"}
]

# --- 1. SEKME: KEŞFET ---
with tabs[0]:
    # GÜNÜN ÖNE ÇIKANLARI (STORY/BANNER MANTIĞI)
    st.markdown("""
        <div class="highlight-banner">
            <div>
                <h3 style="margin:0;">🍊 GÜNÜN ESNAFI: FISTIKZADE GURME</h3>
                <p style="margin:0; font-size:0.9rem;">Bugün tüm siparişlerde Dörtyol Portakal Suyu ikram!</p>
            </div>
            <div style="font-weight:900; font-size:1.5rem;">⚡ FIRSAT</div>
        </div>
    """, unsafe_allow_html=True)

    # KATEGORİ HİKAYELERİ (KARE VE BÜYÜK)
    st.write("### 🏷️ Kategoriler")
    story_cols = st.columns(len(kategoriler))
    for i, c in enumerate(kategoriler):
        with story_cols[i]:
            st.markdown(f"""
                <div style="text-align:center;">
                    <img src="{c['img']}" style="width:100px; height:100px; border-radius:20px; border:3px solid {'#ffcc00' if st.session_state.selected_cat == c['ad'] else '#333'};">
                    <p style="font-size:0.7rem; font-weight:800; margin-top:5px; color:{'#ffcc00' if st.session_state.selected_cat == c['ad'] else '#bbb'};">{c['ad'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("SEC", key=f"cat_{c['ad']}", help=f"{c['ad']} Seç"):
                st.session_state.selected_cat = c['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME
    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        search = st.text_input("🔍 Aradığınız lezzet veya dükkan...", placeholder="Örn: Kebap, Kuyumcu, Eczane...")
        
        filtered = [d for d in dukkanlar if (search.lower() in d['ad'].lower() or search.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        if not filtered:
            st.info(f"{st.session_state.selected_cat} kategorisinde henüz bir kayıt bulunmuyor.")
        
        # Grid Görünümü (Trendyol Kartları gibi)
        grid = st.columns(3)
        for idx, d in enumerate(filtered):
            with grid[idx % 3]:
                st.markdown(f"""
                <div class="dukkan-card">
                    <small style="color:#ffcc00; font-weight:800;">{d['sektor'].upper()}</small>
                    <h4 style="margin:5px 0;">{d['ad']}</h4>
                    <p style="font-size:0.8rem; color:#aaa; min-height:40px;">{d['urun']}</p>
                    <p style="font-size:0.7rem; color:#666;">📍 Dörtyol Merkez</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"DETAYLAR: {d['ad']}", key=f"v_{d['id']}"):
                    st.session_state.selected_id = d
                    if db and col_ref:
                        col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI LİSTESİNE DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.6); padding:40px; border-radius:40px; border:1px solid #ffcc00;">
            <h1 style="color:#ffcc00; text-align:center;">{d['ad']}</h1>
            <p style="text-align:center; letter-spacing:3px;">2026 KURUMSAL ESNAF AĞI</p>
            <hr style="border-color:#444;">
            <div style="display:flex; justify-content:space-around; text-align:center; padding:20px 0;">
                <div><h5 style="color:#ffcc00;">İMZA ÜRÜN</h5><p>{d['urun']}</p></div>
                <div><h5 style="color:#ffcc00;">KATEGORİ</h5><p>{d['sektor']}</p></div>
            </div>
            <p style="padding:20px; font-style:italic; text-align:center; border-radius:20px; background:rgba(255,255,255,0.03);">"{d['icerik']}"</p>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; background:#25D366; color:white; border:none; padding:18px; border-radius:15px; font-weight:bold; cursor:pointer; font-size:1.1rem;">
                    🟢 WHATSAPP İLE SİPARİŞ / BİLGİ AL
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. SEKME: KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏢 KURUMSAL ESNAF BAŞVURUSU</h3>", unsafe_allow_html=True)
    with st.form("premium_register_v4"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("Resmi WhatsApp No (05xx...)")
        with c2:
            n_sek = st.selectbox("Sektör / Faaliyet Alanı", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("İmza Ürününüz / Hizmetiniz")
        
        n_tanitim = st.text_area("İşletme Hikayesi ve Müşterilere Mesajınız")
        
        st.markdown("""
            <div style="background:rgba(255,204,0,0.05); padding:15px; border-radius:15px; border:1px dashed #ffcc00; font-size:0.8rem; color:#ddd;">
                <b>ESNAF TAAHHÜTNAMESİ:</b> Dörtyol Dijital Çarşı platformuna kayıt olan işletmemiz; sunduğu ürün ve hizmetlerde kaliteyi koruyacağını, müşteri memnuniyetini esas alacağını ve platform kurallarına uyacağını dijital olarak taahhüt eder.
            </div>
        """, unsafe_allow_html=True)
        onay = st.checkbox("Kurumsal taahhütnameyi okudum ve dijital imzamla onaylıyorum.")
        
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA VE YAYINLA"):
            if onay and n_ad and db:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0, "onaylı": True
                }
                col_ref.add(data)
                st.success("Tebrikler! İşletmeniz Dörtyol'un dijital geleceğine dahil edildi.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. SEKME: YÖNETİM ---
with tabs[2]:
    pwd = st.text_input("Admin Erişim Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.session_state.is_admin = True
        st.success("Hoş Geldin Albayrax. Sistem ve Analiz Paneli Açık.")
        
        all_data = verileri_yukle()
        
        # ANALİZ METRİKLERİ
        st.markdown("### 📈 Platform Analitiği")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Kayıtlı Esnaf", len(all_data))
        with m2:
            top_hit = max(all_data, key=lambda x: x.get('tıklanma', 0)) if all_data else {"ad": "-"}
            st.metric("En Çok İlgi Gören", top_hit['ad'], f"{top_hit.get('tıklanma', 0)} tık")
        with m3:
            st.metric("Sistem Durumu", "2026 Aktif")

        st.divider()
        
        # SİLME / DÜZENLEME
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']} (Toplam İlgi: {item.get('tıklanma', 0)})"):
                st.write(f"Kayıt Tarihi: {item.get('tarih','-')} | İletişim: {item['tel']}")
                if st.button(f"🗑️ İŞLETMEYİ KALDIR: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.warning("İşletme sistemden silindi.")
                    st.rerun()
    elif pwd:
        st.error("Erişim Reddedildi!")

# FOOTER
st.markdown(f"""
    <div style="text-align:center; padding-top:100px; opacity:0.3; font-size:0.6rem; letter-spacing:2px;">
        © {GUNCEL_YIL} Albayrax Premium Digital Architecture | Dörtyol Hatay<br>
        v4.0 Visionary Commerce Platform
    </div>
    <div style="height:60px;"></div>
    """, unsafe_allow_html=True)
