import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v49 Competition Engine",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = st.secrets.get("gemini_api_key", "")

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Sistem hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

# --- FIREBASE HELPERS (RULE 1) ---
def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- AI FOR PUBLIC DATA (PHARMACIES) ---
def get_ai_public_info(query_type):
    """Kamu verilerini (Eczane, Doktor vb.) internetten çeker"""
    if not apiKey: return "⚠️ API Anahtarı eksik."
    system_prompt = "Sen Dörtyol Çarşı kamu asistanısın. Sadece markdown formatında net bilgi ver."
    user_query = f"Bugün ({datetime.now().strftime('%d.%m.%Y')}) Hatay Dörtyol'daki nöbetçi eczaneleri ve varsa nöbetçi çocuk doktorlarını listele."
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Bilgi bulunamadı.")
        return "Servis şu an meşgul."
    except: return "Bağlantı hatası."

# --- CSS: Hırçın Rekabet Tasarımı ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    .stApp {{ background-color: #FF8C00; font-family: 'Outfit', sans-serif; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #001F3F !important; font-weight: 700; }}
    .main-title {{ font-size: 3.5rem; text-align: center; margin-top: -80px; text-transform: uppercase; letter-spacing: -2px; }}
    .competition-card {{ background: #001F3F; color: #FFFFFF !important; padding: 25px; border-radius: 25px; border: 4px solid white; box-shadow: 0 15px 30px rgba(0,0,0,0.3); margin-bottom: 20px; }}
    .competition-card h4, .competition-card p, .competition-card span {{ color: #FFFFFF !important; }}
    .business-card {{ background: white; border-radius: 25px; padding: 25px; margin-bottom: 20px; border: 4px solid #001F3F; box-shadow: 8px 8px 0px #001F3F; transition: 0.3s; }}
    .business-card:hover {{ transform: scale(1.02); }}
    .price-badge {{ background: #001F3F; color: #FF8C00 !important; padding: 8px 15px; border-radius: 12px; font-weight: 900; font-size: 1.2rem; }}
    .stButton>button {{ background-color: #001F3F !important; color: white !important; border-radius: 12px !important; font-weight: 800; border: none !important; width: 100%; padding: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="****")
        if st.button("SİSTEMİ BAŞLAT"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
    st.stop()

# --- HEADER ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# --- REKABET RADARI (HACIM, BURASI SENİN 5M KAZANACAĞIN YER) ---
all_shops = []
try:
    shops_docs = get_col("dukkanlar").stream()
    all_shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_docs]
except: pass

st.markdown("### 🔥 DÖRTYOL REKABET RADARI")
col_war1, col_war2, col_war3 = st.columns(3)

# En Ucuzları Bul (Dükkan verilerinden)
fuel_list = []
bread_list = []
for s in all_shops:
    for u in s.get('urunler', []):
        u_name = u['ad'].lower()
        if "benzin" in u_name or "95" in u_name: fuel_list.append({"dükkan": s['ad'], "fiyat": u['fiyat']})
        if "ekmek" in u_name: bread_list.append({"dükkan": s['ad'], "fiyat": u['fiyat']})

with col_war1:
    if fuel_list:
        cheapest_fuel = min(fuel_list, key=lambda x: x['fiyat'])
        st.markdown(f"""<div class="competition-card"><h4>⛽ EN UCUZ BENZİN</h4><p>{cheapest_fuel['dükkan']}</p><span>{cheapest_fuel['fiyat']} ₺</span></div>""", unsafe_allow_html=True)
    else: st.markdown("""<div class="competition-card"><h4>⛽ BENZİN SAVAŞI</h4><p>Veri Bekleniyor...</p></div>""", unsafe_allow_html=True)

with col_war2:
    if bread_list:
        cheapest_bread = min(bread_list, key=lambda x: x['fiyat'])
        st.markdown(f"""<div class="competition-card"><h4>🍞 EN UCUZ EKMEK</h4><p>{cheapest_bread['dükkan']}</p><span>{cheapest_bread['fiyat']} ₺</span></div>""", unsafe_allow_html=True)
    else: st.markdown("""<div class="competition-card"><h4>🍞 FIRIN REKABETİ</h4><p>Veri Bekleniyor...</p></div>""", unsafe_allow_html=True)

with col_war3:
    st.markdown("""<div class="competition-card"><h4>🏆 ELİTE ESNAF</h4><p>Antik Kral Künefe</p><span>9.9 Puan</span></div>""", unsafe_allow_html=True)

# --- ANA TABLAR ---
tabs = st.tabs(["💎 ÇARŞI", "🏥 KAMU REHBERİ", "📝 DÜKKAN AÇ", "🔐 PANEL", "🔑 ADM"])

# --- TAB 1: ÇARŞI ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="search_v49")
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Yatırım"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"c_v49_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        for s in filtered:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2.5])
            with col1: st.image(s.get('img', "https://images.unsplash.com/photo-1555066931-4365d14bab8c"), use_container_width=True)
            with col2:
                st.markdown(f"### {s.get('ad')}")
                st.write(s.get('icerik', '')[:120] + "...")
                if st.button(f"Göz At: {s.get('ad')}", key=f"btn_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DETAY SAYFASI
        shop_id = st.session_state.selected_shop_id
        shop_data = next((s for s in all_shops if s['id'] == shop_id), None)
        if st.button("← Geri"): st.session_state.selected_shop_id = None; st.rerun()
        if shop_data:
            st.image(shop_data.get('img',''), use_container_width=True)
            st.title(shop_data['ad'])
            for p in shop_data.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:20px; border-radius:15px; border:2px solid #001F3F; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;"><span style="font-size:1.2rem;"><b>{p['ad']}</b></span><span class="price-badge">{p['fiyat']} ₺</span></div>""", unsafe_allow_html=True)
            st.button(f"💬 WHATSAPP: {shop_data.get('tel','0000')}", use_container_width=True)

# --- TAB 2: KAMU REHBERİ (AI) ---
with tabs[1]:
    st.subheader("🏥 Kamu ve Sağlık Bilgileri")
    try:
        public_ref = get_col("sistem_bilgi").document("kamu").get()
        public_data = public_ref.to_dict() if public_ref.exists else {}
    except: public_data = {}

    if st.button("🤖 YAPAY ZEKADAN GÜNCEL LİSTEYİ İSTE"):
        with st.spinner("AI interneti tarıyor..."):
            res = get_ai_public_info("pharmacy")
            get_col("sistem_bilgi").document("kamu").set({"pharmacy_info": res}, merge=True)
            st.success("Bilgiler internetten çekildi!")
            st.rerun()

    st.markdown(public_data.get("pharmacy_info", "*Henüz veri çekilmedi.*"))

# --- TAB 4: ESNAF PANELİ ---
with tabs[3]:
    if st.session_state.owner_shop_id is None:
        st.subheader("🔐 Esnaf Yönetim Paneli")
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Panel Şifresi", type="password")
        if st.button("DASHBOARD'A GİR"):
            match = next((s for s in all_shops if s.get('ad') == l_ad and s.get('sifre') == l_pwd), None)
            if match:
                st.session_state.owner_shop_id = match['id']
                st.rerun()
            else: st.error("Bilgiler Hatalı!")
    else:
        shop_id = st.session_state.owner_shop_id
        s_data = next((s for s in all_shops if s['id'] == shop_id), None)
        if s_data:
            st.success(f"Dükkan: {s_data['ad']}")
            with st.expander("📝 Fiyat Güncelle & Rekabete Gir"):
                st.warning("Burada fiyatı düşürürseniz ana sayfadaki 'REKABET RADARI'nda en üstte görünürsünüz!")
                u_n = st.text_input("Ürün Adı (Örn: Benzin 95 veya Ekmek)")
                u_p = st.number_input("Satış Fiyatı (₺)", min_value=0.0, step=0.1)
                if st.button("FİYATI YAYINLA"):
                    prods = s_data.get('urunler', [])
                    # Eski ürünü silip yeniyi ekle (güncelleme mantığı)
                    prods = [p for p in prods if p['ad'].lower() != u_n.lower()]
                    prods.append({"ad": u_n, "fiyat": u_p})
                    get_col("dukkanlar").document(shop_id).update({"urunler": prods})
                    st.success("Tebrikler! Rekabette öne geçtiniz."); time.sleep(1); st.rerun()
            
            if st.button("Çıkış Yap"): st.session_state.owner_shop_id = None; st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; opacity:0.5;'>© {GUNCEL_YIL} Albayrax 5M Vision v49 | Dörtyol Rekabet Portalı</div>", unsafe_allow_html=True)
