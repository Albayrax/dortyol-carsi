import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI (MARKETING READY) ---
st.set_page_config(
    page_title="Dörtyol Çarşı 2026 | Elite Esnaf Ağı",
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
        st.error(f"Sistem Bağlantı Hatası: {e}")

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'is_admin': False,
    'owner_shop_id': None,
    'selected_cat': "Tümü",
    'selected_id': None,
    'sort_filter': "Puan (Yüksek)"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            if st.session_state.sort_filter == "Puan (Yüksek)":
                return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
            elif st.session_state.sort_filter == "En Çok İncelenen":
                return sorted(data, key=lambda x: x.get('tıklanma', 0), reverse=True)
            return data
        except: return []
    return []

# --- ULTRA PREMIUM DESIGN SYSTEM (CSS) ---
# Kategori bazlı renk ve arka plan dinamikleri
THEMES = {
    "Tümü": {"bg": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=1920", "accent": "#ffcc00"},
    "Tatlıcı": {"bg": "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=1920", "accent": "#ffa500"},
    "Kebapçı": {"bg": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1920", "accent": "#ff4500"},
    "Kuyumcu": {"bg": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=1920", "accent": "#d4af37"},
    "Otomotiv": {"bg": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1920", "accent": "#ffffff"},
    "Hırdavat": {"bg": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=1920", "accent": "#708090"}
}
current_theme = THEMES.get(st.session_state.selected_cat, THEMES["Tümü"])

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    /* Global Saray Teması */
    .stApp {{
        background: linear-gradient(rgba(10, 0, 0, 0.92), rgba(20, 0, 0, 0.98)), url("{current_theme['bg']}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
        transition: all 1s ease;
    }}

    /* Header & Logo */
    .hero-section {{
        text-align: center;
        margin-top: -110px;
        padding: 50px 0;
        border-bottom: 2px solid {current_theme['accent']};
        background: rgba(0,0,0,0.3);
        backdrop-filter: blur(5px);
    }}
    .hero-section h1 {{
        font-family: 'Cinzel', serif;
        font-size: 3.5rem;
        color: {current_theme['accent']};
        letter-spacing: 18px;
        text-shadow: 0 0 30px {current_theme['accent']}66;
        margin-bottom: 0;
    }}

    /* Arama Çubuğu */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid {current_theme['accent']} !important;
        border-radius: 20px !important;
        color: white !important;
        padding: 20px 30px !important;
        font-size: 1.2rem !important;
        transition: 0.3s;
    }}
    .stTextInput>div>div>input:focus {{
        box-shadow: 0 0 25px {current_theme['accent']}44 !important;
    }}

    /* Bento Grid Kartları */
    .bento-container {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
        margin-top: 30px;
    }}
    .bento-shop-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
        transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
    }}
    .bento-shop-card:hover {{
        border: 1px solid {current_theme['accent']};
        transform: translateY(-12px);
        background: rgba(255, 255, 255, 0.08);
    }}
    .shop-img-header {{
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-bottom: 2px solid {current_theme['accent']};
        filter: brightness(0.8);
        transition: 0.5s;
    }}
    .bento-shop-card:hover .shop-img-header {{
        filter: brightness(1.1);
        transform: scale(1.05);
    }}

    /* Puan ve Badge'ler */
    .score-badge {{
        background: {current_theme['accent']};
        color: #000;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 0.85rem;
    }}
    .sale-tag {{
        background: #00ff00;
        color: #000;
        padding: 4px 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.75rem;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 1; }}
    }}

    /* Altın Varaklı Butonlar */
    .stButton>button {{
        background: linear-gradient(135deg, {current_theme['accent']} 0%, #b38b00 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.4s;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK ---
if not st.session_state.is_site_unlocked:
    _, lock_col, _ = st.columns([1, 1.5, 1])
    with lock_col:
        st.markdown("<br><br><br><br><h2 style='text-align:center; color:#ffcc00;'>🏛️ ELİTE GİRİŞ</h2>", unsafe_allow_html=True)
        key_input = st.text_input("Giriş Anahtarı", type="password")
        if st.button("SARAYIN KAPILARINI AÇ"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Erişim Engellendi.")
    st.stop()

# --- MAIN UI ---
st.markdown('<div class="hero-section"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)

# ARAMA (TEPEDE)
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_q = st.text_input("", placeholder="🔍 Aradığınız her neyse, burada mutlaka vardır...", key="marketing_search")

# SEKMELER
tabs = st.tabs(["💎 KEŞFET", "📜 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 YÖNETİM"])

# KATEGORİ LİSTESİ
kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=800"},
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544148103-0773bf10d330?q=80&w=800"},
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=800"},
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?q=80&w=800"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800"},
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=800"},
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # BENTO GRID KATEGORİLER
    st.markdown(f"### 🏷️ Kategoriye Göre Gezin ({st.session_state.selected_cat})")
    cat_cols = st.columns(len(kategoriler))
    for i, c in enumerate(kategoriler):
        with cat_cols[i]:
            border_style = f"3px solid {current_theme['accent']}" if st.session_state.selected_cat == c['ad'] else "1px solid #444"
            st.markdown(f"""
                <div style="text-align:center; cursor:pointer;">
                    <img src="{c['img']}" style="width:100%; height:120px; object-fit:cover; border-radius:20px; border:{border_style};">
                    <p style="font-size:0.7rem; font-weight:800; margin-top:8px; color:{'white' if st.session_state.selected_cat == c['ad'] else '#888'};">
                        {c['ad'].upper()}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Seç", key=f"c_{c['ad']}", help=c['ad']):
                st.session_state.selected_cat = c['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTESİ
    if st.session_state.selected_id is None:
        all_data = verileri_yukle()
        filtered = [d for d in all_data if (search_q.lower() in d['ad'].lower() or search_q.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        if not filtered:
            st.info("Henüz bu alanda bir kayıt yok. Kurumsal kayıt ile ilk dükkanı siz ekleyin!")
        
        # 3'lü Bento Grid
        for i in range(0, len(filtered), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered):
                    d = filtered[i + j]
                    with cols[j]:
                        img_url = THEMES.get(d['sektor'], THEMES["Tümü"])["bg"]
                        st.markdown(f"""
                        <div class="bento-shop-card">
                            <img src="{img_url}" class="shop-img-header">
                            <div style="padding:20px; text-align:center;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <span class="score-badge">⭐ {d.get('puan', 0)} / 10</span>
                                    {f'<span class="sale-tag">🔥 {d["indirim"]}</span>' if d.get('indirim') else ""}
                                </div>
                                <h3 style="color:{current_theme['accent']}; margin:0; font-family:'Cinzel', serif;">{d['ad']}</h3>
                                <p style="font-size:0.9rem; color:#ccc; margin:10px 0;">{d['urun']}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🏢 MAĞAZAYI AÇ: {d['ad']}", key=f"sh_{d['id']}"):
                            st.session_state.selected_id = d
                            if db and col_ref: col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                            st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI MEYDANINA GERİ DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.85); padding:60px; border-radius:50px; border:2px solid {current_theme['accent']}; text-align:center;">
            <h1 style="color:{current_theme['accent']}; font-family:'Cinzel', serif; font-size:4rem; margin:0;">{d['ad']}</h1>
            <p style="font-size:1.8rem; font-weight:700; color:#ddd;">{d['urun']}</p>
            <hr style="border-color:{current_theme['accent']}; width:40%; margin:40px auto;">
            <p style="font-size:1.4rem; font-style:italic; line-height:1.8; color:#bbb; padding:0 50px;">"{d['icerik']}"</p>
            <div style="display:flex; justify-content:center; gap:40px; margin:40px 0;">
                <div style="background:rgba(255,255,255,0.05); padding:20px 40px; border-radius:20px; border:1px solid {current_theme['accent']};">
                    <h5 style="color:{current_theme['accent']}; margin:0;">ELITE SKOR</h5>
                    <p style="font-size:2rem; margin:0;">⭐ {d.get('puan', 0)}</p>
                </div>
                <div style="background:rgba(255,255,255,0.05); padding:20px 40px; border-radius:20px; border:1px solid {current_theme['accent']};">
                    <h5 style="color:{current_theme['accent']}; margin:0;">ZİYARET</h5>
                    <p style="font-size:2rem; margin:0;">👁️ {d.get('tıklanma', 0)}</p>
                </div>
            </div>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:500px; background:#25D366; color:white; border:none; padding:25px; border-radius:20px; font-weight:bold; font-size:1.5rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown(f"<h2 style='text-align:center; color:{current_theme['accent']};'>🏛️ KURUMSAL ESNAF BAŞVURUSU</h2>", unsafe_allow_html=True)
    with st.form("elite_register_v13"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("Resmi WhatsApp (05xx...)")
            n_map = st.text_input("Harita Konum Linki*")
        with c2:
            n_sek = st.selectbox("Sektör", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("İmza Ürün / Hizmet")
            n_pwd = st.text_input("Panel Şifreniz*", type="password")
        
        n_tanitim = st.text_area("İşletme Hikayesi (Pazarlama için çok kritiktir)")
        onay = st.checkbox("Elite Hizmet Sözleşmesini ve kurumsal şartları onaylıyorum.")
        
        if st.form_submit_button("📜 SİSTEME DİJİTAL KAYIT OL"):
            if onay and n_ad and n_pwd:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0, "puan": 0, "sifre": n_pwd, "map_url": n_map, "indirim": ""
                }
                col_ref.add(data)
                st.success("Tebrikler! Dörtyol'un dijital geleceğine kurumsal adımınızı attınız.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
        login_ad = st.text_input("Dükkan Adınız")
        login_pwd = st.text_input("Şifreniz", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_shops = verileri_yukle()
            match = next((s for s in all_shops if s['ad'] == login_ad and s.get('sifre') == login_pwd), None)
            if match:
                st.session_state.owner_shop_id = match
                st.rerun()
            else: st.error("Hatalı Giriş!")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} - Yönetim Paneli")
        st.write(f"Elite Skoru: ⭐ {d.get('puan', 0)} | Popülerlik: 👁️ {d.get('tıklanma', 0)}")
        st.divider()
        u_ind = st.text_input("🔥 Flaş İndirim (Örn: Bugün %20 indirim!)", value=d.get('indirim', ''))
        u_urn = st.text_input("Meşhur Ürün", value=d['urun'])
        u_icr = st.text_area("Tanıtım", value=d['icerik'])
        if st.button("GÜNCELLEMELERİ KAYDET"):
            if db and col_ref:
                col_ref.document(d['id']).update({"indirim": u_ind, "urun": u_urn, "icerik": u_icr})
                st.success("Bilgiler güncellendi!")
                time.sleep(1)
                st.rerun()
        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Sistem Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Paneli Aktif.")
        all_data = verileri_yukle()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']}"):
                p_val = st.slider("Puan Ver (0-10)", 0, 10, int(item.get('puan', 0)), key=f"p_{item['id']}")
                if st.button(f"Onayla: {item['ad']}", key=f"ps_{item['id']}"):
                    col_ref.document(item['id']).update({"puan": p_val})
                    st.rerun()
                if st.button(f"SİL: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.2; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Premium Architecture | v13.0 Marketing Edition</div>", unsafe_allow_html=True)
