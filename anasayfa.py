import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

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

# --- TASARIM & PREMIUM UI (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, #0d0d0d 0%, #2b0000 100%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Üst Başlık - Daha Kompakt */
    .header-box {{
        text-align: center;
        margin-top: -85px;
        padding-bottom: 10px;
    }}
    .header-box h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        color: #ffcc00;
        margin: 0;
        letter-spacing: 6px;
    }}

    /* Trendyol Stili Kategori Barı */
    .cat-container {{
        display: flex;
        overflow-x: auto;
        gap: 20px;
        padding: 20px 0;
        scrollbar-width: none;
        justify-content: center;
    }}
    .cat-item {{
        flex: 0 0 auto;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
        width: 80px;
    }}
    .cat-img {{
        width: 65px;
        height: 65px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ffcc00;
        margin-bottom: 8px;
        box-shadow: 0 4px 15px rgba(255, 204, 0, 0.2);
    }}
    .cat-text {{
        font-size: 0.7rem;
        font-weight: 700;
        color: #eee;
    }}

    /* Premium Kartlar */
    .dukkan-card {{
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 204, 0, 0.1);
        text-align: center;
        transition: 0.4s ease;
    }}
    .dukkan-card:hover {{
        border: 1px solid #ffcc00;
        background: rgba(255, 204, 0, 0.07);
        transform: translateY(-8px);
    }}

    /* İstatistik Paneli */
    .stat-box {{
        background: rgba(0,0,0,0.4);
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #ffcc00;
        margin-bottom: 10px;
    }}

    /* Butonlar */
    .stButton>button {{
        border-radius: 15px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
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

st.markdown('<div class="header-box"><h1>DÖRTYOL ÇARŞI</h1><p style="font-size:0.7rem; color:#888;">2026 PRESTİJ VİZYONU</p></div>', unsafe_allow_html=True)

# KATEGORİ LİSTESİ (TRENDYOL STİLİ)
kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?q=80&w=150"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1590483734724-388175d74b6e?q=80&w=150"},
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=150"},
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1573408302185-9127fe5801f3?q=80&w=150"},
    {"ad": "Giyim", "img": "https://images.unsplash.com/photo-1445205170230-053b83016050?q=80&w=150"},
    {"ad": "Teknoloji", "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=150"},
    {"ad": "Kasap", "img": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?q=80&w=150"},
    {"ad": "Manav", "img": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?q=80&w=150"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1587854692152-cbe660dbbb88?q=80&w=150"},
    {"ad": "Çiçekçi", "img": "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=150"},
    {"ad": "Mobilya", "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=150"},
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1581244276891-9964c15d0111?q=80&w=150"},
    {"ad": "Züccaciye", "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?q=80&w=150"},
    {"ad": "Emlak", "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=150"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=150"},
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=150"}
]

# KATEGORİ BARINI ÇİZDİRME
cols_cat = st.columns(len(kategoriler))
for i, c in enumerate(kategoriler):
    with cols_cat[i]:
        st.markdown(f"""
            <div style="text-align:center;">
                <img src="{c['img']}" style="width:50px; height:50px; border-radius:50%; border:2px solid {'#ffcc00' if st.session_state.selected_cat == c['ad'] else '#444'}; cursor:pointer;">
                <p style="font-size:0.6rem; margin-top:5px; color:{'#ffcc00' if st.session_state.selected_cat == c['ad'] else '#aaa'};">{c['ad']}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(" ", key=f"cat_{c['ad']}", help=c['ad']):
            st.session_state.selected_cat = c['ad']
            st.rerun()

st.divider()

# ANA PANEL
_, center_col, _ = st.columns([1, 10, 1])

with center_col:
    tabs = st.tabs(["🏛️ ÇARŞIYI GEZ", "📝 KURUMSAL KAYIT", "🔑 YÖNETİM"])

    # 1. SEKME: KEŞFET
    with tabs[0]:
        if st.session_state.selected_id is None:
            dukkanlar = verileri_yukle()
            
            # Arama
            search = st.text_input("🔍 Aradığınız esnaf, lezzet veya hizmet...", placeholder="Örn: Meşhur Kadayıfçı")
            
            # Filtreleme
            filtered = [d for d in dukkanlar if (search.lower() in d['ad'].lower() or search.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
            
            if not filtered:
                st.info(f"{st.session_state.selected_cat} kategorisinde henüz bir dükkan yok.")
            
            # Kart Grid Görünümü
            grid = st.columns(3)
            for idx, d in enumerate(filtered):
                with grid[idx % 3]:
                    st.markdown(f"""
                    <div class="dukkan-card">
                        <small style="color:#ffcc00; font-weight:800;">{d['sektor'].upper()}</small>
                        <h4 style="margin:5px 0;">{d['ad']}</h4>
                        <p style="font-size:0.75rem; color:#bbb;">{d['urun']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"İNCELE: {d['ad']}", key=f"v_{d['id']}"):
                        st.session_state.selected_id = d
                        # Tıklanma sayısını artırma (Analiz için)
                        if db and col_ref:
                            col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
        else:
            # DETAY SAYFASI
            d = st.session_state.selected_id
            if st.button("⬅️ LİSTEYE DÖN"):
                st.session_state.selected_id = None
                st.rerun()
            
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:30px; border:1px solid #ffcc00;">
                <h2 style="color:#ffcc00; text-align:center;">{d['ad']}</h2>
                <hr style="border-color:#333;">
                <div style="display:flex; justify-content:space-around; text-align:center;">
                    <div><h6 style="color:#ffcc00;">İMZA ÜRÜN</h6><p>{d['urun']}</p></div>
                    <div><h6 style="color:#ffcc00;">SEKTÖR</h6><p>{d['sektor']}</p></div>
                </div>
                <p style="padding:20px; font-style:italic; text-align:center;">"{d['icerik']}"</p>
                <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                    <button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; font-weight:bold; cursor:pointer;">
                        🟢 WHATSAPP İLE İLETİŞİME GEÇ
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

    # 2. SEKME: KAYIT
    with tabs[1]:
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>YENİ ESNAF BAŞVURUSU</h3>", unsafe_allow_html=True)
        with st.form("kurumsal_kayit_v3"):
            c1, c2 = st.columns(2)
            with c1:
                n_ad = st.text_input("İşletme Adı*")
                n_tel = st.text_input("Kurumsal WhatsApp (05xx...)")
            with c2:
                n_sek = st.selectbox("Sektör", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
                n_urn = st.text_input("İmza Ürününüz / Hizmetiniz")
            
            n_tanitim = st.text_area("İşletme Hikayesi ve Müşteri Mesajı")
            
            st.markdown("""
                <div style="font-size:0.75rem; color:#999; border:1px solid #444; padding:10px; border-radius:10px; margin-bottom:10px;">
                    <b>KURUMSAL TAAHHÜT:</b> Bu dükkan, Dörtyol Dijital Çarşı standartlarına uymayı, müşteri memnuniyetini en üstte tutmayı ve yanıltıcı bilgi vermemeyi kabul eder.
                </div>
            """, unsafe_allow_html=True)
            onay = st.checkbox("Sözleşme şartlarını kurumsal olarak onaylıyorum.")
            
            if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
                if onay and n_ad and db:
                    data = {
                        "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                        "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                        "tıklanma": 0, "satış": 0 # Gelecekteki raporlama için
                    }
                    col_ref.add(data)
                    st.success("Başvuru onaylandı! Çarşıya hoş geldiniz.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # 3. SEKME: YÖNETİM & ANALİZ
    with tabs[2]:
        pwd = st.text_input("Admin Anahtarı", type="password")
        if pwd == ADMIN_SIFRE:
            st.session_state.is_admin = True
            st.success("Yönetici Yetkisi Onaylandı.")
            
            # ANALİZ BÖLÜMÜ
            st.markdown("### 📊 Satış ve İlgi Analizi")
            all_data = verileri_yukle()
            
            c_stat1, c_stat2, c_stat3 = st.columns(3)
            with c_stat1:
                st.metric("Toplam Esnaf", len(all_data))
            with c_stat2:
                top_hit = max(all_data, key=lambda x: x.get('tıklanma', 0)) if all_data else {"ad": "-"}
                st.metric("En Çok İncelenen", top_hit['ad'])
            with c_stat3:
                st.metric("Platform Durumu", "Aktif / 2026")

            st.divider()
            
            # SİLME VE YÖNETİM
            for item in all_data:
                with st.expander(f"⚙️ {item['ad']} (İlgi: {item.get('tıklanma', 0)} tıklama)"):
                    st.write(f"Sektör: {item['sektor']} | Kayıt: {item.get('tarih', '-')}")
                    if st.button(f"🗑️ KALDIR: {item['ad']}", key=f"del_{item['id']}"):
                        col_ref.document(item['id']).delete()
                        st.warning("Dükkan silindi.")
                        st.rerun()
        elif pwd:
            st.error("Hatalı anahtar!")

# FOOTER
st.markdown(f"""
    <div style="text-align:center; padding-top:100px; opacity:0.3; font-size:0.65rem;">
        © {GUNCEL_YIL} Albayrax Premium Architecture | v3.0 Ultra-Premium<br>
        Dörtyol'un İlk Dijital Alışveriş Köprüsü
    </div>
    <div style="height:60px;"></div>
    """, unsafe_allow_html=True)
