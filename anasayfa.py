import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests
import re

# --- 1. AYARLAR VE SAYFA YAPISI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v57 Master Brain",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"
apiKey = st.secrets.get("gemini_api_key", "")

# --- 2. FIREBASE BAĞLANTISI (HAFIZA BURADA) ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': f"{key_dict.get('project_id')}.firebasestorage.app"})
    except:
        st.error("Firebase anahtarı bulunamadı! Lütfen Secrets ayarlarına ekleyin.")

db = firestore.client() if firebase_admin._apps else None

# Firebase Yol Yardımcısı (Rule 1)
def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- 3. AKILLI ANALİZ (İŞ TİPİ) ---
def analyze_job_type(details_text):
    text = details_text.lower()
    full_time_match = re.search(r'([8-9]|1[0-2])\s*saat', text)
    part_time_match = re.search(r'([1-7])\s*saat', text)
    if full_time_match: return "TAM ZAMANLI"
    if part_time_match or "part" in text or "yarı" in text: return "VERİMLİ / PART-TIME"
    return "TAM ZAMANLI"

# --- 4. SESSION STATE (NAVİGASYON HAFIZASI) ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- 5. TASARIM (HIGH CONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    h1, h2, h3, h4, p, span, label, div { color: #1C1E21 !important; font-family: 'Inter', sans-serif; }
    .main-title { font-weight: 900; color: #001F3F !important; text-align: center; margin-top: -60px; font-size: 2.2rem; }
    .standard-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #DADDE1; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .announcement-bar { background: #1C1E21; color: #FFB300 !important; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; border: 1px solid #FFB300; }
    .badge-full { background: #E7F3FF; color: #1877F2 !important; padding: 4px 8px; border-radius: 5px; font-size: 0.7rem; font-weight: 800; }
    .badge-efficient { background: #E7F3EF; color: #2E7D32 !important; padding: 4px 8px; border-radius: 5px; font-size: 0.7rem; font-weight: 800; }
    .stButton>button { border-radius: 8px !important; font-weight: 600 !important; width: 100%; transition: 0.2s; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL ÇARŞI</h1>', unsafe_allow_html=True)
    pwd = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
    if st.button("PORTALI AKTİF ET"):
        if pwd == SITE_GIRIS_SIFRESI:
            st.session_state.is_site_unlocked = True
            st.rerun()
    st.stop()

# --- 7. ANA İÇERİK ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div class="announcement-bar">🚀 Dörtyol Ekonomisi ve Kariyer Merkezi Yayında!</div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER MERKEZİ", "🔐 ESNAF PANELİ", "🔑 ADMIN"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    if st.session_state.selected_shop_id is None:
        search = st.text_input("🔍 Ne aramıştınız?", placeholder="Künefe, Lastikçi, Eczane, Shell...")
        try:
            shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
            filtered = [s for s in shops if search.lower() in s.get('ad','').lower()]
            
            for s in filtered:
                with st.container():
                    st.markdown(f"""<div class="standard-card">
                        <h3 style="margin:0;">{s['ad']}</h3>
                        <p style="margin:5px 0; color:gray; font-size:0.8rem;">{s.get('sektor')} | ⭐ {s.get('puan', 5.0)}</p>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"İncele: {s['ad']}", key=f"v_{s['id']}"):
                        st.session_state.selected_shop_id = s['id']
                        get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
        except: st.info("Sistem verileri Firebase'den çekiyor...")
    else:
        # DÜKKAN DETAY SAYFASI
        sid = st.session_state.selected_shop_id
        doc = get_col("dukkanlar").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            # Önemli: Geri Dön butonu tarayıcıyı bozmaz
            if st.button("⬅️ Çarşıya Geri Dön"):
                st.session_state.selected_shop_id = None
                st.rerun()
            
            st.image(s.get('img', 'https://images.unsplash.com/photo-1555066931-4365d14bab8c'), use_container_width=True)
            st.title(s['ad'])
            st.info(f"📍 {s.get('address', 'Dörtyol')} | 📞 {s.get('tel','0326')}")
            st.write(s.get('icerik', 'Dörtyol esnafımız tüm kalitesiyle hizmetinizde.'))
            st.divider()
            st.subheader("📋 Ürün ve Fiyat Kataloğu")
            for p in s.get('urunler', []):
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:10px; border:1px solid #EEE; margin-bottom:8px; display:flex; justify-content:space-between;">
                    <b>{p['ad']}</b><b style="color:#2E7D32;">{p['fiyat']} ₺</b></div>""", unsafe_allow_html=True)
            st.button(f"💬 {s['ad']} WhatsApp İletişim")

# --- TAB 1: KARİYER MERKEZİ (ZENGİN CV SİSTEMİ) ---
with tabs[1]:
    st.subheader("💼 Kariyer ve İstihdam")
    c_mode = st.radio("", ["İş İlanları", "CV Bankası"], horizontal=True)
    
    if c_mode == "İş İlanları":
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            for j in sorted(jobs, key=lambda x: x.get('is_premium', False), reverse=True):
                badge = "badge-efficient" if "VERİMLİ" in j.get('tip', '') else "badge-full"
                st.markdown(f"""<div class="standard-card">
                    <span class="{badge}">{j.get('tip', 'TAM ZAMANLI')}</span>
                    <h4 style="margin:8px 0;">{j['baslik']}</h4>
                    <p>🏢 <b>{j['isletme']}</b></p>
                    <p style="font-size:0.85rem; color:#444;">{j.get('detay', '')}</p>
                    <p style="color:#2E7D32; font-weight:bold;">Maaş: {j.get('maas', 'Görüşülür')}</p>
                </div>""", unsafe_allow_html=True)
        except: st.write("Henüz ilan yok.")
        
    else:
        st.info("Nitelikli veya genel iş gücü başvurusu için formu doldurun.")
        with st.form("cv_v57"):
            c1, c2 = st.columns(2)
            cv_ad = c1.text_input("Ad Soyad*")
            cv_gender = c2.selectbox("Cinsiyet", ["Belirtilmedi", "Erkek", "Kadın"])
            cv_is = st.text_input("İstediğiniz Pozisyon (Örn: Paketçi, Tezgahtar, Ayak İşleri)*")
            cv_tecrube = st.selectbox("Tecrübe Durumu", ["Tecrübesiz", "1-3 Yıl", "3-5 Yıl", "5+ Yıl"])
            cv_yazi = st.text_area("Kendinizi Kısaca Tanıtın (Başvuru Durumu)*")
            cv_tel = st.text_input("İletişim Numarası*")
            if st.form_submit_button("CV'Mİ BANKAYA EKLE"):
                if cv_ad and cv_is and cv_tel:
                    get_col("cvler").add({
                        "ad": cv_ad, "cinsiyet": cv_gender, "is": cv_is, 
                        "tecrube": cv_tecrube, "yazi": cv_yazi, "tel": cv_tel, "tarih": datetime.now()
                    })
                    st.success("Başvurunuz esnaflar için görünür hale getirildi!")
        
        # CV Bankasını Listele
        st.divider()
        st.write("🔍 **Kayıtlı İş Arayanlar**")
        try:
            cvs = [doc.to_dict() for doc in get_col("cvler").stream()]
            for c in cvs:
                st.markdown(f"""<div class="standard-card" style="border-left: 5px solid #1877F2;">
                    <b>👤 {c['ad']}</b> ({c['cinsiyet']})<br>
                    <b>Pozisyon:</b> {c['is']} | <b>Tecrübe:</b> {c['tecrube']}<br>
                    <p style="font-size:0.85rem; margin-top:5px; color:#555;"><i>"{c.get('yazi', '')}"</i></p>
                    <small>📞 {c['tel']}</small>
                </div>""", unsafe_allow_html=True)
        except: pass

# --- TAB 2: ESNAF PANELİ (KENDİSİ YÖNETİR) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.subheader("🔐 Esnaf Yönetim Girişi")
        l_ad = st.text_input("Dükkan Adı", placeholder="Kayıtlı isminiz...")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("KONTROL PANELİNE GİR"):
            s_docs = get_col("dukkanlar").stream()
            match = next((d for d in s_docs if d.to_dict().get('ad') == l_ad and d.to_dict().get('sifre') == l_pwd), None)
            if match:
                st.session_state.owner_shop_id = match.id
                st.rerun()
            else: st.error("Dükkan adı veya şifre hatalı!")
    else:
        sid = st.session_state.owner_shop_id
        s_data = get_col("dukkanlar").document(sid).get().to_dict()
        st.success(f"Hoş geldin, {s_data['ad']}")
        
        m_tab1, m_tab2 = st.tabs(["📋 Ürün/Fiyat Yönetimi", "💼 İlan/Kariyer"])
        
        with m_tab1:
            with st.expander("➕ Yeni Ürün Ekle"):
                u_n = st.text_input("Ürün Adı")
                u_p = st.number_input("Fiyat", min_value=0.0)
                if st.button("Fiyatı Yayınla"):
                    prods = s_data.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p})
                    get_col("dukkanlar").document(sid).update({"urunler": prods})
                    st.success("Güncellendi!"); time.sleep(1); st.rerun()
            
            st.write("---")
            st.write("Mevcut Ürünleriniz:")
            for p in s_data.get('urunler', []):
                st.write(f"🏷️ {p['ad']} - {p['fiyat']} ₺")
        
        with m_tab2:
            with st.expander("📝 İş İlanı Aç"):
                j_t = st.text_input("Pozisyon")
                j_d = st.text_area("İş Detayları (Saatler, maaş vb.)")
                if st.button("İlanı Yayınla"):
                    get_col("ilanlar").add({
                        "baslik": j_t, "isletme": s_data['ad'], "detay": j_d,
                        "tip": analyze_job_type(j_d), "tel": s_data.get('tel',''), "is_premium": False
                    })
                    st.success("İlan yayına alındı!")

        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- TAB 3: ADMIN (SENİN GİRİŞİN) ---
with tabs[3]:
    adm_pwd = st.text_input("Admin Şifresi", type="password")
    if adm_pwd == ADMIN_SIFRE:
        st.success("Yönetici Yetkisi Onaylandı.")
        
        # Dükkan Başlatıcı (BOŞSA DOLDUR)
        if st.button("🛠️ ÖRNEK DÜKKANLARI YÜKLE (Shell, Petrol Ofisi vb.)"):
            col = get_col("dukkanlar")
            sample = [
                {"ad": "Shell Dörtyol", "sektor": "Ulaşım", "sifre": "123", "tel": "03261234567", "urunler": [{"ad": "Kurşunsuz 95", "fiyat": 60.50}]},
                {"ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "123", "tel": "05321234567", "urunler": [{"ad": "Kral Hasırı", "fiyat": 240.0}]}
            ]
            for s in sample: col.add(s)
            st.success("Dükkanlar hafızaya yüklendi!")

        st.divider()
        st.write("### 🏪 Kayıtlı Esnaflar ve Şifreleri")
        try:
            d_docs = get_col("dukkanlar").stream()
            for d in d_docs:
                dat = d.to_dict()
                with st.expander(f"{dat.get('ad')}"):
                    st.write(f"Şifre: **{dat.get('sifre')}**")
                    if st.button(f"SİL: {dat.get('ad')}", key=f"del_{d.id}"):
                        get_col("dukkanlar").document(d.id).delete()
                        st.rerun()
        except: pass

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3; font-size:0.8rem;'>© {GUNCEL_YIL} Albayrax Master Brain v57</div>", unsafe_allow_html=True)
