import streamlit as st
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import time
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Dörtyol Esnaf Portalı | 2026 Elite Hub",
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
            p_id = key_dict.get("project_id")
            b_name = st.secrets["firebase"].get("storage_bucket", f"{p_id}.firebasestorage.app")
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'storageBucket': b_name})
    except Exception as e:
        pass

db = firestore.client() if firebase_admin._apps else None
col_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("dukkanlar") if db else None

# --- SESSION STATE ---
states = {
    'is_site_unlocked': False,
    'selected_cat': "Tümü",
    'selected_shop_id': None,
    'owner_shop_id': None
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- HAYALİ VE ESTETİK VERİ SETİ ---
DORTYOL_DATABASE = [
    {
        "ad": "Kadir Teknoloji", "sektor": "Teknoloji", "sifre": "tekno2026", "puan": 5.0, "tıklanma": 1240,
        "icerik": "Geleceğin teknolojisi Dörtyol'da. Robotik sistemler ve akıllı yazılım çözümleri.",
        "tel": "0531 000 00 00", "adres": "Dijital Vadi No:1", "saatler": "09:00 - 20:00",
        "img": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800",
        "urunler": [{"ad": "AI Otomasyon Sistemi", "fiyat": 15000, "desc": "İşletmeniz için yapay zeka."}, {"ad": "Teknik Destek", "fiyat": 750, "desc": "7/24 Uzaktan yardım."}]
    },
    {
        "ad": "Antik Kral Künefe", "sektor": "Tatlıcı", "sifre": "kral2026", "puan": 4.9, "tıklanma": 3500,
        "icerik": "Odun ateşinde, Hatay'ın tescilli peyniri ile hazırlanan eşsiz künefe şöleni.",
        "tel": "0532 111 22 33", "adres": "Atatürk Cad. Merkez", "saatler": "10:00 - 01:00",
        "img": "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800",
        "urunler": [{"ad": "Özel Kral Hasırı", "fiyat": 240, "desc": "Bol fıstıklı imza ürün."}, {"ad": "Peynirli Künefe", "fiyat": 180, "desc": "Sıcak ve taze."}]
    },
    {
        "ad": "Dörtyol Petrol Ofisi", "sektor": "Ulaşım", "sifre": "petrol2026", "puan": 4.7, "tıklanma": 850,
        "icerik": "En yüksek standartlarda yakıt kalitesi ve geniş market alanı ile hizmetinizdeyiz.",
        "tel": "0326 712 00 00", "adres": "E-5 Karayolu Dörtyol Mevkii", "saatler": "24 Saat Açık",
        "img": "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800",
        "urunler": [{"ad": "V-Max Kurşunsuz 95", "fiyat": 60.50, "desc": "Performans serisi."}, {"ad": "V-Pro Dizel", "fiyat": 50.25, "desc": "Temiz yanma teknolojisi."}]
    },
    {
        "ad": "Aydın Kuyumculuk", "sektor": "Yatırım", "sifre": "aydin2026", "puan": 4.8, "tıklanma": 2100,
        "icerik": "Yatırımın en güvenli limanı. Has altın, pırlanta ve mücevheratta yarım asırlık tecrübe.",
        "tel": "0532 000 00 00", "adres": "Kuyumcular Çarşısı No:12", "saatler": "08:30 - 18:30",
        "img": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=800",
        "urunler": [{"ad": "Gram Altın (24A)", "fiyat": 3200, "desc": "Sertifikalı yatırım altını."}, {"ad": "Tektaş Pırlanta", "fiyat": 25000, "desc": "E sertifikalı tasarım."}]
    }
]

def verileri_yukle():
    if col_ref:
        try:
            docs = col_ref.stream()
            data = [dict(doc.to_dict(), id=doc.id) for doc in docs]
            return data if data else DORTYOL_DATABASE
        except: return DORTYOL_DATABASE
    return DORTYOL_DATABASE

# --- GOOGLE INSPIRED MODERN UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@400;700;900&display=swap');
    
    .stApp {{ 
        background-color: #F8F9FA; 
        font-family: 'Inter', sans-serif;
    }}

    /* Ana Başlık - Google Tarzı Temiz Vurgu */
    .main-title {{ 
        font-family: 'Outfit', sans-serif;
        font-weight: 900; 
        color: #001F3F; 
        font-size: 3.2rem; 
        text-align: center; 
        letter-spacing: -2px; 
        margin-top: -80px;
        background: linear-gradient(90deg, #001F3F, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Kart Yapıları */
    .business-card {{ 
        background: white; 
        border-radius: 24px; 
        padding: 0; 
        margin-bottom: 24px; 
        transition: all 0.4s ease;
        border: 1px solid #E5E7EB;
        overflow: hidden;
    }}
    .business-card:hover {{ 
        transform: translateY(-8px); 
        box-shadow: 0 20px 40px rgba(0,0,0,0.08); 
        border-color: #FF8C00;
    }}

    .card-content {{ padding: 25px; }}

    /* Fiyat Etiketleri - Okunaklı ve Dengeli */
    .price-tag {{ 
        background: #F1F5F9; 
        color: #001F3F !important; 
        padding: 8px 16px; 
        border-radius: 12px; 
        font-weight: 800; 
        font-size: 1.1rem; 
        border: 1px solid #E2E8F0;
    }}

    /* Butonlar - Modern Yuvarlak */
    .stButton>button {{
        background-color: #001F3F !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,31,63,0.15) !important;
        transition: all 0.3s !important;
    }}
    .stButton>button:hover {{
        background-color: #FF8C00 !important;
        transform: scale(1.05);
    }}

    /* Kategori Hapları */
    .stButton [data-testid="baseButton-secondary"] {{
        background: white !important;
        color: #001F3F !important;
        border: 1px solid #E5E7EB !important;
    }}

    code {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.is_site_unlocked:
    st.markdown('<div style="height:150px;"></div><h1 class="main-title">DÖRTYOL ÇARŞI</h1>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([2, 1.2, 2])
    with col_log:
        st.markdown(f'''
            <div style="background:white; padding:40px; border-radius:32px; border:1px solid #E5E7EB; text-align:center; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                <h2 style="color:#001F3F; font-family:'Outfit';">Elite Giriş</h2>
                <p style="color:#64748B; font-size:0.9rem;">Dörtyol'un dijital kalbine hoş geldiniz.</p>
            </div>
        ''', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Anahtar Kod")
        if st.button("PORTALI AKTİF ET", use_container_width=True):
            if pwd == SITE_GIRIS_SIFRESI:
                st.session_state.is_site_unlocked = True
                st.rerun()
            else: st.error("Hatalı Kod!")
    st.stop()

# --- MAIN ---
st.markdown('<h1 class="main-title">DÖRTYOL PORTAL</h1>', unsafe_allow_html=True)
tabs = st.tabs(["💎 KEŞFET", "🏛️ DÜKKAN AÇ", "🔐 ESNAF PANELİ", "🔑 ADMİN"])

all_shops = verileri_yukle()

# --- 1. KEŞFET SEKMESİ ---
with tabs[0]:
    search_q = st.text_input("", placeholder="🔍 Ürün, dükkan veya kategori ara...", key="main_search_v39")
    
    cats = ["Tümü", "Tatlıcı", "Kebapçı", "Sağlık", "Ulaşım", "Yatırım", "Teknoloji"]
    c_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"c_v39_{c}", use_container_width=True):
            st.session_state.selected_cat = c
            st.session_state.selected_shop_id = None
            st.rerun()

    st.divider()

    if st.session_state.selected_shop_id is None:
        filtered = [s for s in all_shops if (st.session_state.selected_cat == "Tümü" or s.get('sektor') == st.session_state.selected_cat) and (search_q.lower() in s.get('ad','').lower())]
        
        for s in filtered:
            with st.container():
                st.markdown('<div class="business-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2.2])
                with c1:
                    st.image(s.get('img', ""), use_container_width=True)
                with c2:
                    st.markdown(f"""
                    <div class="card-content">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="background:#FFF7ED; color:#EA580C; font-weight:800; font-size:0.7rem; padding:4px 12px; border-radius:50px; border:1px solid #FFEDD5;">{s.get('sektor','').upper()}</span>
                            <span style="color:#001F3F; font-weight:800; font-size:0.9rem;">⭐ {s.get('puan', 0)}</span>
                        </div>
                        <h2 style="margin:0; color:#001F3F; font-family:'Outfit'; font-weight:900; font-size:1.8rem;">{s.get('ad','')}</h2>
                        <p style="color:#475569; margin:15px 0; font-size:1rem; line-height:1.6;">{s.get('icerik','')[:160]}...</p>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <small style="color:#94A3B8; font-weight:600;">👁️ {s.get('tıklanma', 0)} Görüntülenme</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Mağazayı Gez →", key=f"v_v39_{s.get('id', s.get('ad'))}", use_container_width=True):
                        st.session_state.selected_shop_id = s.get('id', s.get('ad'))
                        if col_ref and 'id' in s: col_ref.document(s['id']).update({"tıklanma": firestore.Increment(1)})
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DETAY SAYFASI
        shop = next((s for s in all_shops if (s.get('id') == st.session_state.selected_shop_id or s.get('ad') == st.session_state.selected_shop_id)), None)
        if st.button("← KEŞFETE GERİ DÖN"): st.session_state.selected_shop_id = None; st.rerun()
        if shop:
            st.image(shop.get('img',''), use_container_width=True)
            st.markdown(f"<h1 style='color:#001F3F; font-family:Outfit; font-weight:900; font-size:3rem; margin-top:20px;'>{shop['ad']}</h1>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:#001F3F; color:white; padding:20px; border-radius:20px; display:flex; gap:20px; margin-bottom:30px;">
                    <span>📍 {shop.get('adres','')}</span> | <span>🕒 {shop.get('saatler','')}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📋 Menü ve Ürünler")
            for item in shop.get('urunler', []):
                st.markdown(f"""
                <div style="background:white; border:1px solid #E5E7EB; padding:25px; border-radius:24px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <div>
                        <span style="font-weight:800; color:#001F3F; font-size:1.2rem; display:block;">{item['ad']}</span>
                        <small style="color:#64748B;">{item.get('desc','Hemen Sipariş Ver')}</small>
                    </div>
                    <span class="price-tag">{item['fiyat']} ₺</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.button("💬 WHATSAPP ÜZERİNDEN SİPARİŞ VER", use_container_width=True)

# --- 2. DÜKKAN AÇ (KURUMSAL FORM) ---
with tabs[1]:
    st.markdown('<div style="background:#FF8C00; padding:40px; border-radius:32px; color:white;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#001F3F; font-family:Outfit;'>🏛️ İşletmenizi Dijitale Taşıyın</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#001F3F;'>Dörtyol'un en prestijli dükkanları arasındaki yerinizi bugün alın.</p>", unsafe_allow_html=True)
    with st.form("reg_v39"):
        c1, c2 = st.columns(2)
        n_ad = c1.text_input("İşletme Resmi Adı*")
        n_sek = c2.selectbox("Sektörünüz*", cats[1:])
        n_pwd = c1.text_input("Yönetim Şifresi Belirleyin*", type="password")
        n_icr = st.text_area("İşletme Tanıtım Yazısı (En az 50 kelime önerilir)")
        if st.form_submit_button("📜 BAŞVURUYU TAMAMLA VE YAYINLA"):
            if n_ad and n_pwd and col_ref:
                col_ref.add({"ad": n_ad, "sektor": n_sek, "sifre": n_pwd, "puan": 0, "tıklanma": 0, "urunler": [], "icerik": n_icr, "adres": "Dörtyol", "saatler": "09:00-18:00", "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"})
                st.success("Tebrikler! Dükkanınız Elite ağımıza katıldı."); time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ESNAF PANELİ ---
with tabs[2]:
    if st.session_state.owner_shop_id is None:
        st.markdown("<h3 style='color:#001F3F;'>🔐 Esnaf Dashboard Girişi</h3>", unsafe_allow_html=True)
        l_ad = st.text_input("Dükkan Adı", placeholder="Örn: Antik Kral Künefe")
        l_pwd = st.text_input("Panel Şifresi", type="password")
        if st.button("YÖNETİM PANELİNİ AÇ"):
            match = next((s for s in all_shops if s.get('ad','').lower().strip() == l_ad.lower().strip() and str(s.get('sifre','')).strip() == l_pwd.strip()), None)
            if match: st.session_state.owner_shop_id = match.get('id', match.get('ad')); st.rerun()
            else: st.error("Bilgiler uyuşmuyor!")
    else:
        shop_id = st.session_state.owner_shop_id
        d = next((s for s in all_shops if (s.get('id') == shop_id or s.get('ad') == shop_id)), None)
        if d:
            st.subheader(f"📊 {d['ad']} Yönetim Merkezi")
            with st.expander("📝 Ürün / Hizmet Listesini Güncelle"):
                u_n = st.text_input("Yeni Ürün İsmi")
                u_p = st.number_input("Fiyat (TL)", min_value=0.0)
                u_d = st.text_input("Kısa Açıklama")
                if st.button("VİTRİNE EKLE VE YAYINLA"):
                    prods = d.get('urunler', [])
                    prods.append({"ad": u_n, "fiyat": u_p, "desc": u_d})
                    col_ref.document(d['id']).update({"urunler": prods})
                    st.success("Ürün anında müşterilere sunuldu!"); time.sleep(1); st.rerun()
            if st.button("🚪 PANELİ GÜVENLİ KAPAT"): st.session_state.owner_shop_id = None; st.rerun()

# --- 4. ADMİN ---
with tabs[3]:
    pwd = st.text_input("Süper Yönetici Girişi", type="password", key="admin_v39")
    if pwd == ADMIN_SIFRE:
        st.success("Admin Kontrol Paneli Aktif.")
        for i in all_shops:
            with st.expander(f"⚙️ {i.get('ad','')} Kaydını Yönet"):
                st.write(f"Şifre: **{i.get('sifre')}** | Toplam Tıklanma: **{i.get('tıklanma')}**")
                if st.button(f"SİSTEMDEN KALDIR: {i.get('ad')}", key=f"del_v39_{i.get('ad')}"):
                    if col_ref and 'id' in i: col_ref.document(i['id']).delete(); st.rerun()

st.markdown(f"<div style='text-align:center; padding-top:100px; color:#001F3F; font-weight:800; font-size:0.8rem; opacity:0.6;'>© {GUNCEL_YIL} Albayrax Dijital Hub | v39.0 Google Inspired Edition</div>", unsafe_allow_html=True)
