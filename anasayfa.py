import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Dijital Çarşı 2026",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AYARLAR ---
ADMIN_SIFRE = "dortyol31"
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
        st.error(f"Bağlantı Hatası: {e}")

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- FONKSİYONLAR ---
def verileri_yukle():
    if db and col_ref:
        try:
            # RULE 2: Basit sorgu, sıralama JS tarafında yapılacak
            docs = col_ref.stream()
            return [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except:
            return []
    return []

# --- ULTRA PREMIUM & INTERACTIVE CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Montserrat:wght@300;400;600&display=swap');
    
    /* Hareketli Arka Plan */
    .stApp {{
        background: linear-gradient(-45deg, #1a0000, #3d0000, #000000, #220000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Yüzen Baloncuk Efekti */
    .bubble-bg {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
        overflow: hidden;
    }}
    .bubble {{
        position: absolute;
        bottom: -100px;
        width: 40px; height: 40px;
        background: rgba(255, 204, 0, 0.1);
        border-radius: 50%;
        animation: rise 10s infinite ease-in;
    }}
    @keyframes rise {{
        0% {{ bottom: -100px; transform: translateX(0); }}
        50% {{ transform: translateX(100px); }}
        100% {{ bottom: 1080px; transform: translateX(-200px); }}
    }}

    /* Header Tasarımı */
    .header-section {{
        padding: 20px 0;
        text-align: center;
        margin-top: -50px;
    }}
    .header-section h2 {{
        font-family: 'Cinzel', serif;
        font-size: 2.8rem;
        color: #ffcc00;
        letter-spacing: 5px;
        margin-bottom: 5px;
        text-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
    }}
    .header-section p {{
        font-size: 0.9rem;
        letter-spacing: 3px;
        color: #ddd;
        opacity: 0.8;
    }}

    /* Premium Kartlar */
    .dukkan-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 204, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
    }}
    .dukkan-card:hover {{
        border: 1px solid #ffcc00;
        background: rgba(255, 204, 0, 0.05);
        transform: scale(1.03);
    }}

    /* Butonlar */
    .stButton>button {{
        background: linear-gradient(90deg, #ffcc00 0%, #ff9900 100%) !important;
        color: #000 !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 10px 20px !important;
    }}

    /* Form & Input */
    input, textarea {{
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,204,0,0.3) !important;
        border-radius: 10px !important;
        color: white !important;
    }}

    /* Sözleşme Alanı */
    .agreement-box {{
        background: rgba(0,0,0,0.4);
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #ffcc00;
        font-size: 0.85rem;
        max-height: 150px;
        overflow-y: scroll;
        margin-bottom: 10px;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 50px 0;
        color: #666;
        font-size: 0.8rem;
    }}
    </style>
    
    <div class="bubble-bg">
        <div class="bubble" style="left:10%; width:80px; height:80px; animation-duration:8s;"></div>
        <div class="bubble" style="left:20%; width:40px; height:40px; animation-duration:12s; animation-delay:2s;"></div>
        <div class="bubble" style="left:70%; width:60px; height:60px; animation-duration:10s; animation-delay:4s;"></div>
        <div class="bubble" style="left:85%; width:30px; height:30px; animation-duration:15s;"></div>
    </div>
    """, unsafe_allow_html=True)

# --- UYGULAMA İÇERİĞİ ---
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# HEADER
st.markdown(f"""
    <div class="header-section">
        <h2>DÖRTYOL ÇARŞI</h2>
        <p>PREMIUM ESNAF AĞI & LEZZET DURAKLARI</p>
    </div>
    """, unsafe_allow_html=True)

# ORTALANMIŞ İÇERİK İÇİN COLUMNS
_, center_col, _ = st.columns([1, 6, 1])

with center_col:
    tabs = st.tabs(["💎 ÇARŞIYI KEŞFET", "🏢 KURUMSAL KAYIT", "🔑 YÖNETİM"])

    # 1. SEKME: KEŞFET
    with tabs[0]:
        if st.session_state.selected_id is None:
            dukkanlar = verileri_yukle()
            
            # Filtre Paneli
            f1, f2 = st.columns([3,1])
            with f1:
                search = st.text_input("🔍 Aradığınız esnaf veya ürün...", placeholder="Örn: Portakal, Kebap, Altın...")
            with f2:
                cat = st.selectbox("Sektör Seçin", ["Tümü", "Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Diğer"])

            # Filtreleme
            filtered = [d for d in dukkanlar if (search.lower() in d['ad'].lower() or search.lower() in d['urun'].lower()) and (cat == "Tümü" or d['sektor'] == cat)]
            
            if not filtered:
                st.info("Henüz bu kategoride bir kayıt bulunmuyor.")
            
            # Grid
            grid_cols = st.columns(2)
            for i, d in enumerate(filtered):
                with grid_cols[i % 2]:
                    st.markdown(f"""
                    <div class="dukkan-card">
                        <span style="color:#ffcc00; font-size:0.7rem; font-weight:700;">{d['sektor'].upper()}</span>
                        <h3 style="margin:5px 0; color:white;">{d['ad']}</h3>
                        <p style="font-size:0.9rem; color:#bbb;"><b>İmza Lezzet:</b> {d['urun']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"DETAYLARI İNCELE: {d['ad']}", key=f"view_{d['id']}"):
                        st.session_state.selected_id = d
                        st.rerun()
        else:
            # DETAY GÖRÜNÜMÜ
            d = st.session_state.selected_id
            if st.button("⬅️ LİSTEYE DÖN"):
                st.session_state.selected_id = None
                st.rerun()
            
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:30px; border:2px solid #ffcc00;">
                <h1 style="color:#ffcc00; text-align:center;">{d['ad']}</h1>
                <p style="text-align:center; letter-spacing:2px;">DÖRTYOL / HATAY ESNAFI</p>
                <hr style="border-color:rgba(255,204,0,0.3);">
                <div style="display:flex; justify-content:space-around; text-align:center; padding:20px 0;">
                    <div><h5 style="color:#ffcc00;">İmza Ürün</h5><p>{d['urun']}</p></div>
                    <div><h5 style="color:#ffcc00;">Kategori</h5><p>{d['sektor']}</p></div>
                </div>
                <p style="font-style:italic; text-align:center; padding:20px;">"{d['icerik']}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            wa_num = d['tel'].replace(" ", "").replace("+", "")
            st.markdown(f"""
                <a href="https://wa.me/{wa_num}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; cursor:pointer; font-weight:bold; font-size:1rem; margin-top:10px;">
                        💚 WHATSAPP ÜZERİNDEN İLETİŞİME GEÇ
                    </button>
                </a>
            """, unsafe_allow_html=True)

    # 2. SEKME: ESNAF KAYDI (KURUMSAL)
    with tabs[1]:
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>YENİ ESNAF BAŞVURUSU</h3>", unsafe_allow_html=True)
        
        with st.form("kurumsal_kayit"):
            c1, c2 = st.columns(2)
            with c1:
                new_ad = st.text_input("İşletme Adı*")
                new_tel = st.text_input("Kurumsal İletişim (05xx...)")
            with c2:
                new_sek = st.selectbox("Faaliyet Alanı", ["Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Teknoloji", "Diğer"])
                new_urn = st.text_input("İmza Ürününüz / Hizmetiniz")
            
            new_tanitim = st.text_area("İşletme Hikayesi ve Tanıtım")
            
            st.markdown("---")
            st.markdown("**ESNAF HİZMET VE KALİTE SÖZLEŞMESİ**")
            st.markdown("""
                <div class="agreement-box">
                    1. İşbu sözleşme, Dörtyol Dijital Çarşı platformunda yer alan esnafın hizmet kalitesini korumayı amaçlar.<br>
                    2. Esnaf, sunduğu ürün ve hizmetlerde dürüstlük ve kalite esaslarına uyacağını taahhüt eder.<br>
                    3. Müşteri memnuniyetini ön planda tutacağını, verilen iletişim numaralarından makul sürelerde yanıt vereceğini kabul eder.<br>
                    4. Platformun bir yardımlaşma ve dijitalleşme projesi olduğunu bilerek, topluluk kurallarına aykırı içerik paylaşmayacağını onaylar.<br>
                    5. Hatalı veya yanıltıcı bilgi girişi durumunda üyeliğinin askıya alınabileceğini peşinen kabul eder.
                </div>
            """, unsafe_allow_html=True)
            
            onay = st.checkbox("Sözleşme maddelerini okudum ve dijital imzamla onaylıyorum.")
            
            if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
                if not onay:
                    st.error("Lütfen sözleşmeyi onaylayın.")
                elif not new_ad or not new_tel:
                    st.error("Yıldızlı alanlar zorunludur.")
                elif db and col_ref:
                    data = {
                        "ad": new_ad, "tel": new_tel, "sektor": new_sek, 
                        "urun": new_urn, "icerik": new_tanitim,
                        "tarih": datetime.now().strftime("%d/%m/%Y"),
                        "onayli": True
                    }
                    col_ref.add(data)
                    st.success("Tebrikler! Dükkanınız Dörtyol'un dijital çarşısına başarıyla eklendi.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # 3. SEKME: YÖNETİM
    with tabs[2]:
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>ADMİN KONTROL PANELİ</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Giriş Anahtarı", type="password")
        
        if pwd == ADMIN_SIFRE:
            st.success("Hoş geldin Albayrax. Sistem Kontrol Altında.")
            all_data = verileri_yukle()
            for item in all_data:
                with st.expander(f"⚙️ {item['ad']} - {item.get('tarih','-')}"):
                    st.write(f"İletişim: {item['tel']}")
                    if st.button(f"🗑️ BU DÜKKANI SİSTEMDEN KALDIR", key=f"del_{item['id']}"):
                        col_ref.document(item['id']).delete()
                        st.warning(f"{item['ad']} silindi.")
                        st.rerun()
        elif pwd:
            st.error("Hatalı Giriş Anahtarı! Lütfen tekrar deneyin.")

# FOOTER
st.markdown(f"""
    <div class="footer">
        <p>© {GUNCEL_YIL} Albayrax Premium Digital Architecture | Dörtyol / Hatay</p>
        <p style="opacity:0.5;">Geleceğin Esnaf Ağı Yayında</p>
        <div style="height:100px;"></div>
    </div>
    """, unsafe_allow_html=True)
