import React, { useState, useMemo } from 'react';
import { 
  Search, 
  MapPin, 
  Phone, 
  Clock, 
  Star, 
  ShoppingBag, 
  Lock, 
  ShieldCheck, 
  Zap,
  TrendingDown,
  ChevronRight,
  MessageCircle,
  Home,
  Grid,
  Bell,
  User,
  Heart,
  ArrowLeft,
  Share2,
  Cpu,
  Gem,
  UtensilsCrossed,
  Fuel
} from 'lucide-react';

// --- GELİŞMİŞ HAYALİ VERİ SETİ ---
const INITIAL_SHOPS = [
  {
    id: "kadir-tekno",
    name: "Kadir Teknoloji",
    category: "Teknoloji",
    rating: 5.0,
    discount: "%15 İndirim",
    image: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800", // Robot/Tech image
    desc: "Yapay zeka sistemleri, robotik kodlama ve ileri teknoloji donanım merkezi.",
    address: "Dörtyol Dijital Vadisi, No:1",
    hours: "09:00 - 20:00",
    products: [
      { id: 1, name: "Yapay Zeka Sunucu Paketi", price: 12500, oldPrice: 15000, desc: "Kadir AI altyapılı." },
      { id: 2, name: "Robotik Eğitim Kiti", price: 2450, desc: "Geleceğin mühendisleri için." }
    ]
  },
  {
    id: "antik-kral",
    name: "Antik Kral Künefe",
    category: "Tatlıcı",
    rating: 4.9,
    discount: "Sınırsız İkram",
    image: "https://images.unsplash.com/photo-1541450805268-4822a3a774ca?q=80&w=800", // Genuine Kunafa/Turkish dessert
    desc: "Tescilli kral hasırı, fıstıkzade ve geleneksel Hatay tatlı sanatının zirvesi.",
    address: "Atatürk Caddesi, Çarşı İçi",
    hours: "10:00 - 01:00",
    products: [
      { id: 1, name: "Kral Hasırı", price: 240, oldPrice: 280, desc: "Bol fıstıklı imza lezzet." },
      { id: 2, name: "Kaymaklı Künefe", price: 180, desc: "Odun ateşinde sıcak servis." },
      { id: 3, name: "Fıstık Sarma", price: 240, desc: "Gaziantep fıstığının en saf hali." }
    ]
  },
  {
    id: "po-dortyol",
    name: "Dörtyol Petrol Ofisi",
    category: "Ulaşım",
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1545143333-636a661f391e?q=80&w=800", // Real Petrol Station
    desc: "Güvenli yakıt, 24 saat açık market ve ultra hızlı servis noktası.",
    address: "E-5 Karayolu, Dörtyol Girişi",
    hours: "24 Saat Açık",
    products: [
      { id: 1, name: "Kurşunsuz 95 (Litre)", price: 60.50, oldPrice: 62.10, desc: "V-Max Performans Serisi." },
      { id: 2, name: "V-Pro Dizel", price: 50.25, desc: "Yeni nesil temiz yakıt." }
    ]
  },
  {
    id: "aydin-kuyumcu",
    name: "Aydın Kuyumculuk",
    category: "Yatırım",
    rating: 4.8,
    image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=800", // Gold and Jewelry
    desc: "Has altın, mücevherat ve yatırım danışmanlığında Dörtyol'un güven kapısı.",
    address: "Kuyumcular Çarşısı, No:12",
    hours: "08:30 - 18:30",
    products: [
      { id: 1, name: "Gram Altın (24 Ayar)", price: 3150, desc: "Yatırımın en güvenli limanı." },
      { id: 2, name: "Tektaş Pırlanta Yüzük", price: 45000, oldPrice: 52000, desc: "E sertifikalı özel tasarım." }
    ]
  },
  {
    id: "ferah-kebap",
    name: "Ferah Kebap Salonu",
    category: "Kebapçı",
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1561651823-34feb02250e4?q=80&w=800", // Kebab/Grill
    desc: "Gerçek zırh kıyması ve közlenmiş Hatay mezeleri ile unutulmaz lezzet.",
    address: "İnönü Caddesi, Meydan Karşısı",
    hours: "11:00 - 22:00",
    products: [
      { id: 1, name: "Adana Kebap (Zırh)", price: 350, desc: "Köz biber ve soğan salatası ile." },
      { id: 2, name: "Kuşbaşı Şiş", price: 420, desc: "Kuzu buttan özel marine." }
    ]
  }
];

const CATEGORIES = [
  { name: "Tümü", icon: <Grid size={24}/>, color: "bg-gray-100" },
  { name: "Tatlıcı", icon: <UtensilsCrossed size={24}/>, color: "bg-orange-100" },
  { name: "Kebapçı", icon: <UtensilsCrossed size={24}/>, color: "bg-red-100" },
  { name: "Ulaşım", icon: <Fuel size={24}/>, color: "bg-green-100" },
  { name: "Yatırım", icon: <Gem size={24}/>, color: "bg-indigo-100" },
  { name: "Teknoloji", icon: <Cpu size={24}/>, color: "bg-purple-100" }
];

export default function App() {
  const [view, setView] = useState('home'); 
  const [selectedCategory, setSelectedCategory] = useState('Tümü');
  const [selectedShop, setSelectedShop] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredShops = useMemo(() => {
    return INITIAL_SHOPS.filter(shop => {
      const matchesCat = selectedCategory === 'Tümü' || shop.category === selectedCategory;
      const matchesSearch = shop.name.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCat && matchesSearch;
    });
  }, [selectedCategory, searchQuery]);

  const handleOpenShop = (shop) => {
    setSelectedShop(shop);
    setView('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#FDFDFD] text-[#1D1D1F] pb-24 md:pb-0 font-sans tracking-tight">
      
      {/* --- MASAÜSTÜ NAV --- */}
      <nav className="hidden md:flex sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100 h-20 px-10 items-center justify-between shadow-sm">
        <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setView('home')}>
          <div className="w-10 h-10 bg-orange-500 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:rotate-6 transition-transform">D</div>
          <span className="font-black text-2xl tracking-tighter text-gray-900 uppercase">Dörtyol Çarşı</span>
        </div>
        <div className="flex items-center gap-10">
          <button onClick={() => setView('home')} className="font-bold text-sm uppercase tracking-widest hover:text-orange-500 transition-colors">Keşfet</button>
          <button onClick={() => setView('register')} className="font-bold text-sm uppercase tracking-widest hover:text-orange-500 transition-colors">Dükkan Aç</button>
          <button onClick={() => setView('login')} className="flex items-center gap-2 bg-gray-900 text-white px-8 py-3 rounded-full font-bold text-xs uppercase tracking-widest hover:bg-orange-500 transition-all shadow-xl active:scale-95">
            <Lock size={16} /> Esnaf Paneli
          </button>
        </div>
      </nav>

      {/* --- MOBİL ÜST BAR --- */}
      <header className="md:hidden sticky top-0 z-50 bg-white/80 backdrop-blur-md px-5 py-5 flex items-center justify-between border-b border-gray-50">
        <div className="flex items-center gap-2" onClick={() => setView('home')}>
          <div className="w-8 h-8 bg-orange-500 rounded-xl flex items-center justify-center text-white font-bold">D</div>
          <span className="font-black text-lg tracking-tighter uppercase">Dörtyol Çarşı</span>
        </div>
        <div className="flex gap-2">
          <button className="p-2.5 bg-gray-50 rounded-full text-gray-400 active:scale-90 transition-transform"><Bell size={20} /></button>
          <button className="p-2.5 bg-gray-50 rounded-full text-gray-400 active:scale-90 transition-transform" onClick={() => setView('login')}><User size={20} /></button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {view === 'home' && (
          <div className="space-y-10 animate-in fade-in duration-700">
            {/* Arama Kutusu */}
            <div className="relative group">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-orange-500 transition-colors" size={20} />
              <input 
                type="text" 
                placeholder="Dörtyol'da ne aramıştınız? (Künefe, Altın, Benzin...)"
                className="w-full bg-gray-100 border-none py-5 pl-14 pr-6 rounded-[2rem] focus:ring-4 focus:ring-orange-500/5 focus:bg-white transition-all outline-none font-bold text-gray-800 shadow-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Hikaye Tarzı Kategoriler */}
            <section>
              <div className="flex items-center justify-between mb-5 px-1">
                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Hızlı Kategoriler</h3>
              </div>
              <div className="flex gap-6 overflow-x-auto no-scrollbar pb-2">
                {CATEGORIES.map(cat => (
                  <div 
                    key={cat.name} 
                    onClick={() => setSelectedCategory(cat.name)}
                    className="flex flex-col items-center gap-3 flex-shrink-0 cursor-pointer group"
                  >
                    <div className={`w-16 h-16 ${cat.color} rounded-[1.8rem] flex items-center justify-center group-active:scale-90 transition-all border-2 ${selectedCategory === cat.name ? 'border-orange-500 ring-8 ring-orange-50' : 'border-transparent shadow-sm'}`}>
                      {cat.icon}
                    </div>
                    <span className={`text-[11px] font-black uppercase tracking-tighter ${selectedCategory === cat.name ? 'text-orange-600' : 'text-gray-400'}`}>{cat.name}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Fiyat Savaşı Kartı */}
            {!searchQuery && (
              <div className="bg-orange-500 rounded-[2.5rem] p-7 text-white flex items-center justify-between shadow-2xl shadow-orange-100 overflow-hidden relative group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-150 transition-transform duration-1000">
                  <TrendingDown size={120} />
                </div>
                <div className="flex items-center gap-5 relative z-10">
                  <div className="w-14 h-14 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
                    <TrendingDown size={28} strokeWidth={3} />
                  </div>
                  <div>
                    <p className="text-[10px] font-black uppercase tracking-[0.3em] text-orange-100 mb-1">Günün Savaşçısı: En Ucuz</p>
                    <h4 className="font-black text-lg leading-none uppercase italic">Dörtyol Petrol Ofisi</h4>
                  </div>
                </div>
                <div className="text-right relative z-10">
                  <span className="text-4xl font-black tracking-tighter">60.50 ₺</span>
                  <p className="text-[10px] text-orange-100 font-bold uppercase mt-1">Litre Fiyatı</p>
                </div>
              </div>
            )}

            {/* Dükkan Listesi */}
            <section className="space-y-8 pb-10">
              <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 px-1">Seçkin Dörtyol Esnafları</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {filteredShops.map(shop => (
                  <div 
                    key={shop.id}
                    onClick={() => handleOpenShop(shop)}
                    className="group bg-white rounded-[2.5rem] overflow-hidden shadow-sm border border-gray-100/50 hover:shadow-2xl hover:shadow-orange-100 hover:border-orange-100 transition-all duration-500 cursor-pointer"
                  >
                    <div className="relative h-60 overflow-hidden">
                      <img src={shop.image} alt={shop.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" />
                      {shop.discount && (
                        <div className="absolute top-6 right-6 bg-orange-500 text-white px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg border border-white/20">
                          {shop.discount}
                        </div>
                      )}
                      <div className="absolute bottom-6 left-6">
                         <span className="bg-black/80 backdrop-blur-md text-white px-3 py-1.5 rounded-xl text-[11px] font-black flex items-center gap-1.5">
                          <Star size={12} fill="#f97316" className="text-orange-500" /> {shop.rating.toFixed(1)}
                         </span>
                      </div>
                    </div>
                    <div className="p-8 flex justify-between items-center">
                      <div className="space-y-2">
                        <h4 className="text-2xl font-black text-gray-900 tracking-tighter leading-none">{shop.name}</h4>
                        <p className="text-xs text-gray-400 font-bold max-w-[200px] leading-relaxed">{shop.desc}</p>
                      </div>
                      <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-300 group-hover:bg-orange-500 group-hover:text-white transition-all shadow-inner">
                        <ChevronRight size={28} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {view === 'detail' && selectedShop && (
          <div className="animate-in slide-in-from-right duration-700 pb-12">
            <button 
              onClick={() => setView('home')}
              className="mb-8 flex items-center gap-3 font-black text-[10px] uppercase tracking-[0.2em] text-gray-400 hover:text-black transition-colors bg-gray-100 px-6 py-3 rounded-full shadow-sm"
            >
              <ArrowLeft size={16} /> Geri Keşfe Dön
            </button>

            <div className="space-y-10">
              <div className="relative h-[450px] rounded-[4rem] overflow-hidden shadow-2xl">
                <img src={selectedShop.image} className="w-full h-full object-cover" alt={selectedShop.name} />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent"></div>
                <div className="absolute top-8 right-8 flex gap-3">
                  <button className="p-5 bg-white/10 backdrop-blur-xl rounded-3xl text-white hover:bg-white/30 transition-all border border-white/10"><Heart size={24} /></button>
                  <button className="p-5 bg-white/10 backdrop-blur-xl rounded-3xl text-white hover:bg-white/30 transition-all border border-white/10"><Share2 size={24} /></button>
                </div>
                <div className="absolute bottom-12 left-12 space-y-4">
                  <div className="flex gap-3">
                    <span className="bg-orange-500 px-4 py-1.5 rounded-full text-[10px] font-black uppercase text-white tracking-[0.1em]">{selectedShop.category}</span>
                    <span className="bg-white/20 backdrop-blur px-4 py-1.5 rounded-full text-[10px] font-black uppercase text-white tracking-[0.1em] flex items-center gap-2">
                      <Star size={12} fill="currentColor" /> {selectedShop.rating} Puan
                    </span>
                  </div>
                  <h1 className="text-5xl md:text-7xl font-black text-white tracking-tighter leading-none">{selectedShop.name}</h1>
                  <p className="text-gray-300 font-medium max-w-2xl text-lg leading-relaxed">{selectedShop.desc}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-5">
                <div className="md:col-span-2 space-y-6">
                  <h3 className="font-black text-2xl px-2 uppercase tracking-tighter">Menü & Ürün Kataloğu</h3>
                  <div className="grid gap-5">
                    {selectedShop.products.map(p => (
                      <div key={p.id} className="bg-white border border-gray-100/80 p-8 rounded-[2.5rem] flex items-center justify-between shadow-sm hover:shadow-xl hover:border-orange-200 transition-all group">
                        <div className="space-y-2">
                          <span className="font-black text-gray-900 text-xl tracking-tighter block leading-none group-hover:text-orange-500 transition-colors">{p.name}</span>
                          <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">{p.desc}</p>
                        </div>
                        <div className="text-right">
                           {p.oldPrice && <span className="block text-[11px] text-gray-400 line-through mb-1 font-bold">{p.oldPrice} ₺</span>}
                           <span className="font-black text-xl text-gray-900 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100">{p.price} ₺</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="space-y-6">
                  <div className="bg-white p-10 rounded-[3rem] border border-gray-100 shadow-xl space-y-8 sticky top-24">
                    <h3 className="font-black text-lg uppercase tracking-widest text-gray-900">Kurumsal Künye</h3>
                    <div className="space-y-6">
                      <div className="flex items-center gap-5">
                        <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-400 shadow-inner"><MapPin size={22} /></div>
                        <div><p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Konum</p><p className="text-sm font-bold text-gray-800">{selectedShop.address}</p></div>
                      </div>
                      <div className="flex items-center gap-5">
                        <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-400 shadow-inner"><Clock size={22} /></div>
                        <div><p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Saatler</p><p className="text-sm font-bold text-gray-800">{selectedShop.hours}</p></div>
                      </div>
                    </div>
                    <button className="w-full bg-[#25D366] text-white py-6 rounded-3xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-green-100 hover:scale-[1.03] active:scale-95 transition-all">
                      <MessageCircle size={28} /> WhatsApp'tan Sor
                    </button>
                    <p className="text-[10px] text-center text-gray-300 font-bold uppercase tracking-widest">Siparişleriniz satıcıya direkt iletilir.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {view === 'register' && (
          <div className="max-w-xl mx-auto py-10 animate-in fade-in zoom-in-95 duration-700">
            <div className="bg-gray-900 rounded-[3rem] p-12 text-white shadow-2xl relative overflow-hidden">
               <div className="absolute top-[-10%] right-[-10%] w-64 h-64 bg-orange-500/20 rounded-full blur-3xl"></div>
               <div className="relative z-10 space-y-8">
                  <div className="text-center space-y-3">
                    <h2 className="text-4xl font-black tracking-tighter uppercase leading-none">Dükkanını <br/> <span className="text-orange-500 italic">Dünyaya Aç.</span></h2>
                    <p className="text-gray-400 font-bold text-sm uppercase tracking-widest">Dörtyol'un En Büyük Platformuna Katılın</p>
                  </div>
                  <div className="space-y-4">
                    <input type="text" placeholder="İşletme Adı*" className="w-full bg-white/5 border border-white/10 p-5 rounded-2xl outline-none focus:border-orange-500 transition-colors font-bold" />
                    <select className="w-full bg-white/5 border border-white/10 p-5 rounded-2xl outline-none focus:border-orange-500 transition-colors font-bold text-gray-400">
                      <option>Sektör Seçin*</option>
                      {CATEGORIES.slice(1).map(c => <option key={c.name}>{c.name}</option>)}
                    </select>
                    <input type="password" placeholder="Yönetim Şifresi Belirleyin*" className="w-full bg-white/5 border border-white/10 p-5 rounded-2xl outline-none focus:border-orange-500 transition-colors font-bold" />
                    <button className="w-full bg-orange-500 py-5 rounded-2xl font-black text-lg shadow-xl shadow-orange-500/20 hover:scale-105 transition-all">BAŞVURUYU TAMAMLA</button>
                  </div>
                  <div className="flex justify-center gap-6 opacity-30">
                    <ShieldCheck size={20}/> <Zap size={20}/> <Heart size={20}/>
                  </div>
               </div>
            </div>
          </div>
        )}

        {view === 'login' && (
          <div className="max-w-md mx-auto py-12 animate-in slide-in-from-bottom duration-700">
            <div className="bg-white p-12 rounded-[4rem] shadow-2xl border border-gray-50 space-y-10">
              <div className="text-center space-y-3">
                <div className="w-20 h-20 bg-orange-50 text-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-5 rotate-3 shadow-inner">
                  <Lock size={36} strokeWidth={2.5}/>
                </div>
                <h2 className="text-3xl font-black tracking-tighter uppercase leading-none text-gray-900">Esnaf Paneli</h2>
                <p className="text-[10px] text-gray-400 font-black uppercase tracking-[0.2em]">Kadir Teknoloji | Dörtyol Petrol | Antik Kral</p>
              </div>
              <div className="space-y-4">
                <input type="text" placeholder="Dükkan Adı" className="w-full bg-gray-50 p-5 rounded-2xl border-none outline-none focus:ring-4 focus:ring-orange-500/10 font-bold" />
                <input type="password" placeholder="Şifre" className="w-full bg-gray-50 p-5 rounded-2xl border-none outline-none focus:ring-4 focus:ring-orange-500/10 font-bold" />
                <button className="w-full bg-gray-900 text-white py-5 rounded-2xl font-black text-lg shadow-xl hover:bg-orange-500 transition-all active:scale-95">GİRİŞ YAP</button>
              </div>
              <p className="text-center text-[10px] font-black text-gray-300 uppercase tracking-widest cursor-pointer hover:text-orange-500 transition-colors" onClick={() => setView('register')}>Kayıtlı Değil misiniz? Hemen Katılın</p>
            </div>
          </div>
        )}
      </main>

      {/* --- MOBİL ALT NAV (Instagram Style) --- */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-2xl border-t border-gray-100 px-8 py-6 flex items-center justify-between md:hidden shadow-[0_-20px_50px_rgba(0,0,0,0.05)] rounded-t-[3rem]">
        <button onClick={() => setView('home')} className={`p-2 transition-all ${view === 'home' ? 'text-orange-500 scale-125' : 'text-gray-300'}`}>
          <Home size={26} strokeWidth={3} />
        </button>
        <button onClick={() => setView('home')} className="p-2 text-gray-300">
          <UtensilsCrossed size={26} />
        </button>
        
        {/* Merkez Arama */}
        <div className="relative -mt-14 group">
          <div className="absolute -inset-4 bg-orange-500/20 rounded-full blur-2xl animate-pulse"></div>
          <div className="relative w-18 h-18 bg-orange-500 rounded-[2rem] flex items-center justify-center text-white shadow-2xl shadow-orange-500/30 border-4 border-white transition-transform active:scale-90" onClick={() => setView('home')}>
            <Search size={32} strokeWidth={3} />
          </div>
        </div>

        <button className="p-2 text-gray-300">
          <Heart size={26} />
        </button>
        <button onClick={() => setView('login')} className={`p-2 transition-all ${view === 'login' ? 'text-orange-500 scale-125' : 'text-gray-300'}`}>
          <User size={26} strokeWidth={3} />
        </button>
      </div>

      <footer className="hidden md:block py-20 bg-gray-50 mt-20 border-t border-gray-100">
         <div className="max-w-4xl mx-auto px-10 text-center space-y-6">
            <div className="flex justify-center items-center gap-2 mb-4 opacity-50">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white font-bold text-sm">D</div>
              <span className="font-black text-lg tracking-tighter uppercase">Dörtyol Çarşı</span>
            </div>
            <p className="text-gray-400 font-bold text-xs uppercase tracking-[0.3em]">Albayrax Dijital Ağ © 2026 | Dörtyol, Hatay</p>
         </div>
      </footer>
    </div>
  );
}
