import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Dijital Çarşı",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FIREBASE BAĞLANTISI ---
APP_ID = "dortyol-carsi-v1"
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
    except: pass

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except: pass

# --- VERİ İŞLEMLERİ ---
def verileri_yukle():
    if db and col_ref:
        try:
            docs = col_ref.stream()
            return [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: return []
    return []

# --- ULTRA PREMIUM DARK MODE TASARIM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;600&display=swap');
    
    /* Ana Arka Plan: Koyu Bordo'dan Siyaha Geçiş */
    .stApp {
        background: linear-gradient(180deg, #3d0000 0%, #1a0000 50%, #000000 100%);
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header Alanı */
    .premium-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        padding: 60px 20px;
        text-align: center;
        border-radius: 0 0 60px 60px;
        border-bottom: 2px solid #ffcc00;
        margin-bottom: 40px;
    }
    
    .premium-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        margin-bottom: 10px;
        color: #ffcc00;
        text-shadow: 2px 2px 10px rgba(255, 204, 0, 0.3);
    }

    /* Dükkan Kartları */
    .dukkan-kart {
        background: rgba(255, 255, 255, 0.07);
        padding: 30px;
        border-radius: 30px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 204, 0, 0.2);
        transition: all 0.4s ease;
        text-align: center;
    }
    
    .dukkan-kart:hover {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid #ffcc00;
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }

    .sektor-etiket {
        background: #ffcc00;
        color: #000;
        padding: 6px 18px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 15px;
        text-transform: uppercase;
    }

    /* Detay Sayfası Konteyneri */
    .detail-container {
        background: rgba(0, 0, 0, 0.6);
        padding: 40px;
        border-radius: 40px;
        border: 2px solid #ffcc00;
        color: white;
    }

    /* Görseller */
    .menu-img {
        width: 100%;
        height: 250px;
        border-radius: 25px;
        object-fit: cover;
        margin-bottom: 20px;
        border: 2px solid #ffcc00;
    }

    /* Butonlar */
    .stButton>button {
        background: linear-gradient(90deg, #ffcc00 0%, #ff9900 100%) !important;
        color: #000 !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 12px 30px !important;
        font-weight: 800 !important;
        width: 100%;
        font-size: 1rem !important;
    }
    
    /* Input ve Form Alanları */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 204, 0, 0.3) !important;
        border-radius: 12px !important;
    }

    /* Tablar */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #aaa !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ffcc00 !important;
        border-bottom-color: #ffcc00 !important;
    }

    h2, h3 { color: #ffcc00 !important; font-family: 'Playfair Display', serif !important; }
    p { color: #eeeeee !important; }
    </style>
    """, unsafe_allow_html=True)

# --- UYGULAMA AKIŞI ---
if 'selected_dukkan' not in st.session_state:
    st.session_state.selected_dukkan = None

# HEADER
st.markdown("""
    <div class="premium-header">
        <h1>📍 DÖRTYOL ÇARŞI</h1>
        <p style="font-size: 1.3rem; letter-spacing: 2px; color: #ffcc00;">DİJİTAL ESNAF REHBERİ & LEZZET DURAKLARI</p>
    </div>
    """, unsafe_allow_html=True)

# SEKMELER
tabs = st.tabs(["💎 ÇARŞIYI KEŞFET", "🏢 ESNAF KAYDI", "🔑 YÖNETİM"])

# --- 1. ÇARŞI KEŞFİ ---
with tabs[0]:
    if st.session_state.selected_dukkan is None:
        dukkanlar = verileri_yukle()
        
        col_f1, col_f2 = st.columns([3,1])
        with col_f1:
            arama = st.text_input("🔍 Aradığınız lezzet veya dükkan...", placeholder="Örn: Fıstıklı Kadayıf, Kebap...")
        with col_f2:
            kategori = st.selectbox("Kategori", ["Tümü", "Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Diğer"])

        st.markdown("<br>", unsafe_allow_html=True)
        
        filtered = [d for d in dukkanlar if (arama.lower() in d['ad'].lower() or arama.lower() in d['urun'].lower()) and (kategori == "Tümü" or d['sektor'] == kategori)]
        
        if not filtered:
            st.warning("Aradığınız kriterde bir dükkan henüz kayıtlı değil.")
        
        # Grid Sistemi
        cols = st.columns(3)
        for i, d in enumerate(filtered):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="dukkan-kart">
                    <span class="sektor-etiket">{d['sektor']}</span>
                    <h2 style="margin:10px 0;">{d['ad']}</h2>
                    <p><b>🌟 Meşhur:</b> {d['urun']}</p>
                    <p style="color:#ffcc00; font-weight:bold;">📍 Dörtyol / Hatay</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔎 {d['ad']} İncele", key=f"d_{d['id']}"):
                    st.session_state.selected_dukkan = d
                    st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_dukkan
        if st.button("⬅️ ÇARŞIYA DÖN"):
            st.session_state.selected_dukkan = None
            st.rerun()
            
        st.markdown("<div class='detail-container'>", unsafe_allow_html=True)
        
        col_img, col_txt = st.columns([1, 1])
        
        with col_img:
            # Fıstıkzade ve Tatlıcılar için Premium Görseller
            if "Fıstık" in d['ad'] or d['sektor'] == "Tatlıcı":
                st.markdown('<img src="https://images.unsplash.com/photo-1590483734724-388175d74b6e?q=80&w=800" class="menu-img">', unsafe_allow_html=True)
                st.markdown('<img src="https://images.unsplash.com/photo-1519676867240-f03562e64548?q=80&w=800" class="menu-img">', unsafe_allow_html=True)
            else:
                st.markdown('<img src="https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800" class="menu-img">', unsafe_allow_html=True)
        
        with col_txt:
            st.markdown(f"<h1 style='color:#ffcc00;'>{d['ad']}</h1>", unsafe_allow_html=True)
            st.markdown(f"### 🌟 Meşhur Ürün: {d['urun']}")
            st.write(f"**Tanıtım:**\n{d['icerik']}")
            st.divider()
            st.markdown(f"### 📞 İletişim: {d['tel']}")
            
            # WhatsApp Sipariş Butonu
            wa_num = d['tel'].replace(" ", "").replace("+", "")
            st.markdown(f"""
                <a href="https://wa.me/{wa_num}" target="_blank">
                    <button style="width:100%; background:#25D366; color:white; border:none; padding:18px; border-radius:15px; cursor:pointer; font-weight:bold; font-size:1.1rem;">
                        🟢 WHATSAPP İLE SİPARİŞ VER / SORU SOR
                    </button>
                </a>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. ESNAF KAYDI ---
with tabs[1]:
    st.markdown("<h2 style='text-align:center;'>🏢 Dükkanınızı Çarşıya Taşıyın</h2>", unsafe_allow_html=True)
    st.write("Dörtyol'un en büyük dijital rehberinde yerinizi almak için formu eksiksiz doldurun.")
    
    with st.form("premium_kayit"):
        c1, c2 = st.columns(2)
        with c1:
            ad = st.text_input("Dükkan Adı*")
            tel = st.text_input("İletişim Numarası (Örn: 05xx...)")
        with c2:
            sek = st.selectbox("Sektör", ["Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Diğer"])
            urn = st.text_input("En Meşhur Ürününüz")
        
        tanitim = st.text_area("Müşterilerinize Mesajınız (Dükkan Tanıtımı)")
        
        if st.form_submit_button("🌟 KAYDI TAMAMLA VE YAYINLA"):
            if ad and db and col_ref:
                yeni_dukkan = {
                    "ad": ad, "tel": tel, "sektor": sek, "urun": urn, "icerik": tanitim,
                    "tarih": datetime.now().strftime("%d/%m/%Y")
                }
                col_ref.add(yeni_dukkan)
                st.success(f"Tebrikler! {ad} artık Dörtyol Dijital Çarşı'da.")
                st.balloons()

# --- 3. YÖNETİM ---
with tabs[2]:
    st.markdown("### 🔑 Yönetici Girişi")
    sifre = st.text_input("Giriş Anahtarı", type="password")
    
    if sifre == "dortyol31":
        st.success("Yönetim Yetkisi Onaylandı.")
        dukkanlar = verileri_yukle()
        for d in dukkanlar:
            with st.expander(f"⚙️ {d['ad']}"):
                if st.button(f"🗑️ SİL: {d['ad']}", key=f"del_{d['id']}"):
                    col_ref.document(d['id']).delete()
                    st.warning(f"{d['ad']} sistemden kaldırıldı.")
                    st.rerun()
    elif sifre:
        st.error("Hatalı Giriş Anahtarı!")

st.markdown("<br><hr><p style='text-align:center; color:#888;'>© 2024 Albayrax Premium Digital | Dörtyol Hatay</p>", unsafe_allow_html=True)
