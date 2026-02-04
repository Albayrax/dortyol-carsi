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
if 'sort_filter' not in st.session_state:
    st.session_state.sort_filter = "Puan (Yüksek)"

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            # Filtreleme mantığı
            if st.session_state.sort_filter == "Puan (Yüksek)":
                return sorted(data, key=lambda x: x.get('puan', 0), reverse=True)
            elif st.session_state.sort_filter == "En Çok İncelenen":
                return sorted(data, key=lambda x: x.get('tıklanma', 0), reverse=True)
            return data
        except: return []
    return []

# --- ROYAL ELITE UI & REELS ANIMATIONS (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {{
        background: linear-gradient(180deg, #0a0000 0%, #200000 50%, #000000 100%);
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Tepe Başlık */
    .header-box {{
        text-align: center;
        margin-top: -90px;
        padding-bottom: 5px;
        transition: 0.5s;
    }}
    .header-box h1 {{
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        color: #ffcc00;
        letter-spacing: 10px;
        text-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
    }}

    /* Reels Tarzı Dikey Kartlar */
    .reels-card {{
        background: rgba(255, 255, 255, 0.04);
        border-radius: 25px;
        padding: 0;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 204, 0, 0.15);
        overflow: hidden;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .reels-card:hover {{
        transform: scale(1.02);
        border: 1px solid #ffcc00;
        background: rgba(255, 255, 255, 0.08);
    }}
    
    .card-img {{
        width: 100%;
        height: 350px; /* Daha dikey ve büyük görseller */
        object-fit: cover;
        border-bottom: 3px solid #ffcc00;
    }}

    .card-info {{
        padding: 20px;
        text-align: center;
    }}

    /* Kategori Bölümleri */
    .section-title {{
        font-family: 'Cinzel', serif;
        font-size: 1.5rem;
        color: #ffcc00;
        border-left: 5px solid #ffcc00;
        padding-left: 15px;
        margin: 40px 0 20px 0;
    }}

    /* Arama ve Filtre Çubuğu */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 20px !important;
        color: white !important;
        height: 50px;
    }}

    /* Puan ve İndirim Etiketleri */
    .badge-puan {{
        background: #ffcc00;
        color: black;
        padding: 5px 12px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 0.8rem;
    }}
    .badge-indirim {{
        background: #00ff00;
        color: black;
        padding: 5px 12px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 0.8rem;
        animation: blink 1.5s infinite;
    }}
    @keyframes blink {{
        0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }}
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
        if st.button("SARAYIN KAPILARINI AÇ"):
            if key_input == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Anahtar.")
    st.stop()

# --- ANA İÇERİK ---

st.markdown('<div class="header-box"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)

# ARAMA VE SIRALAMA (FİLTRELEME)
c_search, c_sort = st.columns([3, 1])
with c_search:
    search_q = st.text_input("", placeholder="🔍 Neye ihtiyacınız var? (Dükkan, Kebap, Altın...)", key="v11_search")
with c_sort:
    st.session_state.sort_filter = st.selectbox("Sıralama / Filtre", ["Puan (Yüksek)", "En Çok İncelenen", "En Yeni"])

# SEKMELER
tabs = st.tabs(["💎 ÇARŞIYI KEŞFET", "📝 KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# SEKTÖRLER VE GÖRSELLERİ
sektorler = {
    "Yemek & Tatlı Dünyası": ["Tatlıcı", "Kebapçı", "Gıda"],
    "Moda & Kuyumculuk": ["Kuyumcu", "Giyim"],
    "Teknoloji & Otomotiv": ["Teknoloji", "Otomotiv"],
    "Sağlık & Hizmet": ["Eczane", "Diğer"],
    "Ev & Yapı": ["Mobilya", "Hırdavat", "Züccaciye", "Emlak"]
}

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    if st.session_state.selected_id is None:
        dukkanlar = verileri_yukle()
        
        # 📢 FLAŞ İNDİRİMLER (REELS TARZI TEK SATIR KAYDIRILABİLİR)
        indirimli = [d for d in dukkanlar if d.get('indirim') and len(d.get('indirim')) > 1]
        if indirimli:
            st.markdown("<h3 class='section-title'>🔥 FLAŞ İNDİRİMLER</h3>", unsafe_allow_html=True)
            cols_ind = st.columns(len(indirimli) if len(indirimli) < 4 else 4)
            for idx, ind in enumerate(indirimli[:4]):
                with cols_ind[idx]:
                    st.markdown(f"""
                        <div class="reels-card" style="border: 2px solid #00ff00;">
                            <div style="padding:15px; text-align:center;">
                                <span class="badge-indirim">FIRSAT</span>
                                <h4 style="color:#ffcc00; margin:10px 0;">{ind['ad']}</h4>
                                <p style="font-size:0.9rem;">{ind['indirim']}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Fırsatı Gör: {ind['ad']}", key=f"ind_{ind['id']}"):
                        st.session_state.selected_id = ind
                        st.rerun()

        # 🏢 SEKTÖREL DİKEY AKIŞ
        for s_title, s_cats in sektorler.items():
            s_data = [d for d in dukkanlar if d['sektor'] in s_cats and (search_q.lower() in d['ad'].lower() or search_q.lower() in d['urun'].lower())]
            
            if s_data:
                st.markdown(f"<h3 class='section-title'>{s_title}</h3>", unsafe_allow_html=True)
                
                # Sektöre özel filtreleme (Dinamik)
                if "Otomotiv" in s_cats:
                    st.caption("Filtre: En Düşük KM'li ve En Yeni Modeller Önce Listelenir.")
                
                grid = st.columns(2) # Reels gibi geniş kartlar
                for idx, d in enumerate(s_data):
                    with grid[idx % 2]:
                        # Görsel Belirleme
                        img_url = "https://images.unsplash.com/photo-1571214050215-08e92a8397a7?q=80&w=600" if d['sektor'] == "Tatlıcı" else \
                                  "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=600" if d['sektor'] == "Kebapçı" else \
                                  "https://images.unsplash.com/photo-1588444839138-0422329d145f?q=80&w=600" if d['sektor'] == "Kuyumcu" else \
                                  "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=600" if d['sektor'] == "Otomotiv" else \
                                  "https://images.unsplash.com/photo-1530124560676-41bc1275d428?q=80&w=600"
                        
                        st.markdown(f"""
                        <div class="reels-card">
                            <img src="{img_url}" class="card-img">
                            <div class="card-info">
                                <div style="display:flex; justify-content:center; gap:10px; margin-bottom:10px;">
                                    <span class="badge-puan">⭐ {d.get('puan', 0)} / 10</span>
                                    <span style="color:#aaa; font-size:0.8rem;">👁️ {d.get('tıklanma', 0)}</span>
                                </div>
                                <h2 style="color:#ffcc00; margin:0;">{d['ad']}</h2>
                                <p style="font-size:1.1rem; font-weight:600; color:#ddd; margin:10px 0;">{d['urun']}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"MAĞAZAYI KEŞFET: {d['ad']}", key=f"v_{d['id']}"):
                            st.session_state.selected_id = d
                            if db and col_ref: col_ref.document(d['id']).update({"tıklanma": firestore.Increment(1)})
                            st.rerun()
    else:
        # DETAY SAYFASI (TAM EKRAN PREMIUM)
        d = st.session_state.selected_id
        if st.button("⬅️ ÇARŞI MEYDANINA DÖN"):
            st.session_state.selected_id = None
            st.rerun()
        
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.8); padding:60px; border-radius:40px; border:3px solid #ffcc00; text-align:center;">
            <h1 style="color:#ffcc00; font-family:'Cinzel', serif; font-size:3.5rem; margin:0;">{d['ad']}</h1>
            <p style="font-size:1.8rem; font-weight:700;">{d['urun']}</p>
            <hr style="border-color:#444;">
            <p style="font-size:1.3rem; line-height:1.8; color:#ccc; font-style:italic;">"{d['icerik']}"</p>
            <div style="display:flex; justify-content:center; gap:40px; margin:30px 0;">
                <div style="background:#111; padding:15px 30px; border-radius:20px; border:2px solid #ffcc00;">
                    <h5 style="color:#ffcc00; margin:0;">ELITE SKORU</h5>
                    <p style="font-size:1.5rem; margin:0;">⭐ {d.get('puan', 0)}</p>
                </div>
                <div style="background:#111; padding:15px 30px; border-radius:20px; border:2px solid #ffcc00;">
                    <h5 style="color:#ffcc00; margin:0;">POPÜLERLİK</h5>
                    <p style="font-size:1.5rem; margin:0;">👁️ {d.get('tıklanma', 0)}</p>
                </div>
            </div>
            <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; max-width:500px; background:#25D366; color:white; border:none; padding:20px; border-radius:20px; font-weight:bold; font-size:1.5rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL ESNAF BAŞVURUSU</h3>", unsafe_allow_html=True)
    with st.form("elite_register_v11"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("WhatsApp No (05xx...)")
            n_map = st.text_input("Harita Konum Linki*")
        with c2:
            n_sek = st.selectbox("Sektör", [cat for sublist in sektorler.values() for cat in sublist])
            n_urn = st.text_input("İmza Ürün / Hizmet")
            n_pwd = st.text_input("Dükkan Şifreniz*", type="password")
        
        n_tanitim = st.text_area("İşletme Hikayesi ve Müşteri Mesajı")
        st.markdown("""
            <div style="background:rgba(255,204,0,0.05); padding:15px; border-radius:15px; border:1px dashed #ffcc00; font-size:0.8rem; color:#ddd;">
                <b>ESNAF TAAHHÜTNAMESİ:</b> Dörtyol Dijital Çarşı platformuna kayıt olan işletmemiz; dürüst ticaret, yüksek kalite ve mutlak müşteri memnuniyetini kurumsal bir ilke olarak kabul ettiğini beyan eder.
            </div>
        """, unsafe_allow_html=True)
        onay = st.checkbox("Sözleşmeyi ve kurumsal şartları dijital imzamla onaylıyorum.")
        
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA VE YAYINLA"):
            if onay and n_ad and n_pwd:
                data = {
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                    "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y"),
                    "tıklanma": 0, "puan": 0, "sifre": n_pwd, "map_url": n_map, "indirim": ""
                }
                col_ref.add(data)
                st.success("Tebrikler! Dükkanınız Dörtyol'un dijital geleceğine kurumsal adımını attı.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# --- 3. ESNAF PANELİ (DASHBOARD) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
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
        st.subheader(f"📊 {d['ad']} - Yönetim Paneli")
        st.write(f"Elite Skoru: ⭐ {d.get('puan', 0)} | Popülerlik: 👁️ {d.get('tıklanma', 0)}")
        st.divider()
        st.markdown("### 🔥 Flaş İndirim Girişi")
        u_ind = st.text_input("İndirim Mesajınız (Örn: Bugün tüm ürünlerde %20 indirim!)", value=d.get('indirim', ''))
        st.markdown("### ✏️ Bilgi Güncelleme")
        u_urn = st.text_input("Meşhur Ürün/Hizmet", value=d['urun'])
        u_icr = st.text_area("Tanıtım Yazısı", value=d['icerik'])
        if st.button("DEĞİŞİKLİKLERİ KAYDET"):
            if db and col_ref:
                col_ref.document(d['id']).update({"indirim": u_ind, "urun": u_urn, "icerik": u_icr})
                st.success("Dükkan güncellendi!")
                time.sleep(1)
                st.rerun()
        if st.button("🚪 ÇIKIŞ YAP"):
            st.session_state.owner_shop_id = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Sistem Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Sistem Genel Kontrolü Aktif - Merhaba Albayrax.")
        all_data = verileri_yukle()
        for item in all_data:
            with st.expander(f"⚙️ {item['ad']}"):
                p_val = st.slider("Elite Skoru Ver (0-10)", 0, 10, int(item.get('puan', 0)), key=f"p_{item['id']}")
                if st.button(f"Skoru Onayla: {item['ad']}", key=f"ps_{item['id']}"):
                    col_ref.document(item['id']).update({"puan": p_val})
                    st.rerun()
                if st.button(f"SİL: {item['ad']}", key=f"del_{item['id']}"):
                    col_ref.document(item['id']).delete()
                    st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:150px; opacity:0.2; font-size:0.7rem; letter-spacing:3px;'>© {GUNCEL_YIL} Albayrax Premium Architecture | v11.0 Elite Flow Edition</div>", unsafe_allow_html=True)
