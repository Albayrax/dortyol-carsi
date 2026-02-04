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

# --- GERÇEKÇİ DÖRTYOL VERİLERİ (MOCK DATA - HATALAR DÜZELTİLDİ) ---
DORTYOL_DATABASE = [
    {
        "ad": "Antik Kral Künefe", 
        "sektor": "Tatlıcı", 
        "urun": "Meşhur Kral Hasırı", 
        "tel": "0532 111 00 11",
        "icerik": "Dörtyol'un kalbinde, odun ateşinde pişen taze peynirli künefenin tek adresi.",
        "puan": 9.9, "tıklanma": 950, "sifre": "1234",
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
        "puan": 9.7, "tıklanma": 720, "sifre": "1234",
        "urunler": [
            {"ad": "Zırh Kıyma", "fiyat": 320, "detay": "Makine değmeden, bıçakla kıyılan et.", "tarihce": "Eski usul kebap kültürünü yaşatan özel teknik."},
            {"ad": "Kuşbaşı Kebap", "fiyat": 350, "detay": "Kuzu etinden yumuşacık lezzet.", "tarihce": "Özel terbiyesinde 24 saat bekletilen etler."}
        ]
    },
    {
        "ad": "Aydın Kuyumculuk", 
        "sektor": "Yatırım", 
        "urun": "Altın & Değerli Maden", 
        "tel": "0532 333 00 33",
        "icerik": "Dörtyol'da güvenin ve birikimin adresi. Çeyrek altından pırlantaya geniş seçenekler.",
        "puan": 9.8, "tıklanma": 600, "sifre": "1234",
        "urunler": [
            {"ad": "Çeyrek Altın", "fiyat": 4500, "detay": "22 Ayar, 1.75 gram saf altın.", "tarihce": "Yatırımın en küçük ve en güvenilir birimi. Gram altının dörtte biri ağırlığındadır."},
            {"ad": "Pırlanta Tektaş", "fiyat": 25000, "detay": "0.30 Karat, F color, sertifikalı.", "tarihce": "Sonsuz sevginin ve zarafetin pırıltılı simgesi. Karat, pırlantanın ağırlık birimidir."}
        ]
    },
    {
        "ad": "Dörtyol Taksi", 
        "sektor": "Ulaşım", 
        "urun": "7/24 Şehir İçi & Dışı Ulaşım", 
        "tel": "0544 555 44 33",
        "icerik": "Güvenli, konforlu ve hızlı ulaşımın Dörtyol'ataki tek adresi.",
        "puan": 9.4, "tıklanma": 430, "sifre": "1234",
        "urunler": [
            {"ad": "Şehir İçi Transfer", "fiyat": 100, "detay": "Dörtyol içi her noktaya.", "tarihce": "Günün her saati hızlı ve güvenilir ulaşım hizmeti."},
            {"ad": "Havaalanı Transfer", "fiyat": 1200, "detay": "Hatay/Adana Havalimanı ulaşımı.", "tarihce": "VIP konforunda, zamanında yetişme garantili hizmet."}
        ]
    },
    {
        "ad": "Kadir Usta Tamirhane", 
        "sektor": "Hizmet", 
        "urun": "Teknik Servis & Bakım", 
        "tel": "0505 111 22 33",
        "icerik": "Her türlü teknik arıza ve bakım işlerinizde usta işi çözümler.",
        "puan": 9.1, "tıklanma": 310, "sifre": "1234",
        "urunler": [
            {"ad": "Periyodik Bakım", "fiyat": 1500, "detay": "Yağ ve filtre değişim seti.", "tarihce": "Aracınızın sağlığı için her 10.000 km'de bir yapılması gereken işlem."},
            {"ad": "Arıza Tespit", "fiyat": 500, "detay": "Bilgisayarlı sistem kontrolü.", "tarihce": "Modern cihazlarla aracınızdaki gizli hataları bulma işlemi."}
        ]
    },
    {
        "ad": "Mavi / LC Waikiki", 
        "sektor": "Giyim", 
        "urun": "Yeni Sezon Koleksiyonları", 
        "tel": "0326 713 00 00",
        "icerik": "En trend moda ürünleri ve her bütçeye uygun kaliteli giyim seçenekleri.",
        "puan": 8.8, "tıklanma": 540, "sifre": "1234",
        "urunler": [
            {"ad": "Basic Tişört", "fiyat": 250, "detay": "%100 Pamuklu, her renk seçeneğiyle.", "tarihce": "Yaz aylarının vazgeçilmez, nefes alan kumaş dokusu."},
            {"ad": "Denim Pantolon", "fiyat": 850, "detay": "Slim fit, esnek Jean kumaşı.", "tarihce": "Dünya modasının zamansız parçası, dayanıklı ve şık."}
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
    elif st.session_state.sort_by == "En Çok Ziyaret":
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
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.4);
    }

    /* Kart Tasarımı */
    .business-card {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        border-left: 5px solid #ffcc00;
        padding: 25px;
        margin-bottom: 15px;
        transition: 0.4s;
        border-top: 1px solid #222;
    }
    .business-card:hover { background: rgba(255, 255, 255, 0.08); transform: translateY(-5px); }

    /* Ürün Satırı */
    .product-box {
        background: rgba(0,0,0,0.3);
        padding: 18px; border-radius: 15px;
        border: 1px solid #333; margin-bottom: 12px;
    }

    /* Gizli Teknik Yazılar */
    code { display: none !important; }
    .stMarkdown div p code { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.is_site_unlocked:
    st.markdown('<h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ffcc00; font-style:italic;">Prestijli Esnaf Portalı - 2026</p>', unsafe_allow_html=True)
    
    _, log_col, _ = st.columns([2, 1.5, 2])
    with log_col:
        st.markdown('<div style="background:rgba(0,0,0,0.5); padding:30px; border-radius:25px; border:1px solid #ffcc0033;">', unsafe_allow_html=True)
        pwd_try = st.text_input("Giriş Anahtarı", type="password", placeholder="••••••")
        if st.button("PORTALI AKTİF ET"):
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
with c_s: search_q = st.text_input("", placeholder="🔍 Dükkan, hizmet veya meşhur lezzet ara...", key="main_search_v20")
with c_f: st.session_state.sort_by = st.selectbox("Sıralama / Filtrele", ["En Yüksek Puan", "En Çok Ziyaret"])

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
    # Sektör Seçimi (Grid)
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
        shops = verileri_yukle()
        filtered = [s for s in shops if (search_q.lower() in s['ad'].lower() or search_q.lower() in s.get('urun', '').lower()) and (st.session_state.selected_cat == "Tümü" or s['sektor'] == st.session_state.selected_cat)]
        
        for s in filtered:
            st.markdown(f"""
                <div class="business-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ffcc00; font-weight:800; font-size:0.75rem; border:1px solid #444; padding:3px 12px; border-radius:50px;">{s['sektor'].upper()}</span>
                        <span style="color:#ffcc00; font-weight:900;">⭐ {s.get('puan', 0)} / 10</span>
                    </div>
                    <h2 style="margin:10px 0; color:white; font-family:'Cinzel', serif;">{s['ad']}</h2>
                    <p style="color:#ddd; font-size:1rem;">{s['icerik']}</p>
                    <p style="color:#666; font-size:0.8rem;">İmza Ürün: <b>{s.get('urun', '-')}</b> | 👁️ {s.get('tıklanma', 0)} Ziyaret</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🏪 {s['ad']} Menüsünü İncele", key=f"view_{s['ad']}"):
                st.session_state.selected_shop = s
                if db and col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                st.rerun()
    else:
        # DÜKKAN DETAY SAYFASI
        s = st.session_state.selected_shop
        if st.button("⬅️ ÇARŞI MEYDANINA DÖN"):
            st.session_state.selected_shop = None
            st.rerun()
        
        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.8); padding:50px; border-radius:35px; border:2px solid #ffcc00; text-align:center;">
                <h1 style="color:#ffcc00; font-family:'Cinzel', serif; font-size:3.5rem; margin:0;">{s['ad']}</h1>
                <p style="font-size:1.2rem; color:#888; letter-spacing:2px;">ELITE ESNAF PROFİLİ</p>
                <hr style="border-color:#333; width:50%; margin:20px auto;">
                <p style="font-size:1.3rem; line-height:1.7; color:#bbb; max-width:850px; margin:0 auto; font-style:italic;">"{s['icerik']}"</p>
            </div>
            <h3 style="color:#ffcc00; margin-top:40px; font-family:Cinzel, serif; letter-spacing:3px;">📋 ÜRÜNLER & HİZMETLER</h3>
        """, unsafe_allow_html=True)
        
        # Ürünlerin Listelenmesi
        for item in s.get('urunler', []):
            st.markdown(f"""
                <div class="product-box">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#ffcc00; letter-spacing:1px;">{item['ad']}</h4>
                        <span style="font-weight:900; color:white; font-size:1.3rem;">{item.get('fiyat', 0)} ₺</span>
                    </div>
                    <p style="color:#ccc; margin:8px 0; font-size:0.95rem;">{item.get('detay', '-')}</p>
                </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📜 {item['ad']} Hakkında Bilgi & Tarihçe"):
                st.write(item.get('tarihce', 'Bu ürün için detaylı bilgi girilmemiş.'))
        
        st.markdown(f"""
            <br><a href="https://wa.me/{s['tel'].replace(' ','')}" target="_blank">
                <button style="width:100%; background:#25D366; color:white; border:none; padding:20px; border-radius:20px; font-weight:bold; font-size:1.4rem; cursor:pointer; box-shadow: 0 10px 20px rgba(0,0,0,0.3);">
                    🟢 WHATSAPP İLE SİPARİŞ / BİLGİ HATTI
                </button>
            </a>
        """, unsafe_allow_html=True)

# --- 2. KURUMSAL KAYIT ---
with tabs[1]:
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🏛️ KURUMSAL KAYIT BAŞVURUSU</h3>", unsafe_allow_html=True)
    with st.form("reg_pro_v20"):
        c1, c2 = st.columns(2)
        with c1:
            n_ad = st.text_input("İşletme Adı*")
            n_tel = st.text_input("WhatsApp İletişim (05xx...)*")
        with c2:
            n_sek = st.selectbox("Sektör Seçin", [k['ad'] for k in kategoriler if k['ad'] != "Tümü"])
            n_pwd = st.text_input("Yönetim Şifresi*", type="password")
        n_urn = st.text_input("İmza Ürün/Hizmet")
        n_tanitim = st.text_area("İşletme Tanıtım Yazısı")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA"):
            if n_ad and n_pwd and db:
                data = {"ad": n_ad, "tel": n_tel, "sektor": n_sek, "urun": n_urn, "icerik": n_tanitim, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": []}
                col_ref.add(data)
                st.success("Tebrikler! Dükkanınız kaydedildi. 'Esnaf Paneli'nden ürünlerinizi ekleyebilirsiniz."); time.sleep(1); st.rerun()

# --- 3. ESNAF PANELİ (DYNAMIC CMS) ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='text-align:center;'>🔐 ESNAF DİJİTAL YÖNETİMİ</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Kayıtlı Dükkan Adınız")
        l_pwd = st.text_input("Şifreniz", type="password")
        if st.button("PANELE GİRİŞ YAP"):
            all_s = verileri_yukle()
            match = next((s for s in all_s if s['ad'] == l_ad and s.get('sifre') == l_pwd), None)
            if match: st.session_state.owner_shop_id = match; st.rerun()
            else: st.error("Giriş bilgileri hatalı.")
    else:
        d = st.session_state.owner_shop_id
        st.subheader(f"📊 {d['ad']} Kontrol Merkezi")
        st.write(f"Mağaza Ziyareti: **{d.get('tıklanma', 0)}** | Skor: **⭐ {d.get('puan', 0)}**")
        
        st.divider()
        with st.expander("➕ Menüye Yeni Ürün/Hizmet Ekle"):
            u_ad = st.text_input("Ürün/Hizmet Adı")
            u_fiy = st.number_input("Fiyat (₺)", min_value=0)
            u_det = st.text_input("Kısa Tanıtım (Müşterinin ilk göreceği yazı)")
            u_tar = st.text_area("Ürün Tarihçesi / Teknik Bilgi (Altın ayarı, kumaş türü vb.)")
            if st.button("ÜRÜNÜ YAYINLA"):
                current_prods = d.get('urunler', [])
                current_prods.append({"ad": u_ad, "fiyat": u_fiy, "detay": u_det, "tarihce": u_tar})
                if db and col_ref and 'id' in d:
                    col_ref.document(d['id']).update({"urunler": current_prods})
                    st.success("Yeni ürün menüye eklendi!"); time.sleep(1); st.rerun()
        
        if st.button("🚪 PANELİ KAPAT"):
            st.session_state.owner_shop_id = None
            st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Yönetici Anahtarı", type="password")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Yetkisi Aktif.")
        all_d = verileri_yukle()
        for i in all_d:
            if 'id' in i:
                with st.expander(f"⚙️ {i['ad']}"):
                    if st.button(f"SİSTEMDEN SİL: {i['ad']}", key=f"del_{i['id']}"):
                        col_ref.document(i['id']).delete(); st.rerun()

# FOOTER
st.markdown(f"<div style='text-align:center; padding-top:100px; opacity:0.3; font-size:0.75rem;'>© {GUNCEL_YIL} Albayrax Elite Portal | v20.0 BugFix & Dynamic CMS</div>", unsafe_allow_html=True)
