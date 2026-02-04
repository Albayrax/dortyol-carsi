import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite",
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
        # Secrets içinde firebase anahtarı aranıyor
        if "firebase" in st.secrets:
            key_dict = json.loads(st.secrets["firebase"]["key"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        # Hataları sessizce geçiyoruz ki uygulama çökmesin
        pass

db = None
col_ref = None
try:
    db = firestore.client()
    col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar")
except:
    pass

# --- SESSION STATE (DURUM YÖNETİMİ) ---
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
        "icerik": "Dörtyol'un en teknolojik mağazası. Sıfır ve ikinci el güvencesiyle teknoloji kapınızda.",
        "puan": 10.0, "tıklanma": 50, "sifre": "tekno2026",
        "urunler": [
            {"ad": "Dizüstü Bilgisayar", "fiyat": 35000, "detay": "16GB RAM, RTX 4050 Ekran Kartı.", "tarihce": "2026 model yüksek performans serisi."}
        ]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "urun": "Meşhur Kral Hasırı", "tel": "0532 111 00 11",
        "icerik": "Dörtyol'un kalbinde, odun ateşinde pişen taze peynirli künefenin tek adresi.",
        "puan": 9.9, "tıklanma": 950, "sifre": "1234",
        "urunler": [{"ad": "Kral Hasırı", "fiyat": 250, "detay": "Bol fıstıklı.", "tarihce": "Geleneksel reçete."}]
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "urun": "Altın & Değerli Maden", "tel": "0532 333 00 33",
        "icerik": "Dörtyol'da güvenin ve birikimin adresi.",
        "puan": 9.8, "tıklanma": 600, "sifre": "1234",
        "urunler": [{"ad": "Çeyrek Altın", "fiyat": 4500, "detay": "22 Ayar saf altın.", "tarihce": "Yatırım birimi."}]
    }
]

# --- VERİ YÜKLEME FONKSİYONU ---
def verileri_yukle():
    data = []
    if db and col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        except: pass
    
    current_list = data if data else DORTYOL_DATABASE
    if st.session_state.sort_by == "En Yüksek Puan":
        return sorted(current_list, key=lambda x: x.get('puan', 0), reverse=True)
    return sorted(current_list, key=lambda x: x.get('tıklanma', 0), reverse=True)

# --- PREMIUM UI TASARIMI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), 
                    url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920");
        background-size: cover; 
        background-attachment: fixed; 
        color: #ffffff; 
        font-family: 'Montserrat', sans-serif;
    }
    
    .main-title { 
        font-family: 'Cinzel', serif; 
        color: #ffcc00; 
        font-size: 3rem; 
        text-align: center; 
        margin-top: -100px; 
        letter-spacing: 10px; 
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.4); 
    }
    
    .business-card { 
        background: rgba(255, 255, 255, 0.04); 
        border-radius: 20px; 
        border-left: 5px solid #ffcc00; 
        padding: 25px; 
        margin-bottom: 15px; 
        border-top: 1px solid #333; 
    }
    
    .product-box { 
        background: rgba(0,0,0,0.3); 
        padding: 15px; 
        border-radius: 15px; 
        border: 1px solid #333; 
        margin-bottom: 10px; 
    }
    
    /* Gereksiz teknik öğeleri gizle */
    code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SİTE GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.5, 2])
    with col_log:
        st.markdown('<div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:25px; border:1px solid #ffcc0033;">', unsafe_allow_html=True)
        pwd_try = st.text_input("Giriş Anahtarı", type="password", placeholder="dortyol2026")
        if st.button("PORTAL GİRİŞİ YAP"):
            if pwd_try == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: 
                st.error("Hatalı Anahtar!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- ANA PORTAL ARAYÜZÜ ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

c_s, c_f = st.columns([3, 1])
with c_s: 
    search_q = st.text_input("", placeholder="🔍 Dükkan, hizmet veya ürün ara...", key="m_search")
with c_f: 
    st.session_state.sort_by = st.selectbox("Sıralama", ["En Yüksek Puan", "En Çok Ziyaret"])

tabs = st.tabs(["💎 ÇARŞIYI GEZ", "🏛️ KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

# Sektör Tanımlamaları
kategoriler = [
    {"ad": "Tümü", "ikon": "🌐"}, 
    {"ad": "Tatlıcı", "ikon": "🍯"}, 
    {"ad": "Kebapçı", "ikon": "🔥"}, 
    {"ad": "Sağlık", "ikon": "🏥"}, 
    {"ad": "Ulaşım", "ikon": "🚗"}, 
    {"ad": "Hizmet", "ikon": "🛠️"}, 
    {"ad": "Yatırım", "ikon": "💎"}, 
    {"ad": "Teknoloji", "ikon": "💻"}
]

# --- 1. SEKMEYE: KEŞFET ---
with tabs[0]:
    st.markdown("### 🏷️ Sektörler")
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
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.7rem; border:1px solid #444; padding:3px 10px; border-radius:50px;">{s['sektor'].upper()}</span>
                        <span style="color:#ffcc00;">⭐ {s.get('puan', 0)} / 10</span>
                    </div>
                    <h2 style="color:#ffcc00; font-family:Cinzel; margin:10px 0;">{s['ad']}</h2>
                    <p>{s['icerik']}</p>
                    <p style="font-size:0.8rem; color:#666;">👁️ {s.get('tıklanma', 0)} Toplam Ziyaret</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s['ad']} Mağazasını İncele", key=f"v_{s['ad']}"):
                st.session_state.selected_shop = s
                if db and col_ref and 'id' in s: 
                    col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # Dükkan Detay ve Ürün Listesi
        s = st.session_state.selected_shop
        if st.button("⬅️ LİSTEYE GERİ DÖN"): 
            st.session_state.selected_shop = None
            st.rerun()
        
        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:30px; border:2px solid #ffcc00; text-align:center;">
                <h1 style="color:#ffcc00; font-family:Cinzel; margin:0;">{s['ad']}</h1>
                <p style="font-style:italic; font-size:1.2rem; color:#ddd;">"{s['icerik']}"</p>
            </div>
            <h3 style="color:#ffcc00; margin-top:30px;">📋 ÜRÜN VE HİZMET LİSTESİ</h3>
        """, unsafe_allow_html=True)
        
        for item in s.get('urunler', []):
            st.markdown(f"""
                <div class="product-box">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="color:#ffcc00; margin:0;">{item['ad']}</h4>
                        <span style="font-weight:900; font-size:1.2rem;">{item['fiyat']} ₺</span>
                    </div>
                    <p style="color:#ccc; margin-top:5px;">{item['detay']}</p>
                </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📜 {item['ad']} Detaylı Bilgi"): 
                st.write(item.get('tarihce', 'Bu ürün için detaylı bilgi girilmemiş.'))
        
        st.markdown(f"""
            <br><a href="https://wa.me/{s['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; background:#25D366; color:white; border:none; padding:20px; border-radius:20px; font-weight:bold; font-size:1.4rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ / BİLGİ AL
                </button>
            </a>
        """, unsafe_allow_html=True)

# --- 2. SEKMEYE: KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT</h3>", unsafe_allow_html=True)
    with st.form("reg_form_v22_fix"):
        n_ad = st.text_input("Dükkan Adı*")
        n_tel = st.text_input("İletişim WhatsApp*")
        n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
        n_pwd = st.text_input("Giriş Şifresi*", type="password")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                col_ref.add({
                    "ad": n_ad, "tel": n_tel, "sektor": n_sek, "sifre": n_pwd, 
                    "puan": 0, "tıklanma": 0, "urunler": [], "icerik": "Yeni Elite Mağaza."
                })
                st.success("Tebrikler! Mağazanız oluşturuldu."); time.sleep(1); st.rerun()

# --- 3. SEKMEYE: ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF PANELİ GİRİŞİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı")
        l_pwd = st.text_input("Şifre", type="password")
        st.info("Kendi dükkanın için Ad: Kadir Teknoloji, Şifre: tekno2026")
        if st.button("DASHBOARD'A GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: 
                st.session_state.owner_shop_id = match
                st.rerun()
            else: 
                st.error("Giriş bilgileri hatalı!")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
        st.write(f"Elite Puan: **⭐ {d.get('puan', 0)}** | Toplam Ziyaret: **👁️ {d.get('tıklanma', 0)}**")
        
        with st.expander("➕ Yeni Ürün Ekle"):
            u_ad = st.text_input("Ürün Adı")
            u_fiy = st.number_input("Satış Fiyatı (₺)", min_value=0)
            u_det = st.text_input("Kısa Özet")
            u_tar = st.text_area("Teknik Bilgiler / Tarihçe")
            if st.button("ÜRÜNÜ YAYINLA"):
                prods = d.get('urunler', [])
                prods.append({"ad": u_ad, "fiyat": u_fiy, "detay": u_det, "tarihce": u_tar})
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Ürün stoklara eklendi!"); time.sleep(1); st.rerun()
        
        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- 4. SEKMEYE: ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Aktif.")
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(f"⚙️ {i['ad']}"):
                    if st.button(f"SİSTEMDEN SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete()
                        st.rerun()

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v22.0 Fix Edition</div>", unsafe_allow_html=True)
