import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v44 Smart Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = "" # Otomatik tanımlanacak

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")

db = firestore.client() if firebase_admin._apps else None

# --- FIREBASE PATHS (RULE 1) ---
def get_col(col_name):
    # Public Data: artifacts/dortyol-carsi-v1/public/data/{collection}
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- SMART AI FUNCTIONS (Gemini Grounding) ---
def get_smart_info(query_type):
    """Google Search destekli akıllı bilgi çekme fonksiyonu"""
    system_prompt = "Sen Dörtyol Çarşı asistanısın. Sadece istenen bilgiyi kısa ve net ver."
    user_query = ""
    
    if query_type == "fuel":
        user_query = "Bugün Hatay Dörtyol ilçesindeki güncel Benzin (95 Oktan), Motorin ve LPG litre fiyatlarını liste halinde ver."
    elif query_type == "pharmacy":
        user_query = f"Bugün ({datetime.now().strftime('%d %B %Y')}) Hatay Dörtyol ilçesindeki nöbetçi eczanelerin isim, adres ve telefonlarını ver."

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}]
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Bilgi alınamadı.")
    except:
        return "Bağlantı hatası oluştu."

# --- CSS: ULTRA CONTRAST ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    .stApp {{ background-color: #FF8C00; font-family: 'Outfit', sans-serif; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #001F3F !important; font-weight: 700; }}
    .main-title {{ font-size: 3.5rem; text-align: center; margin-top: -80px; text-transform: uppercase; letter-spacing: -2px; }}
    .info-bar {{ background: #001F3F; color: #FF8C00 !important; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px; font-weight: 900; }}
    .business-card {{ background: white; border-radius: 30px; padding: 25px; margin-bottom: 25px; border: 4px solid #001F3F; box-shadow: 10px 10px 0px #001F3F; }}
    .smart-widget {{ background: #001F3F; color: #FFFFFF !important; padding: 20px; border-radius: 20px; border: 3px solid #FFFFFF; margin-bottom: 15px; }}
    .price-badge {{ background: #001F3F; color: white !important; padding: 8px 15px; border-radius: 12px; font-weight: 900; }}
    .stButton>button {{ background-color: #001F3F !important; color: white !important; border-radius: 15px !important; font-weight: 800 !important; padding: 12px 20px !important; width: 100%; border: none !important; }}
    input, textarea, select {{ border: 3px solid #001F3F !important; border-radius: 12px !important; font-weight: 700 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="****")
        if st.button("SİSTEME GİR"):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı!")
    st.stop()

# --- HEADER & SMART INFO BAR ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# Firestore'dan sistem bilgisini çek (RULE 2: Basit sorgu)
try:
    sistem_doc = get_col("sistem_bilgi").document("genel").get()
    if sistem_doc.exists:
        s_data = sistem_doc.to_dict()
        st.markdown(f'<div class="info-bar">🚀 {s_data.get("haber", "Dörtyol Dijital Çarşı Yayında!")}</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="info-bar">📢 Dörtyol Dijital Çarşı v44 Smart Hub Yayında!</div>', unsafe_allow_html=True)

tabs = st.tabs(["💎 ÇARŞI", "🏥 AKILLI REHBER", "📝 DÜKKAN AÇ", "🔐 PANEL", "🔑 ADM"])

# --- TAB 1: ÇARŞI ---
with tabs[0]:
    col_s1, col_s2 = st.columns([3, 1])
    search_q = col_s1.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="search_box")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Yatırım"]
    cat_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if cat_cols[i].button(c, key=f"cat_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    if st.session_state.selected_shop_id is None:
        try:
            shops_ref = get_col("dukkanlar")
            shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_ref.stream()]
            filtered = [s for s in shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
            
            for s in filtered:
                st.markdown(f'<div class="business-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2.5])
                with c1: st.image(s.get('img', "https://images.unsplash.com/photo-1555066931-4365d14bab8c"), use_container_width=True)
                with c2:
                    st.markdown(f"### {s.get('ad')}")
                    st.write(s.get('icerik', '')[:120] + "...")
                    if st.button(f"Detayları Gör: {s.get('ad')}", key=f"btn_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        shops_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Mağazalar yükleniyor...")
    else:
        # DETAY SAYFASI
        shop_id = st.session_state.selected_shop_id
        shop_doc = get_col("dukkanlar").document(shop_id).get()
        if shop_doc.exists:
            s = shop_doc.to_dict()
            if st.button("⬅️ Çarşıya Dön"): st.session_state.selected_shop_id = None; st.rerun()
            st.image(s.get('img',''), use_container_width=True)
            st.title(s['ad'])
            
            st.subheader("📋 Ürün Listesi")
            for p in s.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:15px; border:2px solid #001F3F; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span><b>{p['ad']}</b></span>
                    <span class="price-badge">{p['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Yorumlar Bölümü
            st.divider()
            st.subheader("💬 Yorumlar")
            with st.form("y_form"):
                y_ad = st.text_input("Adınız")
                y_not = st.text_area("Yorumunuz")
                if st.form_submit_button("Gönder"):
                    if y_ad and y_not:
                        get_col("yorumlar").add({"shop_id": shop_id, "isim": y_ad, "yorum": y_not, "tarih": datetime.now()})
                        st.success("Yorum iletildi!"); time.sleep(1); st.rerun()
            
            # Yorumları Göster
            y_docs = get_col("yorumlar").stream()
            for y in y_docs:
                d = y.to_dict()
                if d.get('shop_id') == shop_id:
                    st.markdown(f"<div style='background:#F0F8FF; padding:10px; border-radius:10px; margin-top:5px;'><b>{d['isim']}:</b> {d['yorum']}</div>", unsafe_allow_html=True)

# --- TAB 2: AKILLI REHBER (AI INTEGRATION) ---
with tabs[1]:
    st.subheader("🤖 Dörtyol Akıllı Bilgi Servisi")
    st.write("Bu bilgiler internetten anlık olarak yapay zeka tarafından çekilmektedir.")
    
    c1, c2 = st.columns(2)
    
    # Bilgileri Firestore'dan çek
    try:
        smart_ref = get_col("sistem_bilgi").document("genel").get().to_dict()
    except:
        smart_ref = {}

    with c1:
        st.markdown('<div class="smart-widget"><h4>⛽ Akaryakıt Fiyatları</h4></div>', unsafe_allow_html=True)
        st.write(smart_ref.get("fuel_info", "Henüz güncellenmedi."))
    
    with c2:
        st.markdown('<div class="smart-widget"><h4>💊 Nöbetçi Eczaneler</h4></div>', unsafe_allow_html=True)
        st.write(smart_ref.get("pharmacy_info", "Henüz güncellenmedi."))

# --- TAB 5: ADMİN (SMART UPDATE) ---
with tabs[4]:
    adm_pwd = st.text_input("Admin Şifre", type="password")
    if adm_pwd == ADMIN_SIFRE:
        st.subheader("⚙️ Sistem Yönetimi & AI Güncelleme")
        
        col_up1, col_up2 = st.columns(2)
        
        if col_up1.button("🤖 AKARYAKIT FİYATLARINI GÜNCELLE"):
            with st.spinner("Yapay zeka verileri çekiyor..."):
                fuel_data = get_smart_info("fuel")
                get_col("sistem_bilgi").document("genel").set({"fuel_info": fuel_data}, merge=True)
                st.success("Fiyatlar Güncellendi!")
        
        if col_up2.button("🚑 NÖBETÇİ ECZANELERİ GÜNCELLE"):
            with st.spinner("Nöbetçi listesi çekiliyor..."):
                pharmacy_data = get_smart_info("pharmacy")
                get_col("sistem_bilgi").document("genel").set({"pharmacy_info": pharmacy_data}, merge=True)
                st.success("Eczane Listesi Güncellendi!")
        
        st.divider()
        st.write("### Dükkan Yönetimi")
        d_docs = get_col("dukkanlar").stream()
        for d in d_docs:
            d_data = d.to_dict()
            with st.expander(f"{d_data['ad']}"):
                st.write(f"Şifre: {d_data.get('sifre')}")
                if st.button(f"Sil: {d_data['ad']}", key=f"del_{d.id}"):
                    get_col("dukkanlar").document(d.id).delete()
                    st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; opacity:0.6;'>© {GUNCEL_YIL} Albayrax Smart Hub v44 | Dörtyol'un En Akıllı Çarşısı</div>", unsafe_allow_html=True)
