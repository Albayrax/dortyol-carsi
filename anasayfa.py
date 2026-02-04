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
if 'owner_shop_id' not in st.session_state:
    st.session_state.owner_shop_id = None
if 'selected_cat' not in st.session_state:
    st.session_state.selected_cat = "Tümü"
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            # Puanına göre sıralayarak çekiyoruz (Daha sonra JS ile de sıralanabilir)
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
        except: return []
    return []

# --- ROYAL UI & BENTO GRID (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background: linear-gradient(180deg, #0f0000 0%, #300000 100%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Header Tasarımı */
    .header-section {{
        text-align: center;
        margin-top: -95px;
        padding: 30px 0;
        border-bottom: 2px solid #ffcc00;
        margin-bottom: 10px;
    }}
    .header-section h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2.8rem;
        color: #ffcc00;
        letter-spacing: 12px;
        text-shadow: 2px 2px 15px rgba(255, 204, 0, 0.4);
    }}

    /* Arama Çubuğu */
    .stTextInput>div>div>input {{
        background: rgba(0, 0, 0, 0.6) !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 15px 25px !important;
    }}

    /* Bento Grid Kategori Kutuları */
    .bento-box {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 25px;
        overflow: hidden;
        border: 1px solid rgba(255, 204, 0, 0.2);
        transition: 0.4s;
        height: 200px;
        position: relative;
    }}
    .bento-box:hover {{
        transform: translateY(-8px);
        border: 2px solid #ffcc00;
        box-shadow: 0 10px 30px rgba(255, 204, 0, 0.3);
    }}
    .bento-box img {{
        width: 100%; height: 100%; object-fit: cover; opacity: 0.7;
    }}
    .bento-label {{
        position: absolute; bottom: 0; left: 0; right: 0;
        background: rgba(0,0,0,0.8); padding: 10px;
        text-align: center; font-weight: 800; color: #ffcc00;
        font-size: 0.8rem;
    }}

    /* İndirim Bannerı */
    .discount-banner {{
        background: linear-gradient(90deg, #ffcc00, #ffaa00);
        color: black;
        padding: 15px;
        border-radius: 15px;
        margin: 20px 0;
        font-weight: 800;
        text-align: center;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}

    /* Mağaza Kartları */
    .shop-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 204, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.3s;
    }}
    .shop-card:hover {{
        border: 1px solid #ffcc00;
        background: rgba(255, 255, 255, 0.06);
    }}

    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; gap: 30px; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 700; color: #888; }}
    .stTabs [aria-selected="true"] {{ color: #ffcc00 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- SİTE KİLİDİ ---
if not st.session_state.is_site_unlocked:
    _, lock_col, _ = st.columns([1, 1.5, 1])
    with lock_col:
        st.markdown("<br><br><br><br><h2 style='text-align:center; color:#ffcc00;'>🔒 SARAY ERİŞİMİ</h2>", unsafe_allow_html=True)
        key_input = st.text_input("Giriş Anahtarı", type="password")
        if st.button("SİSTEME GİRİŞ YAP"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Giriş Anahtarı")
    st.stop()

# --- ANA İÇERİK ---
st.markdown('<div class="header-section"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)

# ARAMA ÇUBUĞU
_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    search_query = st.text_input("", placeholder="🔍 Neye ihtiyacınız var? (Dükkan, Kebap, Altın...)", key="v10_search")

# NAVİGASYON
tabs = st.tabs(["🏛️ ÇARŞIYI KEŞFET", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# KATEGORİ LİSTESİ (BÜYÜK GÖRSELLER)
kategoriler = [
    {"ad": "Tümü", "img": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"},
    {"ad": "Tatlıcı", "img": "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=800"}, # Baklava
    {"ad": "Kebapçı", "img": "https://images.unsplash.com/photo-1544148103-0773bf10d330?q=80&w=800"}, 
    {"ad": "Kuyumcu", "img": "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=800"}, # Pırlanta
    {"ad": "Eczane", "img": "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?q=80&w=800"},
    {"ad": "Otomotiv", "img": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800"}, # Range/Porsche
    {"ad": "Hırdavat", "img": "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=800"}, # El Aletleri
    {"ad": "Diğer", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # İNDİRİMLER BÖLÜMÜ (OTOMATİK ÇEKİLEN)
    dukkanlar = verileri_yukle()
    indirimli_dukkanlar = [d for d in dukkanlar if d.get('indirim') and len(d.get('indirim')) > 2]
    
    if indirimli_dukkanlar:
        st.markdown(f"""
            <div class="discount-banner">
                📢 GÜNÜN FLAŞ İNDİRİMİ: {indirimli_dukkanlar[0]['ad']} -> {indirimli_dukkanlar[0]['indirim']}
            </div>
        """, unsafe_allow_html=True)

    # BENTO GRID KATEGORİLER
    st.markdown("### 🏆 Elite Kategoriler")
    cat_cols = st.columns(4)
    for i, c in enumerate(kategoriler):
        with cat_cols[i % 4]:
            st.markdown(f"""
                <div class="bento-box">
                    <img src="{c['img']}">
                    <div class="bento-label">{c['ad'].upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Süz: {c['ad']}", key=f"cat_{c['ad']}"):
                st.session_state.selected_cat = c['ad']
                st.session_state.selected_id = None
                st.rerun()

    st.divider()

    # DÜKKAN LİSTELEME (AŞAĞI DOĞRU BENTO GRID)
    if st.session_state.selected_id is None:
        filtered = [d for d in dukkanlar if (search_query.lower() in d['ad'].lower() or search_query.lower() in d['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or d['sektor'] == st.session_state.selected_cat)]
        
        shop_cols = st.columns(3)
        for idx, d in enumerate(filtered):
            with shop_cols[idx % 3]:
                st.markdown(f"""
                <div class="shop-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <small style="color:#ffcc00;">{d['sektor'].upper()}</small>
                        <span style="color:#ffcc00;">⭐ {d.get('puan', 0)}</span>
                    </div>
                    <h3 style="margin:5px 0;">{d['ad']}</h3>
                    <p style="font-size:0.8rem; color:#aaa; min-height:40px;">{d['urun']}</p>
                    {"<p style='color:#00ff00; font-size:0.75rem;'>🔥 " + d['indirim'] + "</p>" if d.get('indirim') else ""}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"MAĞAZAYI AÇ: {d['ad']}", key=f"v_{d['id']}"):
                    st.session_state.selected_id = d
                    if db and col_ref: col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI MEYDANINA DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:40px; border:2px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif;">{d['ad']}</h1>
            <p style="font-size:1.5rem;">{d['urun']}</p>
            <hr style="border-color:#333;">
            <p style="font-size:1.2rem; font-style:italic;">"{d['icerik']}"</p>
            <div style="display:flex; justify-content:center; gap:30px; margin:20px 0;">
                <div style="background:#222; padding:10px 20px; border-radius:10px; border:1px solid #ffcc00;">Puan: ⭐ {d.get('puan', 0)}</div>
                <div style="background:#222; padding:10px 20px; border-radius:10px; border:1px solid #ffcc00;">İnceleme: 👁️ {d.get('tıklanma', 0)}</div>
            </div>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:400px; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; font-weight:bold; cursor:pointer; font-size:1.1rem;">
                    🟢 WHATSAPP SİPARİŞ HATTI
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL ESNAF BAŞVURUSU</h3>", unsafe_allow_html=True)
    with st.form("premium_register_v10"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("Resmi WhatsApp (05xx...)")
            n_map = st.text_input("Harita Konum Linki*")
        with c2:
            n_sek = st.selectbox("Sektör", [k["ad"] for k in kategoriler if k["ad"] != "Tümü"])
            n_urn = st.text_input("İmza Ürün / Hizmet")
            n_pwd = st.text_input("Dükkan Şifreniz*", type="password")
        
        n_tanitim = st.text_area("İşletme Hikayesi")
        st.info("Kayıt sonrası dükkanınız 0 puan ile başlar, kullanıcılar puanladıkça sıralamanız yükselir.")
        onay = st.checkbox("Sözleşmeyi ve kurumsal şartları kabul ediyorum.")
        
        if st.form_submit_button("📜 SİSTEME DAHİL OL"):
            if onay and n_ad and n_pwd:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0, "puan": 0, "sifre": n_pwd, "map_url": n_map, "indirim": ""
                }
                col_ref.add(data)
                st.success("Tebrikler! Dörtyol'un dijital geleceğine katıldınız.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. ESNAF PANELİ (DASHBOARD) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL PANELİ</h3>", unsafe_allow_html=True)
        login_ad = st.text_input("Dükkan Adınız")
        login_pwd = st.text_input("Dükkan Şifreniz", type="password")
        if st.button("DASHBOARD'A GİR"):
            all_shops = verileri_yukle()
            match = next((s for s in all_shops if s['ad'] == login_ad and s.get('sifre') == login_pwd), None)
            if match:
                st.session_state.owner_shop_id = match
                st.rerun()
            else: st.error("Hatalı Giriş!")
    else:
        d = st.session_state.owner_shop_id
        st.markdown("<div style='background:rgba(255,255,255,0.05); padding:30px; border-radius:20px; border:1px solid #ffcc00;'>", unsafe_allow_html=True)
        st.subheader(f"📊 {d['ad']} - Dashboard")
        st.write(f"Elite Skoru: ⭐ {d.get('puan', 0)} | Toplam İlgi: 👁️ {d.get('tıklanma', 0)}")
        
        st.divider()
        st.markdown("### 🔥 Günün İndirimini Gir (İndirimler Sekmesine Düşer)")
        u_ind = st.text_input("İndirim Mesajınız (Örn: Tüm kebaplarda %10 indirim!)", value=d.get('indirim', ''))
        st.markdown("### ✏️ Bilgileri Güncelle")
        u_urn = st.text_input("Meşhur Ürün", value=d['urun'])
        u_icr = st.text_area("Tanıtım Yazısı", value=d['icerik'])
        
        if st.button("DEĞİŞİKLİKLERİ KAYDET"):
            if db and col_ref:
                col_ref.document(d['id']).update({"indirim": u_ind, "urun": u_urn, "icerik": u_icr})
                st.success("Dükkan başarıyla güncellendi!")
                time.sleep(1)
                st.rerun()
        
        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Admin Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Sistem Genel Kontrolü Aktif.")
        all_data = verileri_yukle()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']}"):
                # Admin Esnafa Manuel Puan Verebilir
                new_puan = st.slider(f"Skor Güncelle: {item['ad']}", 0, 10, int(item.get('puan', 0)), key=f"p_{item['id']}")
                if st.button(f"Skoru Kaydet: {item['ad']}", key=f"ps_{item['id']}"):
                    col_ref.document(item['id']).update({"puan": new_puan})
                    st.rerun()
                if st.button(f"SİL: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.2; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Architecture | v10.0 Grand Bazaar Edition</div>", unsafe_allow_html=True)
