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

# --- AYARLAR (Burayı Kendine Göre Düzenle) ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"  # Siteyi tamamen gizlemek için ana şifre
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
        st.error(f"Veri Bağlantı Hatası: {e}")

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE (Giriş Durumları) ---
if 'is_site_unlocked' not in st.session_state:
    st.session_state.is_site_unlocked = False # Site kilidi (Halka kapalı mod)
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False # Yönetici modu
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

# --- PREMİUM TASARIM & EFEKTLER (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Montserrat:wght@300;400;600&display=swap');
    
    /* Hareketli Arka Plan */
    .stApp {{
        background: linear-gradient(-45deg, #0f0000, #2b0000, #000000, #1a0000);
        background-size: 400% 400%;
        animation: gradient 12s ease infinite;
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Küçük ve Zarif Başlık */
    .header-compact {{
        text-align: center;
        margin-top: -70px;
        padding-bottom: 20px;
    }}
    .header-compact h2 {{
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        color: #ffcc00;
        letter-spacing: 4px;
        margin: 0;
        text-shadow: 0 0 15px rgba(255, 204, 0, 0.4);
    }}

    /* Premium Kartlar */
    .dukkan-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 204, 0, 0.15);
        transition: 0.4s;
        margin-bottom: 15px;
        text-align: center;
    }}
    .dukkan-card:hover {{
        border: 1px solid #ffcc00;
        transform: translateY(-5px);
        background: rgba(255, 204, 0, 0.05);
    }}

    /* Butonlar */
    .stButton>button {{
        background: linear-gradient(90deg, #ffcc00 0%, #ffaa00 100%) !important;
        color: #000 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
    }}

    /* Sözleşme Kutusu */
    .contract-view {{
        background: rgba(0,0,0,0.3);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        font-size: 0.8rem;
        color: #ccc;
        height: 120px;
        overflow-y: scroll;
        margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK DUVARI (SİTE GİRİŞİ) ---
if not st.session_state.is_site_unlocked:
    _, lock_col, _ = st.columns([1, 2, 1])
    with lock_col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🔒 ÖZEL ERİŞİM</h2>", unsafe_allow_html=True)
        st.write("Bu site şu an hazırlık aşamasındadır. Devam etmek için giriş anahtarını girin.")
        giris_deneme = st.text_input("Site Anahtarı", type="password")
        if st.button("SİTEYİ AÇ"):
            if giris_deneme == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else:
                st.error("Hatalı anahtar!")
    st.stop() # Site açılana kadar alt tarafı yükleme

# --- ANA UYGULAMA İÇERİĞİ ---

# BAŞLIK
st.markdown("""
    <div class="header-compact">
        <h2>DÖRTYOL ÇARŞI</h2>
        <p style='font-size:0.7rem; letter-spacing:2px; color:#aaa;'>PREMIUM DIGITAL ECOSYSTEM</p>
    </div>
    """, unsafe_allow_html=True)

# MERKEZİ PANEL
_, main_col, _ = st.columns([1, 8, 1])

with main_col:
    tabs = st.tabs(["💎 ÇARŞIYI KEŞFET", "🏢 KURUMSAL KAYIT", "🔑 YÖNETİM"])

    # --- 1. KEŞFET SEKMESİ ---
    with tabs[0]:
        if st.session_state.selected_id is None:
            dukkanlar = verileri_yukle()
            
            # Arama ve Filtre
            f1, f2 = st.columns([3, 1])
            with f1:
                search = st.text_input("🔍 Esnaf veya lezzet ara...", placeholder="Örn: Kebap, Künefe, Kuyumcu")
            with f2:
                cat = st.selectbox("Kategori", ["Tümü", "Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Diğer"])

            filtered = [d for d in dukkanlar if (search.lower() in d['ad'].lower() or search.lower() in d['urun'].lower()) and (cat == "Tümü" or d['sektor'] == cat)]
            
            if not filtered:
                st.info("Henüz bu kategoride bir kayıt bulunmuyor. İlk dükkanı siz ekleyin!")
            
            # Listeleme
            g1, g2 = st.columns(2)
            for i, d in enumerate(filtered):
                with (g1 if i % 2 == 0 else g2):
                    st.markdown(f"""
                    <div class="dukkan-card">
                        <small style="color:#ffcc00;">{d['sektor'].upper()}</small>
                        <h4 style="margin:5px 0;">{d['ad']}</h4>
                        <p style="font-size:0.8rem; color:#aaa;">🌟 {d['urun']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"İNCELE: {d['ad']}", key=f"v_{d['id']}"):
                        st.session_state.selected_id = d
                        st.rerun()
        else:
            # DETAY SAYFASI
            d = st.session_state.selected_id
            if st.button("⬅️ ÇARŞI LİSTESİNE DÖN"):
                st.session_state.selected_id = None
                st.rerun()
            
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.4); padding:30px; border-radius:20px; border:1px solid #ffcc00;">
                <h2 style="color:#ffcc00; text-align:center; margin:0;">{d['ad']}</h2>
                <p style="text-align:center; font-size:0.8rem; letter-spacing:2px; color:#888;">KURUMSAL ESNAF PROFİLİ</p>
                <hr style="border-color:#333;">
                <div style="display:flex; justify-content:space-around; text-align:center;">
                    <div><h6 style="color:#ffcc00; margin:0;">BAŞLICA HİZMET</h6><p>{d['urun']}</p></div>
                    <div><h6 style="color:#ffcc00; margin:0;">SEKTÖR</h6><p>{d['sektor']}</p></div>
                </div>
                <p style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; font-style:italic;">{d['icerik']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            wa_link = f"https://wa.me/{d['tel'].replace(' ','').replace('+','')}"
            st.markdown(f"""
                <a href="{wa_link}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:15px; font-weight:bold; cursor:pointer;">
                        🟢 WHATSAPP İLE İLETİŞİME GEÇ
                    </button>
                </a>
            """, unsafe_allow_html=True)

    # --- 2. KAYIT SEKMESİ ---
    with tabs[1]:
        st.markdown("<h4 style='text-align:center; color:#ffcc00;'>YENİ ESNAF KAYIT FORMU</h4>", unsafe_allow_html=True)
        with st.form("premium_register"):
            c1, c2 = st.columns(2)
            with c1:
                n_ad = st.text_input("İşletme Adı*")
                n_tel = st.text_input("WhatsApp İletişim (05xx...)")
            with c2:
                n_sek = st.selectbox("Sektör", ["Tatlıcı", "Kebapçı", "Kuyumcu", "Giyim", "Gıda", "Teknoloji", "Diğer"])
                n_urn = st.text_input("İmza Ürününüz / Hizmetiniz")
            
            n_tanitim = st.text_area("İşletme Tanıtımı ve Hikayesi")
            
            st.markdown("**📜 KURUMSAL HİZMET SÖZLEŞMESİ**")
            st.markdown("""
                <div class="contract-view">
                    1. Dörtyol Dijital Çarşı, esnafın dijitalleşmesini destekleyen bir prestij platformudur.<br>
                    2. Kayıt olan esnaf, paylaştığı bilgilerin doğruluğunu ve kurumsal etik kurallarına uyacağını taahhüt eder.<br>
                    3. Müşteri memnuniyeti ve güvenliği esastır. Hatalı veya yanıltıcı bilgi girişi dükkanın sistemden kaldırılmasına neden olur.<br>
                    4. Platform, esnaf ve müşteri arasındaki ticari ilişkiden sorumlu değildir, sadece bir köprü görevi görür.<br>
                    5. İşbu sözleşme, dijital onay ile yürürlüğe girmiş kabul edilir.
                </div>
            """, unsafe_allow_html=True)
            
            check = st.checkbox("Hizmet sözleşmesini okudum, işletmem adına onaylıyorum.")
            
            if st.form_submit_button("📜 SÖZLEŞMEYİ İMZALA VE KAYDET"):
                if not check:
                    st.warning("Lütfen sözleşmeyi onaylayın.")
                elif not n_ad or not n_tel:
                    st.error("Dükkan adı ve telefon alanları zorunludur.")
                elif db and col_ref:
                    res = col_ref.add({
                        "ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, 
                        "icerik": n_tanitim, "tarih": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.success("Tebrikler! Dörtyol Çarşı ailesine katıldınız.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # --- 3. YÖNETİM SEKMESİ ---
    with tabs[2]:
        if not st.session_state.is_admin:
            st.markdown("<h4 style='text-align:center;'>🔐 YÖNETİCİ GİRİŞİ</h4>", unsafe_allow_html=True)
            admin_pwd = st.text_input("Yönetici Şifresi", type="password")
            if st.button("SİSTEME GİRİŞ YAP"):
                if admin_pwd == ADMIN_SIFRE:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Hatalı yönetici şifresi!")
        else:
            st.success("👑 YÖNETİCİ MODU AKTİF - Merhaba Albayrax")
            if st.button("Çıkış Yap"):
                st.session_state.is_admin = False
                st.rerun()
            
            st.divider()
            yonetim_data = verileri_yukle()
            for item in yonetim_data:
                with st.expander(f"🛠️ {item['ad']} ({item.get('tarih', '-')})"):
                    st.write(f"Tel: {item['tel']}")
                    if st.button(f"DÜKKANI KALDIR: {item['ad']}", key=f"del_{item['id']}"):
                        col_ref.document(item['id']).delete()
                        st.warning("Dükkan sistemden silindi.")
                        st.rerun()

# ALT BİLGİ
st.markdown(f"""
    <div style="text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;">
        © {GUNCEL_YIL} Albayrax Premium Architecture | Dörtyol / Hatay<br>
        v2.0 Beta - 2026 Vision
    </div>
    <div style="height:50px;"></div>
    """, unsafe_allow_html=True)
