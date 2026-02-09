import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v62 Digital Muhtarlık",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

MAHALLELER = [
    "Tümü", "Numuneevler", "Çaylı", "Ocaklı", "Yeşilköy", 
    "Kuzuculu", "Yeniyurt", "Altınçağ", "Özerli", "Sanayi"
]

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except: pass

db = firestore.client() if firebase_admin._apps else None

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. GÖRSEL TASARIM (MIRROR AI & HIGH READABILITY) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF8C00 0%, #001F3F 100%);
        background-image: url('https://www.transparenttextures.com/patterns/cubes.png');
        background-attachment: fixed;
    }

    h1, h2, h3, h4, p, span, b, label { 
        color: white !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        font-family: 'Inter', sans-serif;
    }

    /* İçerik Kartları - Bembeyaz ve Net */
    .content-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #001F3F;
        box-shadow: 8px 8px 0px #001F3F;
        margin-bottom: 20px;
    }
    .content-card h3, .content-card h4, .content-card p, .content-card b, .content-card span {
        color: #001F3F !important;
        text-shadow: none !important;
    }

    /* Kategori Butonları */
    .stButton>button {
        background-color: white !important;
        color: #001F3F !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: 3px solid #001F3F !important;
    }
    .stButton>button:hover {
        background-color: #001F3F !important;
        color: white !important;
    }
    
    .news-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 900;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .badge-vefat { background: #001F3F; color: white !important; }
    .badge-kesinti { background: #D32F2F; color: white !important; }
    .badge-indirim { background: #2E7D32; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SİSTEM BAŞLATICI ---
def seed_v62():
    if db:
        # Örnek Duyurular & Haberler
        h_col = get_col("haberler")
        sample_news = [
            {"tip": "vefat", "baslik": "Vefat Haberi", "mahalle": "Numuneevler", "detay": "Ahmet Öz vefat etmiştir. Cenaze öğle namazında kaldırılacaktır.", "tarih": datetime.now()},
            {"tip": "kesinti", "baslik": "Elektrik Kesintisi", "mahalle": "Çaylı", "detay": "Trafo bakımı nedeniyle 10:00 - 14:00 arası kesinti olacaktır.", "tarih": datetime.now()},
            {"tip": "indirim", "baslik": "Büyük Market İndirimi", "mahalle": "Ocaklı", "detay": "A101'de bu hafta 5L yağ sadece 180 TL!", "tarih": datetime.now()}
        ]
        for n in sample_news: h_col.add(n)

# --- 5. ANA MANTIK ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None

if not st.session_state.is_site_unlocked:
    st.markdown('<h1 style="text-align:center; font-weight:900;">DÖRTYOL DİJİTAL MUHTARLIK</h1>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 3, 1])
    with c:
        pwd = st.text_input("Giriş Anahtarı", type="password")
        if st.button("PORTALI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI: st.session_state.is_site_unlocked = True; st.rerun()
    st.stop()

# --- HEADER ---
st.markdown('<h1 style="text-align:center; font-weight:900; letter-spacing:-2px;">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# --- MAHALLE FİLTRESİ (RADAR) ---
st.markdown("### 📍 Mahalle Radarı")
secili_mahalle = st.selectbox("Mahallenizi Seçin:", MAHALLELER)

tabs = st.tabs(["📢 GÜNCEL AKIŞ", "🏛️ ÇARŞI MEYDANI", "💼 KARİYER", "🔑 ADMIN"])

# --- TAB 0: GÜNCEL AKIŞ (NABIZ) ---
with tabs[0]:
    st.subheader(f"Dörtyol'da Neler Oluyor? ({secili_mahalle})")
    try:
        query = get_col("haberler").order_by("tarih", direction="DESCENDING").limit(20)
        docs = [doc.to_dict() for doc in query.stream()]
        
        # Filtreleme
        if secili_mahalle != "Tümü":
            docs = [d for d in docs if d.get('mahalle') == secili_mahalle]
            
        if not docs:
            st.info(f"{secili_mahalle} mahallesi için şu an güncel bir haber bulunmuyor.")
            
        for d in docs:
            badge_class = f"badge-{d.get('tip', 'duyuru')}"
            st.markdown(f"""
            <div class="content-card">
                <span class="news-badge {badge_class}">{d.get('tip','duyuru')}</span>
                <small style="color:gray; float:right;">{d['tarih'].strftime('%d.%m.%Y')}</small>
                <h4 style="margin:5px 0;">{d['baslik']}</h4>
                <p style="font-size:0.9rem;">📍 <b>Mahalle:</b> {d.get('mahalle','Dörtyol')}</p>
                <p>{d['detay']}</p>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Haberler yükleniyor...")

# --- TAB 1: ÇARŞI ---
with tabs[1]:
    if st.session_state.selected_shop_id is None:
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            for s in shops:
                st.markdown(f'<div class="content-card"><h3>{s["ad"]}</h3><p>{s.get("sektor")} | ⭐ 5.0</p></div>', unsafe_allow_html=True)
                if st.button(f"🏪 Mağazayı İncele: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    st.rerun()
        except: st.write("Dükkanlar yükleniyor...")
    else:
        sid = st.session_state.selected_shop_id
        doc = get_col("dukkanlar").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            if st.button("⬅️ Çarşıya Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            st.image(s.get('img',''), use_container_width=True)
            st.title(s['ad'])
            for p in s.get('urunler', []):
                st.markdown(f'<div class="content-card" style="display:flex; justify-content:space-between;"><b>{p["ad"]}</b><b style="color:green;">{p["fiyat"]} ₺</b></div>', unsafe_allow_html=True)

# --- TAB 3: ADMIN ---
with tabs[3]:
    adm = st.text_input("Yönetici Şifresi", type="password")
    if adm == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı")
        
        with st.expander("📢 Yeni Duyuru / İndirim / Vefat Ekle"):
            d_tip = st.selectbox("Haber Tipi", ["vefat", "kesinti", "indirim", "duyuru"])
            d_mah = st.selectbox("Mahalle", MAHALLELER[1:])
            d_bas = st.text_input("Haber Başlığı")
            d_det = st.text_area("Haber Detayı")
            if st.button("YAYINLA"):
                get_col("haberler").add({
                    "tip": d_tip, "mahalle": d_mah, "baslik": d_bas, 
                    "detay": d_det, "tarih": datetime.now()
                })
                st.success(f"Haber {d_mah} radarına iletildi!")
        
        if st.button("🚀 SİSTEMİ ÖRNEK VERİLERLE KUR"):
            seed_v62()
            st.success("Sistem Dörtyol Mahallelerine göre yapılandırıldı!")

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.5; color:white;'>© {GUNCEL_YIL} Albayrax Digital Muhtarlık v62</div>", unsafe_allow_html=True)
