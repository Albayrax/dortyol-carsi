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
if 'is_site_unlocked' not in st.session_state: st.session_state.is_site_unlocked = False
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "Tümü"
if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None
if 'owner_shop_id' not in st.session_state: st.session_state.owner_shop_id = None
if 'sort_by' not in st.session_state: st.session_state.sort_by = "En Yüksek Puan"

# --- GERÇEKÇİ DÖRTYOL VERİLERİ (MOCK DATA) ---
DORTYOL_DATABASE = [
    {
        "ad": "Antik Kral Künefe", 
        "sektor": "Tatlıcı", 
        "urun": "Meşhur Kral Hasırı", 
        "tel": "0532 111 00 11",
        "icerik": "Dörtyol'un kalbinde, odun ateşinde pişen taze peynirli künefenin tek adresi.",
        "puan": 9.9, "tıklanma": 950,
        "urunler": [
            {"ad": "Kral Hasırı", "fiyat": 250, "detay": "Bol fıstıklı ve özel şerbetli.", "tarihce": "Geleneksel Dörtyol usulüyle 1980'den beri değişmeyen reçete."},
            {"ad": "Peynirli Künefe", "fiyat": 180, "detay": "Günlük taze Hatay peyniri ile.", "tarihce": "Sıcak servis edilen, peyniri uzayan klasik lezzet."}
        ]
    },
    {
        "ad": "Ferah Kebap", 
        "sektor": "Kebapçı", 
        "urun": "Zırh Kıyma Kebap", 
        "tel": "0533 222 00 22",
        "icerik": "El kıyması ve yerli besi etlerle hazırlanan Dörtyol'un köklü kebapçısı.",
        "puan": 9.7, "tıklanma": 720,
        "urunler": [
            {"ad": "Zırh Kıyma", "fiyat": 320, "detay": "Makine değmeden, bıçakla kıyılan et.", "tarihce": "Eski usul kebap kültürünü yaşatan özel teknik."},
            {"ad": "Kuşbaşı Kebap", "siyat": 350, "detay": "Kuzu etinden yumuşacık lezzet.", "tarihce": "Özel terbiyesinde 24 saat bekletilen etler."}
        ]
    },
    {
        "ad": "Aydın Kuyumculuk", 
        "sektor": "Yatırım", 
        "urun": "Altın & Değerli Maden", 
        "tel": "0532 333 00 33",
        "icerik": "Dörtyol'da güvenin ve birikimin adresi. Çeyrek altından pırlantaya geniş seçenekler.",
        "puan": 9.8, "tıklanma": 600,
        "urunler": [
            {"ad": "Çeyrek Altın", "fiyat": 4500, "detay": "22 Ayar, 1.75 gram saf altın.", "tarihce": "Yatırımın en küçük ve en güvenilir birimi."},
            {"ad": "Pırlanta Tektaş", "fiyat": 25000, "detay": "0.30 Karat, F color, sertifikalı.", "tarihce": "Sonsuz sevginin ve zarafetin pırıltılı simgesi."}
        ]
    },
    {
        "ad": "Kadir Usta Oto Servis", 
        "sektor": "Hizmet", 
        "urun": "Motor & Mekanik Bakım", 
        "tel": "0544 444 00 44",
        "icerik": "Dörtyol Sanayi Sitesi'nde profesyonel oto tamir ve periyodik bakım merkezi.",
        "puan": 9.5, "tıklanma": 410,
        "urunler": [
            {"ad": "Periyodik Bakım", "fiyat": 1500, "detay": "Yağ, filtre ve genel kontrol seti.", "tarihce": "Aracınızın ömrünü uzatan yıllık zorunlu kontrol."},
            {"ad": "Motor Revizyon", "fiyat": 12000, "detay": "Komple motor yenileme hizmeti.", "tarihce": "Ustalık isteyen, sıfır ayarında motor performansı."}
        ]
    },
    {
        "ad": "Mavi / LC Waikiki", 
        "sektor": "Giyim", 
        "urun": "Yeni Sezon Giyim", 
        "tel": "0326 712 00 00",
        "icerik": "En trend moda markalarının Dörtyol şubesiyle her bütçeye uygun giyim seçenekleri.",
        "puan": 8.9, "tıklanma": 880,
        "urunler": [
            {"ad": "Premium Mont", "fiyat": 1800, "detay": "Su geçirmez, kaz tüyü dolgulu.", "tarihce": "Kış aylarında tarz ve sıcaklığı birleştiren tasarım."},
            {"ad": "Slim Fit Jean", "fiyat": 850, "detay": "Lycra karışımlı, esnek denim kumaş.", "tarihce": "Günlük kullanımın en konforlu ve şık parçası."}
        ]
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
    
    current_list = data if data else DORTYOL_DATABASE
    
    if st.session_state.sort_by == "En Yüksek Puan":
        return sorted(current_list, key=lambda x: x.get('puan', 0), reverse=True)
    elif st.session_by == "En Çok Ziyaret":
        return sorted(current_list, key=lambda x: x.get('tıklanma', 0), reverse=True)
    return current_list

# --- PREMIUM UI DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:wght@300;400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920");
        background-size: cover; background-attachment: fixed;
        color: #ffffff; font-family: 'Montserrat', sans-serif;
    }

    .main-title {
        font-family: 'Cinzel', serif; color: #ffcc00; font-size: 3.5rem;
        letter-spacing: 15px; text-align: center; margin-top: -100px;
    }

    /* Kurumsal Kart Tasarımı */
    .business-card {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        border-left: 5px solid #ffcc00;
        padding: 25px;
        margin-bottom: 15px;
        transition: 0.4s;
        border-top: 1px solid #222;
    }
    .business-card:hover { background: rgba(255, 255, 255, 0.08); transform: scale(1.01); }

    /* Ürün/Menü Listesi */
    .product-row {
        background: rgba(0,0,0,0.3);
        padding: 15px; border-radius: 12px;
        border: 1px solid #333; margin-bottom: 10px;
    }

    /* Gereksiz teknik detayları gizle */
    code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ffcc00; font-style:italic;">Prestijli Esnaf Portalı - 2026</p>', unsafe_allow_html=True)
    
    _, log_col, _ = st.columns([2, 1, 2])
    with log_col:
        st.markdown('<div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:25px; border:1px solid #ffcc0033;">', unsafe_allow_html=True)
        pwd_try = st.text_input("Giriş Anahtarı", type="password", placeholder="••••••")
        if st.button("SİSTEMİ BAŞLAT"):
            if pwd_try == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Anahtar!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- ANA PORTAL ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)

# ARAMA VE SIRALAMA
c_s, c_f = st.columns([3, 1])
with c_s: search_q = st.text_input("", placeholder="🔍 Aradığınız her şey... (Örn: Künefe, Altın, Tamir)", key="main_search")
with c_f: st.session_state.sort_by = st.selectbox("Sıralama", ["En Yüksek Puan", "En Çok Ziyaret"])

# SEKMELER
tabs = st.tabs(["💎 ÇARŞIYI GEZ", "🏛️ KURUMSAL KAYIT", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

kategoriler = [
    {"ad": "Tümü", "ikon": "🌐"}, {"ad": "Tatlıcı", "ikon": "🍯"},
    {"ad": "Kebapçı", "ikon": "🔥"}, {"ad": "Sağlık", "ikon": "🏥"},
    {"ad": "Ulaşım", "ikon": "🚗"}, {"ad": "Hizmet", "ikon": "🛠️"},
    {"ad": "Yatırım", "ikon": "💎"}, {"ad": "Giyim", "ikon": "👕"}
]

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    # Kategori Seçimi
    st.markdown("### 🏷️ Sektöre Göre Filtrele")
    cat_cols = st.columns(len(kategoriler))
    for i, cat in enumerate(kategoriler):
        with cat_cols[i]:
            if st.button(f"{cat['ikon']} {cat['ad']}", key=f"cat_{cat['ad']}"):
                st.session_state.selected_cat = cat['ad']
                st.session_state.selected_shop = None
                st.rerun()

    st.divider()

    if st.session_state.selected_shop is None:
        # DÜKKAN LİSTESİ
        shops = verileri_yukle()
        filtered = [s for s in shops if (search_q.lower() in s['ad'].lower() or search_q.lower() in s['urun'].lower()) and (st.session_state.selected_cat == "Tümü" or s['sektor'] == st.session_state.selected_cat)]
        
        for s in filtered:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.8rem; border:1px solid #444; padding:3px 10px; border-radius:50px;">{s['sektor'].upper()}</span>
                        <span style="color:#ffcc00; font-weight:900;">⭐ {s.get('puan', 0)} / 10</span>
                    </div>
                    <h2 style="margin:10px 0; color:white; font-family:'Cinzel', serif;">{s['ad']}</h2>
                    <p style="color:#bbb; font-size:1rem;">{s['icerik']}</p>
                    <p style="color:#666; font-size:0.8rem;">İmza Ürün: <b>{s['urun']}</b> | 👁️ {s.get('tıklanma', 0)} Ziyaret</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s['ad']} Mağazasını ve Menüsünü Gör", key=f"view_{s['ad']}"):
                st.session_state.selected_shop = s
                if db and col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DÜKKAN PROFİLİ & ÜRÜNLER/MENÜ
        s = st.session_state.selected_shop
        if st.button("⬅️ ÇARŞI LİSTESİNE DÖN"):
            st.session_state.selected_shop = None
            st.rerun()
        
        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:30px; border:2px solid #ffcc00; text-align:center;">
                <h1 style="color:#ffcc00; font-family:'Cinzel', serif; font-size:3.5rem; margin:0;">{s['ad']}</h1>
                <p style="font-size:1.2rem; color:#888;">Dörtyol Esnafı Elite Profili</p>
                <hr style="border-color:#333;">
                <p style="font-size:1.3rem; line-height:1.6; max-width:800px; margin:0 auto; font-style:italic;">"{s['icerik']}"</p>
            </div>
            <h3 style="color:#ffcc00; margin-top:40px;">📋 Ürünler ve Hizmetler</h3>
        """, unsafe_allow_html=True)
        
        # Ürünlerin Listelenmesi
        for item in s.get('urunler', []):
            with st.container():
                st.markdown(f"""
                    <div class="product-row">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#ffcc00;">{item['ad']}</h4>
                            <span style="font-weight:900; color:white; font-size:1.2rem;">{item['fiyat']} ₺</span>
                        </div>
                        <p style="color:#ddd; margin:5px 0;">{item['detay']}</p>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander(f"📜 {item['ad']} Hakkında Bilgi & Tarihçe"):
                    st.write(item['tarihce'])
        
        st.markdown(f"""
            <br><a href="https://wa.me/{s['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; background:#25D366; color:white; border:none; padding:20px; border-radius:15px; font-weight:bold; font-size:1.3rem; cursor:pointer;">
                    🟢 WHATSAPP İLE SİPARİŞ VER / BİLGİ AL
                </button>
            </a>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT BAŞVURUSU</h3>", unsafe_allow_html=True)
    with st.form("reg_pro_v19"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("WhatsApp İletişim*")
        with c2:
            n_sek = st.selectbox("Sektör", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Panel Şifreniz*", type="password")
        n_urn = st.text_input("İmza Ürün/Hizmet")
        n_tanitim = st.text_area("İşletme Tanıtımı (Dükkanınızı nasıl anlatırsınız?)")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": []}
                col_ref.add(data)
                st.success("Tebrikler! Dükkanınız kaydedildi. Artık ürünlerinizi ekleyebilirsiniz."); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ (CMS) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİM</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Kayıtlı Dükkan Adı")
        l_pwd = st.text_input("Şifreniz", type="password")
        if st.button("YÖNETİM PANELİNE GİR"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
            else: st.error("Giriş bilgileri hatalı.")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
        
        # ÜRÜN EKLEME FORMU
        with st.expander("➕ Yeni Ürün/Hizmet Ekle"):
            u_ad = st.text_input("Ürün Adı")
            u_fiy = st.number_input("Fiyat (₺)", min_value=0)
            u_det = st.text_input("Kısa Açıklama")
            u_tar = st.text_area("Ürün Tarihçesi / Teknik Bilgi")
            if st.button("ÜRÜNÜ YAYINLA"):
                current_products = d.get('urunler', [])
                current_products.append({"ad": u_ad, "fiyat": u_fiy, "detay": u_det, "tarihce": u_tar})
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"urunler": current_products})
                    st.success("Ürün eklendi!"); time.sleep(1); st.rerun()

        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Sistem Yönetici Şifresi", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Elite Yönetici Onaylı.")
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(f"⚙️ {i['ad']}"):
                    if st.button(f"SİSTEMDEN SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.7rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v19.0 Professional CMS</div>", unsafe_allow_html=True)
