import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | 2026 Mobil Vizyon",
    page_icon="🍊",
    layout="centered", # Yana yayılmayı önleyen, dikey odaklı yerleşim
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# API Anahtarı Kontrolü
apiKey = st.secrets.get("gemini_api_key", "")

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        pass

db = firestore.client() if firebase_admin._apps else None

# --- YARDIMCI FONKSİYONLAR ---
def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- CSS: DİKEY AKIŞ VE KÜÇÜK KUTU TASARIMI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp {{ 
        background-color: #FDFDFD; 
        font-family: 'Inter', sans-serif; 
    }}

    /* Başlık Tasarımı */
    .main-header {{ 
        text-align: center; 
        margin-top: -50px; 
        margin-bottom: 20px;
    }}
    .main-header h1 {{ 
        font-weight: 900; 
        color: #001F3F; 
        font-size: 2.5rem; 
        letter-spacing: -2px; 
        text-transform: uppercase;
    }}

    /* Rekabet Radarı - Küçük Kare Kutular */
    .radar-container {{
        display: flex;
        gap: 10px;
        overflow-x: auto;
        padding-bottom: 10px;
        scrollbar-width: none; /* Firefox */
    }}
    .radar-container::-webkit-scrollbar {{ display: none; }} /* Chrome/Safari */

    .radar-mini-card {{
        min-width: 130px;
        background: white;
        border: 2px solid #001F3F;
        border-radius: 15px;
        padding: 12px;
        text-align: center;
        box-shadow: 4px 4px 0px #001F3F;
    }}
    .radar-mini-card h6 {{ color: #FF8C00 !important; font-size: 0.6rem !important; margin: 0; text-transform: uppercase; font-weight: 900; }}
    .radar-mini-card p {{ color: #001F3F !important; font-size: 0.75rem !important; margin: 5px 0; font-weight: 700; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
    .radar-mini-card b {{ color: #001F3F !important; font-size: 1rem; font-weight: 900; }}

    /* Dükkan Feed Kartları (Aşağı doğru kayan yapı) */
    .shop-feed-card {{
        background: white;
        border-radius: 20px;
        border: 1px solid #EEE;
        margin-bottom: 20px;
        overflow: hidden;
        transition: 0.3s;
    }}
    .shop-feed-card:hover {{ border-color: #FF8C00; transform: translateY(-3px); }}

    .shop-img-container {{ width: 100%; height: 200px; overflow: hidden; }}
    .shop-img-container img {{ width: 100%; height: 100%; object-fit: cover; }}

    .shop-info {{ padding: 15px; }}
    .shop-info h3 {{ margin: 0; color: #001F3F; font-size: 1.3rem; font-weight: 800; }}
    .shop-info p {{ color: #666; font-size: 0.85rem; margin-top: 5px; line-height: 1.3; }}

    /* Kategori Butonları - Sabit ve Net */
    .stButton>button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.2s !important;
        border: 2px solid #001F3F !important;
    }}

    /* Esnaf Paneli & Kayıt Alanları */
    .form-container {{
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 2px solid #001F3F;
        box-shadow: 8px 8px 0px #001F3F;
    }}
    
    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:100px;"></div><div class="main-header"><h1>DÖRTYOL ÇARŞI</h1></div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 4, 1])
    with col_log:
        st.markdown('<div class="form-container" style="text-align:center;">', unsafe_allow_html=True)
        pwd = st.text_input("Giriş Anahtarı", type="password")
        if st.button("PORTALI AÇ"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- VERİ ÇEKME ---
all_shops = []
try:
    shops_docs = get_col("dukkanlar").stream()
    all_shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_docs]
except: pass

# --- BAŞLIK ---
st.markdown('<div class="main-header"><h1>DÖRTYOL PORTAL</h1></div>', unsafe_allow_html=True)

# --- 🔥 REKABET RADARI (KÜÇÜK KUTULAR) ---
fuel_prices = []
bread_prices = []
for s in all_shops:
    for u in s.get('urunler', []):
        name = u['ad'].lower()
        if "benzin" in name or "95" in name: fuel_prices.append({"dükkan": s['ad'], "fiyat": u['fiyat']})
        if "ekmek" in name: bread_prices.append({"dükkan": s['ad'], "fiyat": u['fiyat']})

# Radar Düzeneği (Küçük yan yana kutular)
st.markdown('<div class="radar-container">', unsafe_allow_html=True)
cols = st.columns(3)

with cols[0]:
    if fuel_prices:
        cheapest = min(fuel_prices, key=lambda x: x['fiyat'])
        st.markdown(f'<div class="radar-mini-card"><h6>⛽ EN UCUZ BENZİN</h6><p>{cheapest["dükkan"]}</p><b>{cheapest["fiyat"]} ₺</b></div>', unsafe_allow_html=True)
    else: st.markdown('<div class="radar-mini-card"><h6>⛽ BENZİN</h6><p>Bekleniyor</p></div>', unsafe_allow_html=True)

with cols[1]:
    if bread_prices:
        cheapest = min(bread_prices, key=lambda x: x['fiyat'])
        st.markdown(f'<div class="radar-mini-card"><h6>🍞 EN UCUZ EKMEK</h6><p>{cheapest["dükkan"]}</p><b>{cheapest["fiyat"]} ₺</b></div>', unsafe_allow_html=True)
    else: st.markdown('<div class="radar-mini-card"><h6>🍞 FIRIN</h6><p>Bekleniyor</p></div>', unsafe_allow_html=True)

with cols[2]:
    st.markdown('<div class="radar-mini-card"><h6>🏆 ELİTE ESNAF</h6><p>Kral Künefe</p><b>9.9 Puan</b></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- ANA SEKMELER ---
tabs = st.tabs(["💎 ÇARŞI", "🏛️ DÜKKAN AÇ", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# --- 1. ÇARŞI (DİKEY FEED) ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="main_search")
    
    # Kategoriler
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Hizmet"]
    st.markdown('<div style="margin-bottom:15px;">', unsafe_allow_html=True)
    c_cols = st.columns(4)
    for i, c in enumerate(cats):
        if c_cols[i % 4].button(c, key=f"cat_{c}", use_container_width=True):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        
        # Dikey Liste (Feed)
        for s in filtered:
            st.markdown(f"""
            <div class="shop-feed-card">
                <div class="shop-img-container"><img src="{s.get('img', 'https://images.unsplash.com/photo-1555066931-4365d14bab8c')}"></div>
                <div class="shop-info">
                    <span style="font-size:0.6rem; font-weight:900; background:#001F3F; color:white; padding:3px 8px; border-radius:10px;">{s.get('sektor','').upper()}</span>
                    <h3>{s.get('ad')}</h3>
                    <p>{s.get('icerik', 'Dörtyol esnafı.')[:100]}...</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Mağazayı Gez: {s.get('ad')}", key=f"view_{s['id']}"):
                st.session_state.selected_shop_id = s['id']
                get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DETAY SAYFASI
        shop_id = st.session_state.selected_shop_id
        s_data = next((s for s in all_shops if s['id'] == shop_id), None)
        if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
        if s_data:
            st.image(s_data.get('img',''), use_container_width=True)
            st.title(s_data['ad'])
            st.write(s_data.get('icerik', ''))
            st.markdown("---")
            for p in s_data.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:15px; border:1px solid #DDD; margin-bottom:8px; display:flex; justify-content:space-between;"><b>{p['ad']}</b><b style="color:#FF8C00;">{p['fiyat']} ₺</b></div>""", unsafe_allow_html=True)

# --- 2. DÜKKAN AÇ (FULL LOGIC) ---
with tabs[1]:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader("🏛️ İşletmeni Kaydet")
    with st.form("kayit_v51"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör*", cats[1:])
        n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_tel = st.text_input("WhatsApp İletişim No*")
        n_icr = st.text_area("Mağaza Tanıtım Yazısı")
        if st.form_submit_button("BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and n_tel:
                get_col("dukkanlar").add({
                    "ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "tel": n_tel, "icerik": n_icr,
                    "puan": 5.0, "tıklanma": 0, "urunler": [], "address": "Dörtyol", "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"
                })
                st.success("Dükkanın açıldı! Şimdi Panelden ürün ekleyebilirsin.")
                time.sleep(1); st.rerun()
            else: st.warning("Yıldızlı alanlar boş bırakılamaz.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ (FULL LOGIC) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("🔐 Esnaf Yönetim Girişi")
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("PANELE GİRİŞ YAP"):
            match = next((s for s in all_shops if s.get('ad') == l_ad and s.get('sifre') == l_pwd), None)
            if match:
                st.session_state.owner_shop_id = match['id']
                st.rerun()
            else: st.error("Bilgiler hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        shop_id = st.session_state.owner_shop_id
        s_data = next((s for s in all_shops if s['id'] == shop_id), None)
        if s_data:
            st.success(f"Hoş geldin, {s_data['ad']}")
            with st.expander("📝 Yeni Ürün/Fiyat Ekle"):
                u_n = st.text_input("Ürün Adı (Örn: Benzin 95, Karışık Izgara)")
                u_p = st.number_input("Fiyat (₺)", min_value=0.0, step=0.1)
                if st.button("FİYATI YAYINLA"):
                    prods = s_data.get('urunler', [])
                    prods = [p for p in prods if p['ad'].lower() != u_n.lower()] # Güncelleme mantığı
                    prods.append({"ad": u_n, "fiyat": u_p})
                    get_col("dukkanlar").document(shop_id).update({"urunler": prods})
                    st.success("Ürün vitrine çıktı!"); time.sleep(1); st.rerun()
            
            if st.button("Çıkış Yap"):
                st.session_state.owner_shop_id = None
                st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    adm_pwd = st.text_input("Admin Şifresi", type="password")
    if adm_pwd == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı.")
        st.write("### ⚙️ Sistem Denetimi")
        for d in all_shops:
            with st.expander(f"📦 {d.get('ad','')} Kaydını Yönet"):
                st.write(f"Şifre: {d.get('sifre')}")
                if st.button(f"SİL: {d['ad']}", key=f"del_adm_{d['id']}"):
                    get_col("dukkanlar").document(d['id']).delete()
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; padding-top:50px; color:#999; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Mobil v51 | Dörtyol Dijital Çarşı</div>", unsafe_allow_html=True)
