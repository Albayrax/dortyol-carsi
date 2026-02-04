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

# --- 2026 ULTIMATE UI & ANIMATIONS (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, #0a0a0a 0%, #250000 25%, #000000 50%, #1f0000 75%, #0a0a0a 100%);
        background-size: 400% 400%;
        animation: meshGradient 15s ease infinite;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    @keyframes meshGradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Tepe Başlık */
    .top-nav {{
        text-align: center;
        margin-top: -85px;
        padding-bottom: 5px;
    }}
    .top-nav h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2.8rem;
        color: #ffcc00;
        letter-spacing: 14px;
        text-shadow: 0 0 40px rgba(255, 204, 0, 0.5);
        margin-bottom: 10px;
    }}

    /* Arama Çubuğu Tasarımı - Geniş ve Net */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.07) !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 30px !important;
        color: white !important;
        padding: 20px 35px !important;
        font-size: 1.3rem !important;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.2);
    }}

    /* Büyük Kare Kategori Kartları - Bento Elite */
    .bento-cat-card {{
        background: rgba(0, 0, 0, 0.4);
        border-radius: 35px;
        overflow: hidden;
        border: 1px solid rgba(255, 204, 0, 0.2);
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        position: relative;
        height: 240px; /* Görselleri büyüttük */
        margin-bottom: 15px;
    }}
    .bento-cat-card:hover {{
        border: 2px solid #ffcc00;
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
    }}
    .bento-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.8;
        transition: 0.8s;
    }}
    .bento-cat-card:hover .bento-img {{
        opacity: 1;
        transform: scale(1.1);
    }}
    .bento-title {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(0deg, rgba(0,0,0,0.95) 0%, transparent 100%);
        padding: 25px;
        text-align: center;
        font-weight: 900;
        font-size: 1rem;
        color: #ffcc00;
        letter-spacing: 2px;
    }}

    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        border-bottom: 2px solid rgba(255, 204, 0, 0.1);
        margin-top: 20px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 1.1rem;
        font-weight: 700;
        padding: 15px 40px;
    }}

    /* Butonlar */
    .stButton>button {{
        border-radius: 20px !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #ffcc00 0%, #ffa500 100%) !important;
        color: #000 !important;
        height: 60px;
        font-size: 1.1rem !important;
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

# ARAMA ÇUBUĞU (TEPEDE - DÜKKAN ADININ ALTINDA)
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_query = st.text_input("", placeholder="🔍 Neye ihtiyacınız var? (Dükkan, Kebap, Altın...)", key="global_search_v7")

# SEKMELER (NAVİGASYON)
tabs = st.tabs(["🏛️ ÇARŞIYI KEŞFET", "📝 KURUMSAL KAYIT", "🔑 YÖNETİM"])

# GÖRSEL LİNKLERİ (USER İSTEKLERİNE GÖRE GÜNCELLENDİ)
kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"}, # Alışveriş/Shopping
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=800"}, # Baklava/Künefe Fıstıklı
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800"}, 
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=800"}, # Altın/Pırlanta
    {"ad": "Giyim", "img": "https://images.unsplash.com/photo-1445205170230-053b83016050?q=80&w=800"},
    {"ad": "Teknoloji", "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?q=80&w=800"}, # Sağlık/Aşı/İlaç
    {"ad": "Manav", "img": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?q=80&w=800"},
    {"ad": "Kasap", "img": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?q=80&w=800"},
    {"ad": "Çiçekçi", "img": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=800"},
    {"ad": "Mobilya", "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=800"},
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=800"}, # El Aletleri/Hardware
    {"ad": "Züccaciye", "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?q=80&w=800"},
    {"ad": "Emlak", "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=800"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800"}, # Lüks Araç/Range Rover
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # KATEGORİ IZGARASI (BENTO GRID - 4'LÜ)
    st.markdown("### 🏆 Dörtyol Elite Kategoriler")
    cat_cols = st.columns(4)
    for i, c in enumerate(kategoriler):
        with cat_cols[i % 4]:
            st.markdown(f"""
                <div class="bento-cat-card">
                    <img src="{c['img']}" class="bento-img">
                    <div class="bento-title">{c['ad'].upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Filtrele: {c['ad']}", key=f"cat_{c['ad']}"):
                st.session_state.selected_cat = c['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME
    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        
        filtered = [d for d in dukkanlar if (search_query.lower() in d['ad'].lower() or search_query.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        if not filtered:
            st.info(f"{st.session_state.selected_cat} kategorisinde henüz dükkan bulunmuyor.")
        
        # Featured List (Geniş Kartlar)
        for d in filtered:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06); border-radius:35px; border:1px solid rgba(255,204,0,0.2); overflow:hidden; margin-bottom:25px; transition:0.3s;">
                <div style="padding:35px;">
                    <span style="color:#ffcc00; font-weight:900; font-size:0.9rem; letter-spacing:1px;">{d['sektor'].upper()}</span>
                    <h2 style="margin:10px 0; color:white; font-family:'Cinzel', serif;">{d['ad']}</h2>
                    <p style="color:#ddd; font-size:1.2rem; font-weight:300;">İmza Lezzet/Hizmet: {d['urun']}</p>
                    <p style="color:#888; font-size:1rem;">📍 Dörtyol / Hatay</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📊 {d['ad']} MAĞAZASINI İNCELE", key=f"v_{d['id']}"):
                st.session_state.selected_id = d
                if db and col_ref:
                    col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI (TAM EKRAN PREMIUM)
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI MEYDANINA GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:70px; border-radius:50px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-size:4.5rem; margin:0; font-family:'Cinzel', serif;">{d['ad']}</h1>
            <p style="letter-spacing:10px; color:#666; font-weight:700;">2026 ELİTE ESNAF EKOSİSTEMİ</p>
            <hr style="border-color:#333; width:40%; margin:40px auto;">
            <div style="display:flex; justify-content:center; gap:80px; margin-bottom:50px;">
                <div><h3 style="color:#ffcc00;">İMZA ÜRÜN</h3><p style="font-size:1.8rem; font-weight:600;">{d['urun']}</p></div>
                <div><h3 style="color:#ffcc00;">KATEGORİ</h3><p style="font-size:1.8rem; font-weight:600;">{d['sektor']}</p></div>
            </div>
            <p style="font-size:1.4rem; max-width:900px; margin:0 auto; color:#ccc; line-height:1.8; font-style:italic;">"{d['icerik']}"</p>
            <br><br>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:550px; background:#25D366; color:white; border:none; padding:30px; border-radius:25px; font-weight:900; font-size:1.6rem; cursor:pointer; box-shadow: 0 10px 30px rgba(37,211,102,0.3);">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. SEKME: KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h2 style='text-align:center; color:#ffcc00; font-family:'Cinzel', serif;'>🏛️ KURUMSAL ESNAF BAŞVURUSU</h2>", unsafe_allow_html=True)
    with st.form("elite_register_v7"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Resmi Adı*")
            n_tel = st.text_input("Kurumsal WhatsApp (05xx...)")
        with c2:
            n_sek = st.selectbox("Sektör Seçin", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("Öne Çıkan Ürün/Hizmet")
        
        n_tanitim = st.text_area("İşletme Tanıtım Yazısı (Müşterilerinize Mesajınız)")
        
        st.markdown(f"""
            <div style="background:rgba(255,204,0,0.07); padding:25px; border-radius:30px; border:1px dashed #ffcc00; color:#ddd; margin-bottom:25px; line-height:1.6;">
                <b>ESNAF TAAHHÜTNAMESİ:</b> Dörtyol Dijital Çarşı platformuna kayıt olan işletmemiz; dürüst ticaret, yüksek kalite ve mutlak müşteri memnuniyetini kurumsal bir ilke olarak kabul ettiğini beyan eder. 
                Sözleşmenin tamamını okumak için <span class="contract-link">Dörtyol Çarşı Hizmet Politikası</span> sayfasına göz atabilirsiniz.
            </div>
        """, unsafe_allow_html=True)
        onay = st.checkbox("Kurumsal taahhütnameyi okudum, anladım ve dijital imzamla onaylıyorum.")
        
        if st.form_submit_button("📜 SİSTEME DİJİTAL KAYIT OL"):
            if onay and n_ad and db:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0
                }
                col_ref.add(data)
                st.success("Başvuru onaylandı! Dörtyol'un dijital geleceğine kurumsal adımınızı attınız.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. SEKME: YÖNETİM ---
with tabs[2]:
    pwd = st.text_input("Erişim Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.session_state.is_admin = True
        st.success("Elite Yönetici Paneli Aktif.")
        all_data = verileri_yukle()
        st.markdown("### 📈 Veri ve Performans Analizi")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Kayıtlı Esnaf", len(all_data))
        with m2: 
            best = max(all_data, key=lambda x: x.get('tıklanma', 0)) if all_data else {"ad": "-"}
            st.metric("En Popüler Mağaza", best['ad'], f"{best.get('tıklanma',0)} etkileşim")
        with m3: st.metric("Sistem Versiyonu", "7.0 Ultimate")

        st.divider()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']} (İlgi Skoru: {item.get('tıklanma',0)})"):
                if st.button(f"SİSTEMDEN KALICI OLARAK SİL: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.warning("Mağaza sistemden kaldırıldı.")
                    st.rerun()
    elif pwd: st.error("Erişim Reddedildi")

# FOOTER
st.markdown(f"""
    <div style="text-align:center; padding-top:150px; opacity:0.2; font-size:0.8rem; letter-spacing:5px;">
        © {GUNCEL_YIL} Albayrax Premium Architecture | v7.0 Ultimate Elite Edition<br>
        Dörtyol Dijital Ekosistem Vizyon Projesi
    </div>
    <div style="height:100px;"></div>
    """, unsafe_allow_html=True)
