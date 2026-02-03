import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Sayfa yapılandırması
st.set_page_config(
    page_title="Dörtyol Dijital Çarşı",
    page_icon="🍊",
    layout="wide"
)

# --- FIREBASE BAĞLANTISI ---
APP_ID = "dortyol-carsi-v1"

if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
    except:
        pass

# Veri tabanı referansı
db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- VERİ FONKSİYONLARI ---
def verileri_yukle():
    # Başlangıçta görünecek dükkan (Veri tabanı boşsa)
    varsayilan = [{
        "id": "1",
        "ad": "Fıstıkzade Gurme",
        "tel": "0532 123 45 67",
        "sektor": "Tatlıcı",
        "urun": "Özel Fıstıklı Hasır Kadayıf",
        "icerik": "Dörtyol'un en seçkin fıstıklı lezzet durağı. Geleneksel tarifler, modern sunum.",
        "goruntulenme": 0,
        "kayit_tarihi": datetime.now().strftime("%d/%m/%Y")
    }]
    if db and col_ref:
        try:
            docs = col_ref.stream()
            liste = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            return liste if liste else varsayilan
        except:
            return varsayilan
    return varsayilan

def dukkan_kaydet(yeni_dukkan):
    if db and col_ref:
        try:
            col_ref.add(yeni_dukkan)
            return True
        except:
            return False
    return False

# --- TASARIM (KOYU KIRMIZI ŞIK TEMA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Montserrat:wght@400;700&display=swap');
    
    /* Arka Plan Kırmızı Tonları */
    .stApp {
        background: linear-gradient(135deg, #4a0000 0%, #8b0000 50%, #b30000 100%);
        color: white !important;
    }
    
    header {visibility: hidden;}
    
    /* Kart Tasarımları */
    .dukkan-kart {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border-left: 10px solid #ffcc00;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        color: #1a1a1a;
    }
    
    /* Menü ve Detay Sayfası */
    .detail-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 40px;
        border-radius: 30px;
        color: #000;
        border: 5px solid #ffcc00;
    }
    
    .menu-item {
        display: flex;
        align-items: center;
        background: #fdfdfd;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        gap: 15px;
    }
    
    .menu-img {
        width: 120px;
        height: 100px;
        border-radius: 10px;
        object-fit: cover;
    }

    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    p, span { font-family: 'Montserrat', sans-serif !important; }
    
    .stButton>button {
        background-color: #ffcc00 !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UYGULAMA MANTIĞI ---
if 'secili_dukkan' not in st.session_state:
    st.session_state.secili_dukkan = None

if st.session_state.secili_dukkan is None:
    st.markdown("<h1 style='text-align:center; color:#ffcc00;'>📍 Dörtyol Dijital Çarşı</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 Çarşıyı Geşfet", "🏢 Esnaf Kaydı"])
    
    with tab1:
        dukkanlar = verileri_yukle()
        cols = st.columns(2)
        for i, d in enumerate(dukkanlar):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="dukkan-kart">
                    <h2 style="margin:0; color:#b30000;">{d['ad']}</h2>
                    <p><b>Kategori:</b> {d['sektor']}</p>
                    <p style="color:#555; font-size:0.9em;">📍 Dörtyol / Hatay</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"İncele: {d['ad']}", key=f"btn_{d['id']}"):
                    st.session_state.secili_dukkan = d
                    st.rerun()
    
    with tab2:
        with st.form("yeni_kayit"):
            st.subheader("Yeni Esnaf Kaydı")
            ad = st.text_input("Dükkan Adı")
            tel = st.text_input("Telefon")
            sek = st.selectbox("Sektör", ["Tatlıcı", "Restoran", "Kuyumcu", "Giyim", "Diğer"])
            urn = st.text_input("Meşhur Ürününüz")
            icr = st.text_area("Kısa Tanıtım")
            if st.form_submit_button("Sisteme Kaydet"):
                if ad and db:
                    yeni = {"ad": ad, "tel": tel, "sektor": sek, "urun": urn, "icerik": icr, "goruntulenme": 0, "kayit_tarihi": datetime.now().strftime("%d/%m/%Y")}
                    if dukkan_kaydet(yeni):
                        st.success("Dükkan başarıyla eklendi!")
                        st.rerun()

else:
    # --- DETAY SAYFASI (FISTIKZADE ÖZEL) ---
    d = st.session_state.secili_dukkan
    if st.button("⬅️ Çarşıya Dön"):
        st.session_state.secili_dukkan = None
        st.rerun()
    
    st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:#b30000;'>{d['ad']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>📞 {d['tel']} | 🕒 09:00 - 22:00</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if d['ad'] == "Fıstıkzade Gurme":
        st.subheader("🟢 Fıstıklı Lezzet Menüsü")
        lezzetler = [
            {"isim": "Fıstıklı Hasır Kadayıf", "fiyat": "240 TL", "resim": "https://images.unsplash.com/photo-1590483734724-388175d74b6e?auto=format&fit=crop&w=300"},
            {"isim": "Fıstık Sarma (Özel)", "fiyat": "320 TL", "resim": "https://media.istockphoto.com/id/1184323030/photo/traditional-turkish-dessert-kadayif-with-pistachio.jpg?s=612x612&w=0&k=20&c=uVzW_YpQ8vGf-z1D3z1N7y-Wv4U_W3r1N-d_D1p7Y1Y1Y="},
            {"isim": "Kaymaklı Şöbiyet", "fiyat": "280 TL", "resim": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=300"}
        ]
        for l in lezzetler:
            st.markdown(f"""
            <div class="menu-item">
                <img src="{l['resim']}" class="menu-img">
                <div style="flex-grow:1;">
                    <h3 style="margin:0;">{l['isim']}</h3>
                    <p style="color:#b30000; font-weight:bold;">{l['fiyat']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write(f"### Meşhur Ürün: {d['urun']}")
        st.write(d['icerik'])
    
    st.markdown("</div>", unsafe_allow_html=True)
