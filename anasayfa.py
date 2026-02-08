import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v54 Ecosystem",
    page_icon="🍊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

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

# --- 3. SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- 4. TASARIM (SADE VE KURUMSAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-title { font-weight: 900; color: #1D1D1F; text-align: center; margin-top: -50px; font-size: 2.2rem; }
    .premium-card { background: #FFF8E1; border: 2px solid #FFC107; padding: 20px; border-radius: 15px; margin-bottom: 10px; }
    .standard-card { background: white; border: 1px solid #EEE; padding: 20px; border-radius: 15px; margin-bottom: 10px; }
    .announcement-bar { background: #001F3F; color: #FF8C00 !important; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .badge-job { background: #E3F2FD; color: #1976D2 !important; padding: 4px 8px; border-radius: 5px; font-size: 0.7rem; font-weight: 700; }
    .badge-premium { background: #FFD700; color: #000 !important; padding: 4px 8px; border-radius: 5px; font-size: 0.7rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GİRİŞ KAPISI ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
    pwd = st.text_input("Giriş Kodu", type="password", placeholder="dortyol2026")
    if st.button("Sistemi Başlat"):
        if pwd == SITE_GIRIS_SIFRESI:
            st.session_state.is_site_unlocked = True
            st.rerun()
    st.stop()

# --- 6. ANA EKRAN ---
st.markdown('<h1 class="main-title">DÖRTYOL DİJİTAL ÇARŞI</h1>', unsafe_allow_html=True)
st.markdown('<div class="announcement-bar">📢 DUYURU: Bugün Numuneevler Semt Pazarı Kuruldu!</div>', unsafe_allow_html=True)

tabs = st.tabs(["🏛️ ÇARŞI", "💼 KARİYER (İŞ/CV)", "📰 DUYURULAR", "🔐 ESNAF", "🔑 ADM"])

# --- TAB 0: ÇARŞI ---
with tabs[0]:
    try:
        shops = [dict(doc.to_dict(), id=doc.id) for doc in get_col("dukkanlar").stream()]
        search = st.text_input("🔍 Dükkan/Hizmet Ara", placeholder="Künefe, Lastikçi, Eczane...")
        filtered = [s for s in shops if search.lower() in s.get('ad','').lower()]
        
        if st.session_state.selected_shop_id is None:
            for s in filtered:
                st.markdown(f"""<div class="standard-card"><h3>{s['ad']}</h3><p>{s.get('sektor')} | ⭐ {s.get('puan', 5)}</p></div>""", unsafe_allow_html=True)
                if st.button(f"Mağazayı Gör: {s['ad']}", key=f"v_{s['id']}"):
                    st.session_state.selected_shop_id = s['id']
                    get_col("dukkanlar").document(s['id']).update({"tıklanma": firestore.Increment(1)})
                    st.rerun()
        else:
            sid = st.session_state.selected_shop_id
            shop = next((s for s in shops if s['id'] == sid), None)
            if st.button("⬅️ Çarşıya Dön"): st.session_state.selected_shop_id = None; st.rerun()
            if shop:
                st.title(shop['ad'])
                st.info(f"📍 {shop.get('address', 'Dörtyol')} | 📞 {shop.get('tel',' Belirtilmedi')}")
                st.write(shop.get('icerik', 'Dörtyol esnafı.'))
                st.divider()
                for p in shop.get('urunler', []):
                    st.write(f"✅ {p['ad']} - **{p['fiyat']} ₺**")
    except: st.info("Sistem yükleniyor...")

# --- TAB 1: KARİYER (LinkedIn Modeli) ---
with tabs[1]:
    st.subheader("💼 Dörtyol Kariyer ve İstihdam")
    c_mode = st.radio("", ["İş İlanları", "İş Arayanlar (CV Bankası)"], horizontal=True)
    
    if c_mode == "İş İlanları":
        st.write("Verimlilik odaklı, Dörtyol'un en iyi iş fırsatları.")
        try:
            jobs = [doc.to_dict() for doc in get_col("ilanlar").stream()]
            # Önce Premium İlanları Göster
            for j in sorted(jobs, key=lambda x: x.get('is_premium', False), reverse=True):
                style = "premium-card" if j.get('is_premium') else "standard-card"
                badge = '<span class="badge-premium">⭐ PREMİUM İLAN</span>' if j.get('is_premium') else '<span class="badge-job">STANDART</span>'
                st.markdown(f"""
                <div class="{style}">
                    {badge}
                    <h4 style="margin:5px 0;">{j['baslik']}</h4>
                    <p>🏢 <b>{j['isletme']}</b> | 📍 {j.get('konum', 'Dörtyol')}</p>
                    <p style="font-size:0.85rem; color:#444;">{j.get('detay', '')}</p>
                    <p style="color:#2E7D32; font-weight:bold;">💰 Maaş/Getiri: {j.get('maas', 'Görüşülür')}</p>
                    <small>📞 İletişim: {j['tel']}</small>
                </div>
                """, unsafe_allow_html=True)
        except: st.write("İlanlar yükleniyor...")
        
    else:
        st.info("İş arayanlar buraya 'Dijital Kartlarını' bırakabilir.")
        with st.form("cv_v54"):
            cv_ad = st.text_input("Ad Soyad*")
            cv_is = st.text_input("Uzmanlık / Aradığınız İş* (Örn: Şoför, Akşam Kasiyeri)")
            cv_maas = st.text_input("Beklenen Ücret / Saatlik Beklenti")
            cv_tel = st.text_input("İletişim*")
            if st.form_submit_button("CV'mi Dörtyol Esnafına Sun"):
                if cv_ad and cv_is and cv_tel:
                    get_col("cvler").add({"ad": cv_ad, "is": cv_is, "maas": cv_maas, "tel": cv_tel, "tarih": datetime.now()})
                    st.success("Dijital kartınız oluşturuldu!")

# --- TAB 2: DUYURULAR (Trafik Çeker) ---
with tabs[2]:
    st.subheader("📰 Dörtyol'da Neler Oluyor?")
    try:
        news = [doc.to_dict() for doc in get_col("duyurular").stream()]
        for n in news:
            st.markdown(f"""
            <div class="standard-card" style="border-left: 5px solid #001F3F;">
                <small style="color:gray;">{n['tarih'].strftime('%d.%m.%Y')}</small>
                <h4 style="margin:0;">{n['baslik']}</h4>
                <p style="margin-top:5px;">{n['detay']}</p>
            </div>
            """, unsafe_allow_html=True)
    except: st.write("Güncel duyuru bulunamadı.")

# --- TAB 3: ESNAF PANELİ ---
with tabs[3]:
    if st.session_state.owner_shop_id is None:
        l_ad = st.text_input("Dükkan İsmi")
        l_pwd = st.text_input("Şifre", type="password")
        if st.button("Panele Giriş Yap"):
            s_docs = get_col("dukkanlar").stream()
            match = next((d for d in s_docs if d.to_dict().get('ad') == l_ad and d.to_dict().get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match.id; st.rerun()
    else:
        sid = st.session_state.owner_shop_id
        s_data = get_col("dukkanlar").document(sid).get().to_dict()
        st.success(f"Yönetim: {s_data['ad']}")
        
        with st.expander("💼 İş İlanı Oluştur"):
            j_t = st.text_input("Pozisyon")
            j_m = st.text_input("Tahmini Maaş / Haklar")
            j_d = st.text_area("İş Detayları (Verimlilik/Saatler vb.)")
            if st.button("İlanı Yayınla"):
                get_col("ilanlar").add({"baslik": j_t, "isletme": s_data['ad'], "maas": j_m, "detay": j_d, "tel": s_data.get('tel',''), "is_premium": False})
                st.success("İlan yayında!")
        
        if st.button("Panelden Çık"): st.session_state.owner_shop_id = None; st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:50px; opacity:0.3;'>© {GUNCEL_YIL} Albayrax Ecosystem v54</div>", unsafe_allow_html=True)
