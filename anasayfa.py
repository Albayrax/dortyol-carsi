import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- SAYFA YAPILANDIRMASI (PREMIUM) ---
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

# --- ÖZEL PREMIUM TASARIM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap');
    
    /* Global Stil */
    .stApp {
        background-color: #fcfaf5;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header (Bordo & Altın Geçişi) */
    .premium-header {
        background: linear-gradient(135deg, #6b0000 0%, #a30000 100%);
        padding: 50px 20px;
        text-align: center;
        border-radius: 0 0 50px 50px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin-bottom: 30px;
    }
    
    .premium-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        margin-bottom: 5px;
        color: #ffcc00;
    }

    /* Kartlar */
    .dukkan-kart {
        background: white;
        padding: 25px;
        border-radius: 25px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        border: 1px solid #eee;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .dukkan-kart:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }

    .sektor-etiket {
        background: #6b0000;
        color: #ffcc00;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Menü Görselleri */
    .menu-img {
        width: 100%;
        height: 200px;
        border-radius: 20px;
        object-fit: cover;
        margin-bottom: 15px;
        border: 3px solid #ffcc0033;
    }

    /* Butonlar */
    .stButton>button {
        background: #6b0000 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 25px !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background: #a30000 !important;
        transform: scale(1.02);
    }

    /* Admin Paneli Güzelleştirme */
    .admin-card {
        background: #fff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UYGULAMA MANTIĞI ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_dukkan' not in st.session_state:
    st.session_state.selected_dukkan = None

# HEADER (TÜM SAYFALARDA)
st.markdown("""
    <div class="premium-header">
        <h1>📍 Dörtyol Çarşı</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Esnafın ve Lezzetin Dijital Buluşma Noktası</p>
    </div>
    """, unsafe_allow_html=True)

# NAVİGASYON TABS
menu_tabs = st.tabs(["🏛️ Çarşıyı Gez", "📝 Dükkan Ekle", "⚙️ Yönetim Paneli"])

# --- 1. SEKMEYE: ÇARŞI GEZİNTİSİ ---
with menu_tabs[0]:
    if st.session_state.selected_dukkan is None:
        dukkanlar = verileri_yukle()
        
        # Filtreleme
        col_f1, col_f2 = st.columns([2,1])
        with col_f1:
            arama = st.text_input("🔍 Dükkan veya Ürün Ara...", placeholder="Örn: Kadayıf")
        with col_f2:
            kategori = st.selectbox("Kategori", ["Tümü", "Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Diğer"])

        st.markdown("---")
        
        # Grid Görünümü
        cols = st.columns(3)
        filtered_list = [d for d in dukkanlar if (arama.lower() in d['ad'].lower() or arama.lower() in d['urun'].lower()) and (kategori == "Tümü" or d['sektor'] == kategori)]
        
        if not filtered_list:
            st.info("Aradığınız kriterlerde dükkan bulunamadı.")
        
        for i, d in enumerate(filtered_list):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="dukkan-kart">
                    <span class="sektor-etiket">{d['sektor']}</span>
                    <h3 style="margin:0; color:#6b0000;">{d['ad']}</h3>
                    <p style="color:#555; margin-top:5px;"><b>Meşhur:</b> {d['urun']}</p>
                    <p style="font-size:0.9rem; color:#888;">📞 {d['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"İncele: {d['ad']}", key=f"detay_{d['id']}"):
                    st.session_state.selected_dukkan = d
                    st.rerun()
    else:
        # DETAY SAYFASI
        d = st.session_state.selected_dukkan
        if st.button("⬅️ Çarşıya Geri Dön"):
            st.session_state.selected_dukkan = None
            st.rerun()
            
        st.markdown(f"""
        <div style="background:white; padding:40px; border-radius:30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <h1 style="color:#6b0000; text-align:center;">{d['ad']}</h1>
            <p style="text-align:center; font-size:1.1rem; color:#666;">Dörtyol, Hatay Esnafı</p>
            <hr>
        """, unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns([1, 1])
        
        with col_d1:
            if d['ad'] == "Fıstıkzade Gurme" or "Fıstık" in d['ad']:
                st.markdown(f'<img src="https://images.unsplash.com/photo-1519676867240-f03562e64548?q=80&w=600" class="menu-img">', unsafe_allow_html=True)
                st.markdown(f'<img src="https://images.unsplash.com/photo-1590483734724-388175d74b6e?q=80&w=600" class="menu-img">', unsafe_allow_html=True)
            else:
                st.markdown(f'<img src="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=600" class="menu-img">', unsafe_allow_html=True)
        
        with col_d2:
            st.subheader("🏢 Dükkan Bilgileri")
            st.info(f"📍 **Adres:** Dörtyol / Hatay")
            st.success(f"📞 **Telefon:** {d['tel']}")
            st.warning(f"🌟 **Meşhur Ürün:** {d['urun']}")
            st.write(f"### Hakkımızda\n{d['icerik']}")
            
            # Paylaşım linki (WhatsApp uyumlu)
            st.markdown(f"""
                <a href="https://wa.me/{d['tel'].replace(' ','')}" target="_blank">
                    <button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold;">
                        💬 WhatsApp'tan Sipariş Ver
                    </button>
                </a>
            """, unsafe_allow_html=True)

# --- 2. SEKMEYE: DÜKKAN EKLEME ---
with menu_tabs[1]:
    st.markdown("### 🏢 Dükkanınızı Çarşıya Ekleyin")
    with st.form("yeni_esnaf"):
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            ad = st.text_input("Dükkan Adı*")
            tel = st.text_input("İletişim Telefonu")
        with c_a2:
            sek = st.selectbox("Sektör", ["Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Diğer"])
            urn = st.text_input("En Meşhur Ürününüz")
        
        icr = st.text_area("Dükkan Tanıtımı (Müşterilerinize ne söylemek istersiniz?)")
        
        if st.form_submit_button("📜 Kaydı Tamamla"):
            if ad and db:
                yeni = {
                    "ad": ad, "tel": tel, "sektor": sek, "urun": urn, "icerik": icr,
                    "tarih": datetime.now().strftime("%d/%m/%Y")
                }
                col_ref.add(yeni)
                st.success(f"{ad} başarıyla çarşıya katıldı! Lütfen sayfayı yenileyin.")
                st.balloons()

# --- 3. SEKMEYE: YÖNETİM PANELİ ---
with menu_tabs[2]:
    st.markdown("### ⚙️ Yönetim Girişi")
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "dortyol31": # Basit bir şifre (Değiştirebilirsin)
        st.success("Yönetim Yetkisi Verildi.")
        dukkanlar = verileri_yukle()
        for d in dukkanlar:
            with st.expander(f"⚙️ {d['ad']}"):
                st.write(f"ID: {d['id']}")
                if st.button(f"Dükkanı Sil: {d['ad']}", key=f"del_{d['id']}"):
                    col_ref.document(d['id']).delete()
                    st.warning(f"{d['ad']} silindi.")
                    st.rerun()
    elif sifre:
        st.error("Hatalı Şifre!")

st.markdown("""
    <div style="text-align:center; padding:30px; color:#888; font-size:0.9rem;">
        © 2024 Albayrax Yazılım | Dörtyol'un İlk Dijital Çarşısı
    </div>
    """, unsafe_allow_html=True)
