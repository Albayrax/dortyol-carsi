import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import re

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
if 'owner_shop_id' not in st.session_state:
    st.session_state.owner_shop_id = None # Esnaf kendi dükkanına girdi mi?
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

def maps_dogrula(url):
    # Basit bir Google/Yandex Maps link kontrolü
    if "google.com/maps" in url or "yandex.com/maps" in url or "maps.app.goo.gl" in url:
        return True
    return False

# --- 2026 ULTIMATE UI & DASHBOARD (CSS) ---
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

    /* Tepe Navigasyon */
    .top-nav {{ text-align: center; margin-top: -85px; padding-bottom: 5px; }}
    .top-nav h1 {{
        font-family: 'Cinzel', serif; font-size: 2.8rem; color: #ffcc00;
        letter-spacing: 12px; text-shadow: 0 0 40px rgba(255, 204, 0, 0.5);
    }}

    /* Arama Çubuğu */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.07) !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 30px !important;
        color: white !important;
        padding: 15px 30px !important;
    }}

    /* Bento Kategori Kartları */
    .bento-cat-card {{
        background: rgba(0, 0, 0, 0.4); border-radius: 30px; overflow: hidden;
        border: 1px solid rgba(255, 204, 0, 0.15); transition: 0.5s;
        cursor: pointer; position: relative; height: 180px; margin-bottom: 15px;
    }}
    .bento-cat-card:hover {{ border: 2px solid #ffcc00; transform: translateY(-5px); }}
    .bento-img {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.7; }}
    .bento-title {{
        position: absolute; bottom: 0; left: 0; right: 0;
        background: linear-gradient(0deg, rgba(0,0,0,0.9) 0%, transparent 100%);
        padding: 15px; text-align: center; font-weight: 900; color: #ffcc00;
    }}

    /* Dashboard Paneli */
    .dashboard-panel {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 30px;
        border: 2px solid #ffcc00;
        margin-top: 20px;
    }}

    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; }}
    .stButton>button {{ border-radius: 15px !important; font-weight: 800 !important; }}
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

# ARAMA ÇUBUĞU
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_query = st.text_input("", placeholder="🔍 Aradığınız dükkan, ürün veya hizmet...", key="global_search_v8")

# SEKMELER (NAVİGASYON)
tabs = st.tabs(["🏛️ ÇARŞIYI KEŞFET", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=600"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=600"},
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=600"},
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=600"},
    {"ad": "Giyim", "img": "https://images.unsplash.com/photo-1445205170230-053b83016050?q=80&w=600"},
    {"ad": "Teknoloji", "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=600"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?q=80&w=600"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=600"},
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=600"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    if st.session_state.selected_id is None:
        cat_cols = st.columns(len(kategoriler))
        for i, c in enumerate(kategoriler):
            with cat_cols[i]:
                st.markdown(f"""
                    <div class="bento-cat-card">
                        <img src="{c['img']}" class="bento-img">
                        <div class="bento-title">{c['ad'].upper()}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Gör: {c['ad']}", key=f"cat_{c['ad']}"):
                    st.session_state.selected_cat = c['ad']
                    st.session_state.selected_id = None
                    st.rerun()

        st.divider()

        dukkanlar = verileri_yukle()
        filtered = [d for d in dukkanlar if (search_query.lower() in d['ad'].lower() or search_query.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        for d in filtered:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06); border-radius:25px; border:1px solid rgba(255,204,0,0.2); padding:20px; margin-bottom:15px;">
                <h3 style="margin:0; color:#ffcc00;">{d['ad']}</h3>
                <p style="margin:5px 0; color:#ddd;">{d['urun']}</p>
                <small style="color:#888;">{d['sektor']} | 📍 Dörtyol / Hatay</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔎 DETAYI GÖR: {d['ad']}", key=f"v_{d['id']}"):
                st.session_state.selected_id = d
                if db and col_ref: col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        d = st.session_state.selected_id
        if st.button("⬅️ LİSTEYE DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:40px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00;">{d['ad']}</h1>
            <p style="font-size:1.5rem;">{d['urun']}</p>
            <hr style="border-color:#333;">
            <p style="font-style:italic; font-size:1.2rem;">"{d['icerik']}"</p>
            <br>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:400px; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; font-weight:bold; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT (DÜKKAN EKLEME) ---
with tabs[1]:
    st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL ESNAF BAŞVURUSU</h2>", unsafe_allow_html=True)
    with st.form("elite_register_v8"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("WhatsApp İletişim (05xx...)")
            n_map = st.text_input("Google Maps Konum Linki (Doğrulama İçin)*")
        with c2:
            n_sek = st.selectbox("Sektör Seçin", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("Meşhur Ürün/Hizmet")
            n_pwd = st.text_input("Yönetim Şifresi (Dükkanınızı yönetmek için)", type="password", help="Dükkanınızı ileride güncellemek için bu şifreyi unutmayın.")
        
        n_tanitim = st.text_area("İşletme Hikayesi")
        onay = st.checkbox("Kurumsal Hizmet Sözleşmesini okudum ve dükkan bilgilerimin doğruluğunu taahhüt ediyorum.")
        
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if not maps_dogrula(n_map):
                st.error("Lütfen geçerli bir Google/Yandex Maps linki girin. Doğrulama başarısız.")
            elif not onay or not n_ad or not n_pwd:
                st.error("Lütfen tüm zorunlu alanları doldurun.")
            elif db and col_ref:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0, "sifre": n_pwd, "map_url": n_map, "durum": "onayli"
                }
                col_ref.add(data)
                st.success("Tebrikler! Dükkanınız kaydedildi. 'Esnaf Paneli' sekmesinden dükkanınızı yönetebilirsiniz.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. ESNAF PANELİ (DASHBOARD) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL PANELİ</h3>", unsafe_allow_html=True)
        login_ad = st.text_input("Kayıtlı Dükkan Adınız")
        login_pwd = st.text_input("Dükkan Şifreniz", type="password")
        if st.button("DÜKKANIMI YÖNET"):
            all_shops = verileri_yukle()
            match = next((s for s in all_shops if s['ad'] == login_ad and s.get('sifre') == login_pwd), None)
            if match:
                st.session_state.owner_shop_id = match
                st.success("Giriş başarılı! Panelinize hoş geldiniz.")
                st.rerun()
            else:
                st.error("Hatalı dükkan adı veya şifre!")
    else:
        # ESNAF DASHBOARD
        d = st.session_state.owner_shop_id
        st.markdown(f"<div class='dashboard-panel'>", unsafe_allow_html=True)
        st.subheader(f"📊 {d['ad']} - Dashboard")
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1: st.metric("Toplam İnceleme", d.get('tıklanma', 0))
        with col_stat2: st.metric("Durum", "Aktif / Onaylı")
        
        st.divider()
        st.markdown("### ✏️ Dükkan Bilgilerini Güncelle")
        u_urn = st.text_input("Meşhur Ürün Güncelle", value=d['urun'])
        u_icr = st.text_area("Dükkan Tanıtımı Güncelle", value=d['icerik'])
        u_tel = st.text_input("WhatsApp Güncelle", value=d['tel'])
        
        if st.button("DEĞİŞİKLİKLERİ KAYDET"):
            if db and col_ref:
                col_ref.document(d['id']).update({"urun": u_urn, "icerik": u_icr, "tel": u_tel})
                st.success("Dükkanınız başarıyla güncellendi!")
                time.sleep(1)
                st.rerun()
        
        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Sistem Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Sistem Genel Kontrolü Aktif.")
        all_data = verileri_yukle()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']}"):
                st.write(f"Şifre: {item.get('sifre')} | Map: {item.get('map_url')}")
                if st.button(f"SİL: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.2; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Architecture | v8.0 Dashboard Edition</div>", unsafe_allow_html=True)
