import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Marketplace",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFİGÜRASYON ---
ADMIN_SIFRE = "dortyol31"
SITE_GIRIS_SIFRESI = "dortyol2026"
APP_ID = "dortyol-carsi-v1"
GUNCEL_YIL = "2026"

# --- KÜFÜR FİLTRESİ (TEMEL) ---
KOTU_SOZLER = ["küfür1", "küfür2", "argo1", "uygunsuz1"] # Burayı genişletebilirsin

def icerik_temizle(metin):
    for kelime in KOTU_SOZLER:
        metin = re.sub(re.escape(kelime), "***", metin, flags=re.IGNORECASE)
    return metin

# --- FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
    except:
        pass

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop': None,
    'owner_shop_id': None,
    'sort_by': "En Yüksek Puan"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- DÖRTYOL MOCK DATABASE ---
DORTYOL_DATABASE = [
    {
        "ad": "Kadir Teknoloji", 
        "sektor": "Teknoloji", 
        "urun": "Akıllı Telefonlar & Notebook", 
        "tel": "0531 000 00 00",
        "adres": "Dörtyol Çarşı Merkezi, No:1",
        "saatler": "09:00 - 20:00",
        "icerik": "Teknolojinin Dörtyol'daki kalbi. En güncel cihazlar ve teknik servis desteği.",
        "puan": 10.0, "tıklanma": 50, "sifre": "tekno2026",
        "urunler": [
            {"ad": "iPhone 16 Pro", "fiyat": 85000, "eski_fiyat": 90000, "img": "https://images.unsplash.com/photo-1510557880182-3d4d3cba3f21?q=80&w=400", "detay": "256GB, Titanyum.", "tarihce": "Apple'ın en güçlü serisi."}
        ],
        "yorumlar": []
    }
]

# --- FONKSİYONLAR ---
def verileri_yukle():
    data = []
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: pass
    return data if data else DORTYOL_DATABASE

# --- PREMIUM UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920");
        background-size: cover; background-attachment: fixed; color: #ffffff; font-family: 'Montserrat', sans-serif;
    }
    .main-title { font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3rem; text-align: center; margin-top: -100px; letter-spacing: 10px; }
    .business-card { background: rgba(255, 255, 255, 0.04); border-radius: 20px; border-left: 5px solid #ffcc00; padding: 25px; margin-bottom: 15px; }
    .product-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
    .price-old { text-decoration: line-through; color: #888; font-size: 0.9rem; }
    .price-new { color: #00ff00; font-weight: 900; font-size: 1.2rem; }
    .info-tag { background: #222; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; border: 1px solid #ffcc00; margin-right: 5px; }
    code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:25px; border:1px solid #ffcc0033;">', unsafe_allow_html=True)
        pwd_try = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("PORTALA GİRİŞ YAP"):
            if pwd_try == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Anahtar!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
c_s, c_f = st.columns([3, 1])
with c_s: search_q = st.text_input("", placeholder="🔍 Dükkan, ürün veya marka ara...", key="m_search")
with c_f: st.session_state.sort_by = st.selectbox("Sıralama", ["En Yüksek Puan", "En Çok Ziyaret"])

tabs = st.tabs(["💎 ÇARŞIYI GEZ", "🏛️ KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [{"ad": "Tümü", "ikon": "🌐"}, {"ad": "Tatlıcı", "ikon": "🍯"}, {"ad": "Kebapçı", "ikon": "🔥"}, {"ad": "Sağlık", "ikon": "🏥"}, {"ad": "Ulaşım", "ikon": "🚗"}, {"ad": "Hizmet", "ikon": "🛠️"}, {"ad": "Yatırım", "ikon": "💎"}, {"ad": "Teknoloji", "ikon": "💻"}]

# --- 1. KEŞFET ---
with tabs[0]:
    cat_cols = st.columns(len(kategoriler))
    for i, cat in enumerate(kategoriler):
        with cat_cols[i]:
            if st.button(f"{cat['ikon']} {cat['ad']}", key=f"cat_{cat['ad']}"):
                st.session_state.selected_cat = cat['ad']
                st.session_state.selected_shop = None
                st.rerun()
    st.divider()

    if st.session_state.selected_shop is None:
        shops = verileri_yukle()
        filtered = [s for s in shops if (search_q.lower() in s['ad'].lower()) and (st.session_state.selected_cat == "Tümü" or s['sektor'] == st.session_state.selected_cat)]
        for s in filtered:
            st.markdown(f"""<div class="business-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="info-tag">{s['sektor'].upper()}</span>
                    <span style="color:#ffcc00; font-weight:800;">⭐ {s.get('puan', 0)} / 10</span>
                </div>
                <h2 style="color:#ffcc00; font-family:Cinzel; margin:10px 0;">{s['ad']}</h2>
                <p style="color:#ddd; font-size:0.9rem;">{s['icerik']}</p>
                <p style="font-size:0.75rem; color:#666;">📍 {s.get('adres', 'Adres girilmemiş.')} | 👁️ {s.get('tıklanma', 0)} Ziyaret</p>
            </div>""", unsafe_allow_html=True)
            if st.button(f"🏪 {s['ad']} Mağazasına Gir", key=f"v_{s['ad']}"):
                st.session_state.selected_shop = s
                if db and col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        s = st.session_state.selected_shop
        if st.button("⬅️ LİSTEYE GERİ DÖN"): st.session_state.selected_shop = None; st.rerun()
        
        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.8); padding:40px; border-radius:30px; border:2px solid #ffcc00; text-align:center;">
                <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{s['ad']}</h1>
                <p style="font-style:italic; color:#ddd;">"{s['icerik']}"</p>
                <div style="display:flex; justify-content:center; gap:10px; margin-top:15px;">
                    <span class="info-tag">🕒 {s.get('saatler', 'Belirtilmemiş')}</span>
                    <span class="info-tag">📍 {s.get('adres', 'Belirtilmemiş')}</span>
                </div>
            </div>
            <h3 style="color:#ffcc00; margin-top:30px; font-family:Cinzel;">📋 ÜRÜN KATALOĞU</h3>
        """, unsafe_allow_html=True)
        
        # Ürün Listeleme
        for item in s.get('urunler', []):
            p_col1, p_col2 = st.columns([1, 4])
            with p_col1:
                if item.get('img'): st.image(item['img'], use_container_width=True)
                else: st.markdown("🖼️ Görsel Yok")
            with p_col2:
                st.markdown(f"""<div class="product-box">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="color:#ffcc00; margin:0;">{item['ad']}</h4>
                        <div>
                            {f'<span class="price-old">{item["eski_fiyat"]} ₺</span>' if item.get('eski_fiyat') else ''}
                            <span class="price-new">{item['fiyat']} ₺</span>
                        </div>
                    </div>
                    <p style="color:#ccc; font-size:0.9rem; margin-top:5px;">{item['detay']}</p>
                </div>""", unsafe_allow_html=True)
                with st.expander("📜 Detaylı Bilgi & Tarihçe"): st.write(item.get('tarihce', '-'))
        
        # YORUM BÖLÜMÜ
        st.divider()
        st.markdown("### 💬 Müşteri Yorumları")
        for y in s.get('yorumlar', []):
            st.markdown(f"**👤 Misafir:** {y['metin']} <br><small style='color:#666;'>{y['tarih']}</small>", unsafe_allow_html=True)
        
        with st.form("comment_form"):
            y_metin = st.text_area("Yorumunuzu bırakın (Uygunsuz içerikler otomatik gizlenir)")
            if st.form_submit_button("YORUMU GÖNDER"):
                if y_metin:
                    temiz_y = icerik_temizle(y_metin)
                    y_data = {"metin": temiz_y, "tarih": datetime.now().strftime("%d/%m/%Y %H:%M")}
                    current_y = s.get('yorumlar', [])
                    current_y.append(y_data)
                    if db and col_ref and 'id' in s:
                        col_ref.document(s['id']).update({"yorumlar": current_y})
                        st.success("Yorumunuz iletildi!")
                        time.sleep(1); st.rerun()

# --- 2. KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_form_v23"):
        n_ad = st.text_input("Dükkan Adı*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_tel = st.text_input("WhatsApp İletişim*")
        n_pwd = st.text_input("Giriş Şifresi*", type="password")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                col_ref.add({"ad": n_ad, "tel": n_tel, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "yorumlar": [], "icerik": "Yeni Mağaza.", "adres": "", "saatler": ""})
                st.success("Tebrikler! Mağazanız oluşturuldu."); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF PANELİ GİRİŞİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı (Büyük/Küçük harf fark etmez)")
        l_pwd = st.text_input("Şifre", type="password")
        st.info("Test Hesabı: Kadir Teknoloji | Şifre: tekno2026")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            # Büyük küçük harf duyarlılığını kaldırdık
            match = next((s for s in all_s if s['ad'].lower() == l_ad.lower() and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
            else: st.error("Bilgiler hatalı!")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
        
        # PROFİL GÜNCELLEME
        with st.expander("🏠 Dükkan Profilini Güncelle"):
            u_adr = st.text_input("Dükkan Adresi", value=d.get('adres', ''))
            u_saat = st.text_input("Çalışma Saatleri (Örn: 09:00 - 20:00)", value=d.get('saatler', ''))
            u_icr = st.text_area("Kısa Tanıtım Yazısı", value=d.get('icerik', ''))
            if st.button("PROFİLİ KAYDET"):
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"adres": u_adr, "saatler": u_saat, "icerik": u_icr})
                    st.success("Profil güncellendi!"); time.sleep(1); st.rerun()

        # ÜRÜN YÖNETİMİ
        with st.expander("➕ Menüye Yeni Ürün Ekle (Akakçe/Cimri Stili)"):
            u_ad = st.text_input("Ürün Adı")
            u_fiy = st.number_input("Güncel Satış Fiyatı (₺)", min_value=0)
            u_efiy = st.number_input("Eski Fiyat (İndirim Göstermek İçin - İsteğe Bağlı)", min_value=0)
            u_img = st.text_input("Ürün Fotoğraf Linki (URL)")
            u_det = st.text_input("Kısa Özet")
            u_tar = st.text_area("Teknik Bilgiler / Açıklama")
            if st.button("ÜRÜNÜ YAYINLA"):
                prods = d.get('urunler', [])
                prods.append({"ad": u_ad, "fiyat": u_fiy, "eski_fiyat": u_efiy, "img": u_img, "detay": u_det, "tarihce": u_tar})
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Ürün eklendi!"); time.sleep(1); st.rerun()

        if st.button("🚪 PANELİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(f"⚙️ {i['ad']}"):
                    if st.button(f"SİSTEMDEN SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v23.0 Marketplace Edition</div>", unsafe_allow_html=True)
