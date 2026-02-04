import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı 2026 Elite",
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
        except: return []
    return []

# --- 2026 ELITE UI & ANIMATIONS (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    /* Ana Arka Plan: Hareketli Mesh Gradient */
    .stApp {{
        background: linear-gradient(135deg, #0a0a0a 0%, #200000 25%, #000000 50%, #1a0000 75%, #0a0a0a 100%);
        background-size: 400% 400%;
        animation: meshGradient 20s ease infinite;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    @keyframes meshGradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Header & Nav */
    .top-nav {{
        text-align: center;
        margin-top: -90px;
        padding-bottom: 10px;
    }}
    .top-nav h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        color: #ffcc00;
        letter-spacing: 10px;
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.3);
    }}

    /* Sekme Çizgisi */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        border-bottom: 1px solid rgba(255, 204, 0, 0.2);
    }}

    /* Büyük Kare Kategori Kartları */
    .bento-cat-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        overflow: hidden;
        border: 1px solid rgba(255, 204, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
    }}
    .bento-cat-card:hover {{
        border: 1px solid #ffcc00;
        transform: scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }}
    .bento-img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
        opacity: 0.7;
        transition: 0.5s;
    }}
    .bento-cat-card:hover .bento-img {{
        opacity: 1;
        transform: scale(1.1);
    }}
    .bento-title {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(0deg, rgba(0,0,0,0.9) 0%, transparent 100%);
        padding: 15px;
        text-align: center;
        font-weight: 800;
        font-size: 0.8rem;
        color: #ffcc00;
    }}

    /* Büyük Dükkan Kartları (Featured) */
    .featured-shop {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 30px;
        padding: 0;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 204, 0, 0.15);
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}
    .shop-img-large {{
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-bottom: 2px solid #ffcc00;
    }}
    .shop-content {{
        padding: 25px;
    }}

    /* Butonlar */
    .stButton>button {{
        border-radius: 15px !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #ffcc00 0%, #ffaa00 100%) !important;
        color: #000 !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SİTE KİLİDİ ---
if not st.session_state.is_site_unlocked:
    _, lock_col, _ = st.columns([1, 1.5, 1])
    with lock_col:
        st.markdown("<br><br><br><br><h2 style='text-align:center; color:#ffcc00;'>🔒 PRESTİJ ERİŞİMİ</h2>", unsafe_allow_html=True)
        key_input = st.text_input("Giriş Anahtarı", type="password")
        if st.button("SİSTEMİ AÇ"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Anahtar")
    st.stop()

# --- ANA İÇERİK ---

st.markdown('<div class="top-nav"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞIYI KEŞFET", "📝 KURUMSAL KAYIT", "🔑 YÖNETİM"])

kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?q=80&w=400"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1590483734724-388175d74b6e?q=80&w=400"},
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=400"},
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1573408302185-9127fe5801f3?q=80&w=400"},
    {"ad": "Giyim", "img": "https://images.unsplash.com/photo-1445205170230-053b83016050?q=80&w=400"},
    {"ad": "Teknoloji", "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=400"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1587854692152-cbe660dbbb88?q=80&w=400"},
    {"ad": "Manav", "img": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?q=80&w=400"},
    {"ad": "Kasap", "img": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?q=80&w=400"},
    {"ad": "Çiçekçi", "img": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=400"},
    {"ad": "Mobilya", "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=400"},
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=400"},
    {"ad": "Züccaciye", "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?q=80&w=400"},
    {"ad": "Emlak", "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=400"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=400"},
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=400"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # KATEGORİ IZGARASI (BENTO GRID - 4'LÜ)
    st.markdown("### 🏷️ Kategorilere Göz Atın")
    cat_cols = st.columns(4)
    for i, c in enumerate(kategoriler):
        with cat_cols[i % 4]:
            st.markdown(f"""
                <div class="bento-cat-card">
                    <img src="{c['img']}" class="bento-img">
                    <div class="bento-title">{c['ad'].upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Süz: {c['ad']}", key=f"cat_{c['ad']}"):
                st.session_state.selected_cat = c['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME (BÜYÜK GÖRSELLERLE)
    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        
        c_search, c_sort = st.columns([3, 1])
        with c_search:
            search = st.text_input("🔍 Neye ihtiyacınız var?", placeholder="Dükkan adı veya ürün yazın...")
        with c_sort:
            st.write(f"Süzülen: **{st.session_state.selected_cat}**")

        filtered = [d for d in dukkanlar if (search.lower() in d['ad'].lower() or search.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        if not filtered:
            st.info(f"{st.session_state.selected_cat} kategorisinde henüz dükkan yok.")
        
        # Featured List (Büyük Kartlar)
        for d in filtered:
            st.markdown(f"""
            <div class="featured-shop">
                <img src="{'https://images.unsplash.com/photo-1519676867240-f03562e64548?q=80&w=1200' if d['sektor'] == 'Tatlıcı' else 'https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200'}" class="shop-img-large">
                <div class="shop-content">
                    <span style="color:#ffcc00; font-weight:800; font-size:0.8rem;">{d['sektor'].upper()}</span>
                    <h2 style="margin:10px 0; color:white;">{d['ad']}</h2>
                    <p style="color:#bbb; font-size:1.1rem; line-height:1.6;">{d['urun']}</p>
                    <p style="color:#666; font-size:0.9rem;">📍 Dörtyol / Hatay</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"MAĞAZAYI ZİYARET ET: {d['ad']}", key=f"v_{d['id']}"):
                st.session_state.selected_id = d
                if db and col_ref:
                    col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI (TAM EKRAN PREMIUM)
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI MEYDANINA DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.7); padding:60px; border-radius:40px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-size:4rem; margin:0;">{d['ad']}</h1>
            <p style="letter-spacing:5px; color:#888;">2026 ELİTE ESNAF AĞI</p>
            <hr style="border-color:#333; width:50%; margin:40px auto;">
            <div style="display:flex; justify-content:center; gap:50px; margin-bottom:40px;">
                <div><h3 style="color:#ffcc00;">İMZA ÜRÜN</h3><p style="font-size:1.5rem;">{d['urun']}</p></div>
                <div><h3 style="color:#ffcc00;">KATEGORİ</h3><p style="font-size:1.5rem;">{d['sektor']}</p></div>
            </div>
            <p style="font-size:1.3rem; line-height:1.8; max-width:800px; margin:0 auto; color:#ccc;">"{d['icerik']}"</p>
            <br><br>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:500px; background:#25D366; color:white; border:none; padding:25px; border-radius:20px; font-weight:bold; font-size:1.4rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. SEKME: KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🏢 KURUMSAL ESNAF BAŞVURUSU</h2>", unsafe_allow_html=True)
    with st.form("elite_register_v5"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Resmi Adı*")
            n_tel = st.text_input("Kurumsal WhatsApp (05xx...)")
        with c2:
            n_sek = st.selectbox("Sektör Seçin", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("Öne Çıkan Ürün/Hizmet")
        
        n_tanitim = st.text_area("İşletme Tanıtım Yazısı")
        
        st.markdown("""
            <div style="background:rgba(255,204,0,0.05); padding:20px; border-radius:20px; border:1px dashed #ffcc00; color:#ddd; margin-bottom:20px;">
                <b>ESNAF TAAHHÜTNAMESİ:</b> Dörtyol Dijital Çarşı platformuna kayıt olan işletmemiz; dürüst ticaret, yüksek kalite ve müşteri memnuniyetini kurumsal bir ilke olarak kabul ettiğini beyan eder.
            </div>
        """, unsafe_allow_html=True)
        onay = st.checkbox("Kurumsal taahhütnameyi okudum ve onaylıyorum.")
        
        if st.form_submit_button("📜 SİSTEME DAHİL OL"):
            if onay and n_ad and db:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0
                }
                col_ref.add(data)
                st.success("Başvuru onaylandı! Dörtyol'un dijital geleceğine hoş geldiniz.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. SEKME: YÖNETİM ---
with tabs[2]:
    pwd = st.text_input("Erişim Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.session_state.is_admin = True
        st.success("Admin Paneli Aktif.")
        
        all_data = verileri_yukle()
        st.markdown("### 📈 Veri ve İlgi Analizi")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Kayıtlı Esnaf", len(all_data))
        with m2: 
            best = max(all_data, key=lambda x: x.get('tıklanma', 0)) if all_data else {"ad": "-"}
            st.metric("En Popüler Mağaza", best['ad'], f"{best.get('tıklanma',0)} tık")
        with m3: st.metric("Platform Versiyonu", "5.0 Elite")

        st.divider()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']} (İlgi: {item.get('tıklanma',0)})"):
                if st.button(f"SİSTEMDEN KALDIR: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.warning("Silindi.")
                    st.rerun()
    elif pwd: st.error("Erişim Reddedildi")

# FOOTER
st.markdown(f"""
    <div style="text-align:center; padding-top:120px; opacity:0.3; font-size:0.7rem; letter-spacing:3px;">
        © {GUNCEL_YIL} Albayrax Premium Architecture | v5.0 Elite Edition<br>
        Dörtyol Dijital Ekosistem Projesi
    </div>
    <div style="height:80px;"></div>
    """, unsafe_allow_html=True)
