import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import uuid

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Çarşı | v43 Powerhouse",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

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
# Public Data: artifacts/dortyol-carsi-v1/public/data/dukkanlar
# Public Reviews: artifacts/dortyol-carsi-v1/public/data/yorumlar

def get_col(col_name):
    return db.collection("artifacts").document(APP_ID).collection("public").document("data").collection(col_name)

# --- SESSION STATE ---
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop_id' not in st.session_state: st.session_state.selected_shop_id = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None

# --- CSS: ULTRA CONTRAST & READABILITY ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    .stApp {{ background-color: #FF8C00; font-family: 'Outfit', sans-serif; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #001F3F !important; font-weight: 700; }}
    .main-title {{ font-size: 3.5rem; text-align: center; margin-top: -80px; text-transform: uppercase; letter-spacing: -2px; }}
    .info-bar {{ background: #001F3F; color: #FF8C00 !important; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px; }}
    .business-card {{ background: white; border-radius: 30px; padding: 25px; margin-bottom: 25px; border: 4px solid #001F3F; box-shadow: 10px 10px 0px #001F3F; }}
    .price-badge {{ background: #001F3F; color: white !important; padding: 8px 15px; border-radius: 12px; font-weight: 900; }}
    .review-box {{ background: #F0F8FF; border-left: 5px solid #001F3F; padding: 15px; margin-top: 10px; border-radius: 10px; }}
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
st.markdown('<div class="info-bar">📢 BUGÜN: Numuneevler Semt Pazarı Kuruldu! | ⛽ Benzin tavan fiyatı: 60.50 ₺</div>', unsafe_allow_html=True)

tabs = st.tabs(["💎 ÇARŞI", "🏥 ACİL/NÖBETÇİ", "📝 DÜKKAN AÇ", "🔐 PANEL", "🔑 ADM"])

# --- TAB 1: ÇARŞI (KEŞFET & YORUMLAR) ---
with tabs[0]:
    col_s1, col_s2 = st.columns([3, 1])
    search_q = col_s1.text_input("", placeholder="🔍 Ürün veya dükkan ara...", key="search_box")
    sort_option = col_s2.selectbox("Sırala", ["En Popüler", "En Yeni", "Puan: Yüksek"])

    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Ulaşım", "Sağlık", "Teknoloji", "Yatırım"]
    cat_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if cat_cols[i].button(c, key=f"cat_{c}"):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    if st.session_state.selected_shop_id is None:
        # Dükkanları Listele
        try:
            shops_ref = get_col("dukkanlar")
            shops = [dict(doc.to_dict(), id=doc.id) for doc in shops_ref.stream()]
            
            filtered = [s for s in shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
            
            for s in filtered:
                with st.container():
                    st.markdown(f'<div class="business-card">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2.5])
                    with c1: st.image(s.get('img', "https://images.unsplash.com/photo-1555066931-4365d14bab8c"), use_container_width=True)
                    with c2:
                        st.markdown(f"### {s.get('ad')}")
                        st.markdown(f"⭐ {s.get('puan', 0)} | 👁️ {s.get('tıklanma', 0)} Görüntülenme")
                        st.write(s.get('icerik', '')[:120] + "...")
                        if st.button(f"Detayları Gör: {s.get('ad')}", key=f"btn_{s['id']}"):
                            st.session_state.selected_shop_id = s['id']
                            shops_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Henüz dükkan kaydı bulunamadı veya bağlantı bekleniyor.")
    else:
        # DÜKKAN DETAY & YORUM SİSTEMİ
        shop_id = st.session_state.selected_shop_id
        shop_doc = get_col("dukkanlar").document(shop_id).get()
        if shop_doc.exists:
            s = shop_doc.to_dict()
            if st.button("⬅️ Çarşıya Dön"): st.session_state.selected_shop_id = None; st.rerun()
            
            st.image(s.get('img',''), use_container_width=True)
            st.title(s['ad'])
            st.markdown(f"📍 **Adres:** {s.get('address','Dörtyol')} | 📞 **İletişim:** {s.get('tel','')}")
            
            # Ürünler
            st.divider()
            st.subheader("📋 Menü / Ürünler")
            for p in s.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:15px; border:2px solid #001F3F; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span><b>{p['ad']}</b><br><small>{p.get('desc','')}</small></span>
                    <span class="price-badge">{p['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)

            # YORUM SİSTEMİ (Firestore RULE 1 & 3)
            st.divider()
            st.subheader("💬 Müşteri Yorumları")
            
            with st.form("yorum_form"):
                y_ad = st.text_input("Adınız")
                y_not = st.text_area("Yorumunuz")
                y_puan = st.slider("Puanınız", 1, 5, 5)
                if st.form_submit_button("Yorumu Gönder"):
                    if y_ad and y_not:
                        get_col("yorumlar").add({
                            "shop_id": shop_id,
                            "isim": y_ad,
                            "yorum": y_not,
                            "puan": y_puan,
                            "tarih": datetime.now()
                        })
                        st.success("Yorumun iletildi!")
                        time.sleep(1); st.rerun()

            # Yorumları Listele (RULE 2: Basit Sorgu)
            try:
                y_docs = get_col("yorumlar").stream()
                for y in y_docs:
                    data = y.to_dict()
                    if data.get('shop_id') == shop_id:
                        st.markdown(f"""
                        <div class="review-box">
                            <b>👤 {data['isim']}</b> (⭐ {data['puan']})<br>
                            <p style="margin:5px 0;">{data['yorum']}</p>
                            <small>{data['tarih'].strftime('%d.%m.%Y %H:%M')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.write("Henüz yorum yapılmamış.")

# --- TAB 2: ACİL & NÖBETÇİ ---
with tabs[1]:
    st.subheader("🏥 Dörtyol Acil Rehber")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="business-card"><h4>💊 Nöbetçi Eczaneler</h4><p>Şifa Eczanesi<br>Numuneevler Mah.<br>📞 0326 712 11 22</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="business-card"><h4>🚖 Taksi Durakları</h4><p>Çarşı Taksi: 712 00 00<br>İstasyon Taksi: 712 99 99</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="business-card"><h4>🚑 Önemli No</h4><p>Dörtyol Devlet Hastanesi:<br>0326 712 50 50</p></div>""", unsafe_allow_html=True)

# --- TAB 3: DÜKKAN AÇ ---
with tabs[2]:
    st.markdown("### 🏛️ Elite Esnaf Başvurusu")
    with st.form("kayit_form"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör*", cats[1:])
        n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_icr = st.text_area("Kısa Tanıtım")
        if st.form_submit_button("Başvuruyu Tamamla"):
            if n_ad and n_pwd:
                get_col("dukkanlar").add({
                    "ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "icerik": n_icr,
                    "puan": 5.0, "tıklanma": 0, "urunler": [], "address": "Dörtyol Merkez", "tel": "",
                    "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"
                })
                st.success("Dükkanın kuruldu! Panel sekmesinden ürünlerini ekleyebilirsin."); st.rerun()

# --- TAB 4: ESNAF PANELİ ---
with tabs[3]:
    if st.session_state.owner_shop_id is None:
        st.subheader("🔐 Dükkan Yönetimi")
        l_ad = st.text_input("Dükkan Adınız")
        l_pwd = st.text_input("Panel Şifreniz", type="password")
        if st.button("Giriş Yap"):
            s_docs = get_col("dukkanlar").stream()
            match = next((doc for doc in s_docs if doc.to_dict().get('ad') == l_ad and doc.to_dict().get('sifre') == l_pwd), None)
            if match:
                st.session_state.owner_shop_id = match.id
                st.rerun()
            else: st.error("Bilgiler Hatalı!")
    else:
        shop_id = st.session_state.owner_shop_id
        s_data = get_col("dukkanlar").document(shop_id).get().to_dict()
        st.success(f"Hoş geldin, {s_data['ad']}")
        
        with st.expander("📝 Ürün/Fiyat Güncelle"):
            u_ad = st.text_input("Ürün İsmi")
            u_fi = st.number_input("Fiyat (₺)", min_value=0.0)
            u_de = st.text_input("Kısa Detay")
            if st.button("Ürünü Listeye Ekle"):
                prods = s_data.get('urunler', [])
                prods.append({"ad": u_ad, "fiyat": u_fi, "desc": u_de})
                get_col("dukkanlar").document(shop_id).update({"urunler": prods})
                st.success("Ürün Yayında!"); time.sleep(1); st.rerun()
        
        if st.button("Çıkış Yap"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- TAB 5: ADMİN ---
with tabs[4]:
    adm_pwd = st.text_input("Admin Şifre", type="password", key="adm_pwd")
    if adm_pwd == ADMIN_SIFRE:
        st.write("### Sistem Yönetimi")
        d_docs = get_col("dukkanlar").stream()
        for d in d_docs:
            d_data = d.to_dict()
            with st.expander(f"⚙️ {d_data['ad']}"):
                st.write(f"Şifre: {d_data['sifre']}")
                if st.button(f"SİL: {d_data['ad']}", key=f"del_{d.id}"):
                    get_col("dukkanlar").document(d.id).delete()
                    st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; opacity:0.6;'>© {GUNCEL_YIL} Albayrax Powerhouse v43 | Dörtyol Dijital Çarşı</div>", unsafe_allow_html=True)
