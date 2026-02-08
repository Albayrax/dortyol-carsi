import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import re

# --- 1. AYARLAR VE SAYFA YAPISI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v56 Pro Logic",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = st.secrets.get("gemini_api_key", "")

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

# --- 3. DÜZELTİLMİŞ AKILLI ANALİZ MOTORU (SMART TAGGING) ---
def analyze_job_type(details_text):
    """Metni analiz edip iş tipini HATASIZ belirler"""
    text = details_text.lower()
    
    # 1. Tam Zamanlı Kriterleri (8-12 saat arası tam zamanlıdır)
    full_time_match = re.search(r'([8-9]|1[0-2])\s*saat', text)
    full_time_keywords = ["tam zamanlı", "vardiyalı", "full time", "sigortalı", "daimi"]
    
    # 2. Part-Time Kriterleri (1-7 saat arası veya ek iş ifadeleri)
    part_time_match = re.search(r'([1-7])\s*saat', text)
    part_time_keywords = ["part time", "yarı zamanlı", "ek iş", "öğrenci", "haftalık", "günlük"]

    if full_time_match or any(word in text for word in full_time_keywords):
        return "TAM ZAMANLI"
    elif part_time_match or any(word in text for word in part_time_keywords):
        return "VERİMLİ / PART-TIME"
    
    return "TAM ZAMANLI" # Varsayılan olarak tam zamanlı kabul et (Güvenli liman)

# --- 4. SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- 5. TASARIM (YÜKSEK OKUNABİLİRLİK VE KONTRAST) ---
st.markdown("""
    <style>
    /* Arka planı bembeyaz yerine gözü dinlendiren profesyonel bir tona çektik */
    .stApp { background-color: #F0F2F5; }
    
    /* Yazılar her zaman koyu lacivert (Maksimum Okunabilirlik) */
    h1, h2, h3, h4, p, span, label, div { color: #1C1E21 !important; }
    
    .main-title { font-weight: 900; color: #001F3F !important; text-align: center; margin-top: -50px; font-size: 2.5rem; }
    
    /* Kartlar beyaz, kenarlar net */
    .standard-card { 
        background: white; 
        padding: 25px; 
        border-radius: 18px; 
        border: 1px solid #DADDE1; 
        margin-bottom: 15px; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); 
    }
    
    /* Rozetler için net renkler */
    .badge-full { background: #E7F3FF; color: #1877F2 !important; padding: 5px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; border: 1px solid #1877F2; }
    .badge-efficient { background: #E7F3EF; color: #2E7D32 !important; padding: 5px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; border: 1px solid #2E7D32; }
    
    .announcement-bar { 
        background: #1C1E21; 
        color: #FFB300 !important; 
        padding: 12px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 25px; 
        font-weight: bold; 
        border: 2px solid #FFB300;
    }
    
    /* Buton Tasarımı */
    .stButton>button { 
        background-color: #1877F2 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        font-weight: 700 !important; 
        border: none !important;
        padding: 10px 20px !important;
    }
    .stButton>button:hover { background-color: #166FE5 !important; }
    
    /* Giriş Kutuları */
    input, textarea, select {
        border: 2px solid #DADDE1 !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. GİRİŞ KAPISI ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL ÇARŞI</h1>', unsafe_allow_html=True)
    pwd = st.text_input("Giriş Kodu", type="password", placeholder="dortyol2026")
    if st.button("Sisteme Gir"):
        if pwd == SITE_GIRIS_SIFRESI:
            st.session_state.is_site_unlocked = True
            st.rerun()
    st.stop()

# --- 7. ANA İÇERİK ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div class="announcement-bar">🚀 2026 Hedefi: Dörtyol Ekonomisi Burada Atıyor!</div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER MERKEZİ", "🔐 ESNAF PANELİ", "🔑 ADM"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    try:
        shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
        search = st.text_input("🔍 Mağaza/Esnaf Ara", placeholder="Ne lazımdı?")
        filtered = [s for s in shops if search.lower() in s.get('ad','').lower()]
        
        if st.session_state.selected_shop_id is None:
            for s in filtered:
                with st.container():
                    st.markdown(f"""
                    <div class="standard-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0;">{s['ad']}</h3>
                            <span style="font-weight:900; color:#1877F2;">⭐ {s.get('puan', 5.0)}</span>
                        </div>
                        <p style="margin-top:10px; color:#606770;">{s.get('sektor')} | 👁️ {s.get('tıklanma', 0)} Görüntülenme</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"İncele: {s['ad']}", key=f"v_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
        else:
            sid = st.session_state.selected_shop_id
            shop = next((s for s in shops if s['id'] == sid), None)
            if st.button("⬅️ Geri Dön"): st.session_state.selected_shop_id = None; st.rerun()
            if shop:
                st.markdown(f"## {shop['ad']}")
                st.info(f"📍 {shop.get('address', 'Dörtyol')} | 📞 {shop.get('tel',' Belirtilmedi')}")
                st.write(shop.get('icerik', 'Açıklama mevcut değil.'))
                st.divider()
                st.write("### 📋 Ürün ve Fiyat Kataloğu")
                for p in shop.get('urunler', []):
                    st.markdown(f"""
                    <div style="background:white; padding:15px; border-radius:12px; border:1px solid #EEE; margin-bottom:10px; display:flex; justify-content:space-between;">
                        <b>{p['ad']}</b>
                        <b style="color:#2E7D32;">{p['fiyat']} ₺</b>
                    </div>
                    """, unsafe_allow_html=True)
    except: st.info("Veriler yükleniyor...")

# --- TAB 1: KARİYER MERKEZİ ---
with tabs[1]:
    st.subheader("💼 Kariyer ve İş Gücü")
    c_mode = st.radio("", ["Güncel İlanlar", "CV Bankası"], horizontal=True)
    
    if c_mode == "Güncel İlanlar":
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            if not jobs: st.write("Henüz ilan yok.")
            
            for j in sorted(jobs, key=lambda x: x.get('is_premium', False), reverse=True):
                # AKILLI ETİKETLEME BURADA GÖRÜNÜR
                job_type = j.get('tip', 'TAM ZAMANLI')
                badge_class = "badge-efficient" if "VERİMLİ" in job_type else "badge-full"
                
                st.markdown(f"""
                <div class="standard-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="{badge_class}">{job_type}</span>
                        {'<span style="color:#FFB300; font-weight:900;">⭐ PREMİUM</span>' if j.get('is_premium') else ''}
                    </div>
                    <h4 style="margin:10px 0;">{j['baslik']}</h4>
                    <p style="margin:0; font-weight:700;">🏢 {j['isletme']}</p>
                    <p style="margin-top:10px; color:#606770; font-size:0.9rem;">{j.get('detay', '')}</p>
                    <p style="color:#2E7D32; font-weight:bold; margin-top:10px;">💰 Maaş: {j.get('maas', 'Görüşülür')}</p>
                    <small style="color:gray;">📞 İletişim: {j['tel']}</small>
                </div>
                """, unsafe_allow_html=True)
        except: st.write("İlanlar yükleniyor...")
    else:
        st.info("Kendi yeteneklerinizi Dörtyol esnafına sunun.")
        with st.form("cv_v56"):
            cv_ad = st.text_input("Ad Soyad")
            cv_is = st.text_input("Uzmanlık / İstediğiniz Pozisyon")
            cv_tel = st.text_input("İletişim")
            if st.form_submit_button("CV'mi Gönder"):
                get_col("cvler").add({"ad": cv_ad, "is": cv_is, "tel": cv_tel, "tarih": datetime.now()})
                st.success("Kaydınız başarıyla yapıldı!")

# --- TAB 2: ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.subheader("🔐 Mağaza Yönetim Girişi")
        l_ad = st.text_input("Kayıtlı Mağaza Adı")
        l_pwd = st.text_input("Panel Şifresi", type="password")
        if st.button("Yönetime Gir"):
            s_docs = get_col("dukkanlar").stream()
            match = next((d for d in s_docs if d.to_dict().get('ad') == l_ad and d.to_dict().get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.id; st.rerun()
            else: st.error("Hatalı giriş bilgileri!")
    else:
        sid = st.session_state.owner_shop_id
        s_data = get_col("dukkanlar").document(sid).get().to_dict()
        st.success(f"Hoş geldin, {s_data['ad']}")
        
        with st.expander("💼 Akıllı İş İlanı Aç"):
            st.warning("8 saat ve üzeri mesai 'TAM ZAMANLI' olarak otomatik etiketlenir.")
            j_t = st.text_input("Pozisyon (Örn: Mutfak Şefi)")
            j_d = st.text_area("İş Detayları (Örn: Günde 9 saat, hafta sonu tatil)")
            j_m = st.text_input("Tahmini Maaş")
            
            if st.button("İlanı Yayınla"):
                # AKILLI ANALİZ BURADA DEVREYE GİRİYOR
                detected_type = analyze_job_type(j_d + " " + j_t)
                
                get_col("ilanlar").add({
                    "baslik": j_t, "isletme": s_data['ad'], "maas": j_m, 
                    "detay": j_d, "tel": s_data.get('tel',''), 
                    "tip": detected_type, "is_premium": False
                })
                st.success(f"İlanınız '{detected_type}' olarak sistem tarafından tanımlandı ve yayınlandı!")
        
        if st.button("Güvenli Çıkış"): st.session_state.owner_shop_id = None; st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.4; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Pro Logic v56 | Dörtyol Dijital Portal</div>", unsafe_allow_html=True)
