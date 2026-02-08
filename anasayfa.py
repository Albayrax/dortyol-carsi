import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v46 Bug Fix",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = "" # Çevresel değişkenlerden otomatik çekilir

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
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- SMART AI FUNCTIONS (Gemini Grounding) ---
def get_smart_info(query_type):
    """Google Search destekli anlık bilgi çekme fonksiyonu"""
    system_prompt = "Sen Dörtyol Çarşı asistanısın. Sadece istenen bilgiyi kısa, net ve markdown formatında ver."
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
        for delay in [1, 2, 4]:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Bilgi alınamadı.")
            time.sleep(delay)
        return "API limitine takıldı veya bağlantı sağlanamadı."
    except:
        return "Bağlantı hatası oluştu."

# --- CSS: ULTRA CONTRAST ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    .stApp {{ background-color: #FF8C00; font-family: 'Outfit', sans-serif; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #001F3F !important; font-weight: 700; }}
    .main-title {{ font-size: 3.5rem; text-align: center; margin-top: -80px; text-transform: uppercase; letter-spacing: -2px; }}
    .info-bar {{ background: #001F3F; color: #FF8C00 !important; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px; font-weight: 900; box-shadow: 0 10px 20px rgba(0,31,63,0.2); border: 2px solid white; }}
    .business-card {{ background: white; border-radius: 30px; padding: 25px; margin-bottom: 25px; border: 4px solid #001F3F; box-shadow: 10px 10px 0px #001F3F; }}
    .smart-widget {{ background: #001F3F; color: #FFFFFF !important; padding: 25px; border-radius: 25px; border: 3px solid #FFFFFF; margin-bottom: 15px; }}
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

# --- HEADER & NEWS TICKER ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# Haber Bandı Hata Korumalı (FIX)
try:
    sistem_doc = get_col("sistem_bilgi").document("genel").get()
    haber_metni = "Dörtyol Dijital Çarşı v46 Yayında!"
    if sistem_doc.exists:
        s_data = sistem_doc.to_dict()
        if s_data and "haber" in s_data:
            haber_metni = s_data["haber"]
    st.markdown(f'<div class="info-bar">🚀 {haber_metni}</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="info-bar">📢 Dörtyol Dijital Çarşı Yayında!</div>', unsafe_allow_html=True)

tabs = st.tabs(["💎 ÇARŞI", "🏥 AKILLI REHBER", "📝 DÜKKAN AÇ", "🔐 PANEL", "🔑 ADM"])

# --- TAB 1: ÇARŞI ---
with tabs[0]:
    col_s1, col_s2 = st.columns([3, 1])
    search_q = col_s1.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="search_box_v46")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Yatırım"]
    cat_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if cat_cols[i].button(c, key=f"cat_v46_{c}"):
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
                    if st.button(f"Detayları Gör: {s.get('ad')}", key=f"btn_v46_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        shops_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Veriler yükleniyor...")
    else:
        shop_id = st.session_state.selected_shop_id
        shop_doc = get_col("dukkanlar").document(shop_id).get()
        if shop_doc.exists:
            s = shop_doc.to_dict()
            if st.button("⬅️ Çarşıya Dön"): st.session_state.selected_shop_id = None; st.rerun()
            st.image(s.get('img',''), use_container_width=True)
            st.title(s['ad'])
            for p in s.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:15px; border:2px solid #001F3F; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;"><span><b>{p['ad']}</b></span><span class="price-badge">{p['fiyat']} ₺</span></div>""", unsafe_allow_html=True)

# --- TAB 2: AKILLI REHBER (FIXED) ---
with tabs[1]:
    st.subheader("🤖 Dörtyol Akıllı Bilgi Servisi")
    
    # smart_ref Ataması Düzeltildi (FIX)
    try:
        doc_snap = get_col("sistem_bilgi").document("genel").get()
        smart_ref = doc_snap.to_dict() if doc_snap.exists else {}
    except:
        smart_ref = {}

    if not smart_ref:
        st.info("Bilgiler henüz admin tarafından güncellenmedi. Lütfen 'ADM' sekmesinden AI verilerini çekin.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="smart-widget"><h4>⛽ Güncel Akaryakıt</h4></div>', unsafe_allow_html=True)
        st.markdown(smart_ref.get("fuel_info", "*Henüz veri yok.*") if smart_ref else "*Henüz veri yok.*")
    
    with c2:
        st.markdown('<div class="smart-widget"><h4>💊 Nöbetçi Eczaneler</h4></div>', unsafe_allow_html=True)
        st.markdown(smart_ref.get("pharmacy_info", "*Henüz veri yok.*") if smart_ref else "*Henüz veri yok.*")

# --- TAB 5: ADMİN ---
with tabs[4]:
    adm_pwd = st.text_input("Admin Şifre", type="password", key="adm_v46")
    if adm_pwd == ADMIN_SIFRE:
        st.subheader("⚙️ Akıllı Veri & Haber Yönetimi")
        
        with st.expander("📢 Haber Bandını Değiştir"):
            yeni_haber = st.text_input("Duyuru Metni")
            if st.button("DUYURUYU YAYINLA"):
                get_col("sistem_bilgi").document("genel").set({"haber": yeni_haber}, merge=True)
                st.success("Duyuru yayınlandı!"); time.sleep(1); st.rerun()
        
        st.write("### AI Veri Çekme (Anlık)")
        col_up1, col_up2 = st.columns(2)
        if col_up1.button("🤖 AKARYAKIT VERİSİ ÇEK"):
            with st.spinner("Çekiliyor..."):
                fuel_data = get_smart_info("fuel")
                get_col("sistem_bilgi").document("genel").set({"fuel_info": fuel_data}, merge=True)
                st.success("Güncellendi!"); st.rerun()
        
        if col_up2.button("🚑 NÖBETÇİ LİSTESİ ÇEK"):
            with st.spinner("Taranıyor..."):
                pharmacy_data = get_smart_info("pharmacy")
                get_col("sistem_bilgi").document("genel").set({"pharmacy_info": pharmacy_data}, merge=True)
                st.success("Güncellendi!"); st.rerun()
        
        st.divider()
        st.write("### Dükkan Yönetimi")
        try:
            d_docs = get_col("dukkanlar").stream()
            for d in d_docs:
                d_data = d.to_dict()
                with st.expander(f"{d_data.get('ad','Adsız')}"):
                    if st.button(f"SİL: {d_data.get('ad')}", key=f"del_v46_{d.id}"):
                        get_col("dukkanlar").document(d.id).delete()
                        st.rerun()
        except: pass

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; opacity:0.6;'>© {GUNCEL_YIL} Albayrax Real-Time v46 | Dörtyol Dijital Çarşı</div>", unsafe_allow_html=True)
