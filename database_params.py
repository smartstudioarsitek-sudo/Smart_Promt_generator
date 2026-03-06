# database_params.py

DB_TIPE = [
    "Modern Minimalist House", "Grand Mosque (Masjid)", "Tropical Villa", 
    "Industrial Office", "Futuristic Skyscraper", "Bamboo Eco-Lodge",
    "Luxury Penthouse", "Cultural Center", "Parametric Pavilion",
    "Tropical Modern Townhouse"
]

DB_GAYA = [
    "Futuristic", "Contemporary", "Islamic Modern", "Biophilic/Green", 
    "Brutalist", "Zaha Hadid Style", "Parametric Design", 
    "Scandinavian (Japandi)", "Industrial",
    "Tropical Brutalism with Exposed Brick"
]

DB_MATERIAL = [
    "concrete, glass, and wood accents", "white marble and gold trim", 
    "exposed brick and steel", "sustainable bamboo and stone", 
    "reflective glass facade", "weathered corten steel",
    "polished travertin stone",
    "exposed terracotta brick, raw concrete, and warm timber wood"
]

DB_SUASANA = [
    "Sunny Day", "Golden Hour (Sunset)", "Blue Hour (Twilight)", 
    "Foggy Morning", "Cinematic Night Lighting", "Rainy Cyberpunk Mood",
    "Overcast Soft Light", "Soft Morning Ambient Light"
]

# --- DATABASE BARU UNTUK LOGIKA DINAMIS ---
DB_CUACA_SIANG = [
    "Clear Blue Sky (Cerah)", 
    "Scattered Clouds (Berawan Sebagian)", 
    "Morning Mist (Kabut Tipis Pagi)", 
    "Overcast (Mendung Soft Light)", 
    "Dramatic Storm Clouds (Awan Badai Dramatis)"
]

DB_CUACA_MALAM = [
    "Clear Starry Night (Malam Berbintang)", 
    "Heavy Low Fog (Kabut Tebal Bawah)", 
    "Rainy with Wet Puddles (Hujan & Genangan Air)", 
    "Cinematic Cyberpunk Smog (Asap/Polusi Neon)"
]

DB_VIEW = [
    "[EXT] Eye Level (Human View)", "[EXT] Drone / Bird's Eye View", "[EXT] Worm's Eye View (Low Angle)",
    "[INT] Eye Level (Human View)", "[INT] Wide Angle Interior", "[INT] Close-up Detail Shot"
]

DB_TEMP_WARNA = [
    "Auto (Berdasarkan Waktu/Suasana)",
    "2700K Warm White (Hangat, Intim, Mewah)",
    "3000K Soft White (Nyaman, Elegan)",
    "4000K Natural White (Bersih, Fokus, Modern)",
    "6000K Cool Daylight (Terang, Fungsional, Industrial)",
    "RGB / Neon Accents (Cyberpunk, Futuristic)"
]

DB_FIXTURE_INT = [
    "Tanpa Lampu Spesifik (Natural Light)",
    "Recessed LED Spotlights & Hidden Cove Lighting",
    "Luxury Crystal Chandelier & Warm Wall Sconces",
    "Industrial Pendant Lights & Track Lighting",
    "Minimalist Linear LED Suspended Lights",
    "Floor Lamps & Table Lamps with Soft Warm Glow"
]

DB_FIXTURE_EXT = [
    "Tanpa Lampu Spesifik (Natural Light)",
    "Architectural Facade Up-lighting",
    "Warm Bollard Garden Lights & Pathway LEDs",
    "Hidden LED Strip Under-glowing",
    "Warm Wall Sconces & Porch Pendants",
    "Dramatic Floodlights & Pool Underwater Lighting"
]

DB_TEKNIK_CAHAYA = [
    "Standard Global Illumination",
    "Realistic IES Light Profiles",
    "Cinematic Volumetric Lighting (God Rays)",
    "Soft Diffused Bounce Light",
    "High Contrast Chiaroscuro",
    "Luminous Bloom Effect"
]

DB_PRESENTASI = {
    "📸 Clean Photorealistic": "clean, no text, pure photography style",
    "📏 Technical Concept": "architectural concept sheet style, mixed media, photorealistic render overlaid with hand-drawn technical annotations",
    "📝 Blueprint / Wireframe": "blueprint style, white lines on blue background, technical drawing, wireframe structural view",
    "🎨 Watercolor Sketch": "watercolor painting style, soft edges, artistic architectural sketch, ink outline"
}

DB_SKENARIO = [
    "Standard Clear Architectural Shot",
    "Macro Foreground: Sharp focus on falling flower petals (Bokeh)",
    "Human Scale & Lifestyle: Featuring people on balcony",
    "Carport Focus: Luxury cars under concrete overhang"
]

DB_RASIO = {
    "Landscape (16:9)": "16:9",
    "Portrait / Story (9:16)": "9:16",
    "Square / Feed (1:1)": "1:1",
    "Classic Photo (4:3)": "4:3",
    "Ultra Wide (4:1)": "4:1" 
}

DB_ENGINE = ["Unreal Engine 5", "V-Ray", "Octane", "Corona", "Lumion"]

# --- TAMBAHAN FASE 2: MATERIAL & CINEMATOGRAPHY ---

DB_WEATHERING = [
    "Pristine & Brand New (Sangat Bersih/Baru)",
    "Subtle Weathering (Tanda pemakaian ringan, debu halus di sudut)",
    "Natural Patina & Aging (Oksidasi alami, lumut tipis di area lembap)",
    "Heavy Decay & Abandoned (Rusak, berkarat, cat terkelupas)"
]

DB_KAMERA_FILM = [
    "Digital Crisp (Sony A7R IV, tajam, modern, bersih)",
    "Cinematic Film Stock (Kodak Portra 400, warna hangat, butiran halus)",
    "Medium Format (Hasselblad, depth of field sangat detail & mewah)",
    "Cinematic Anamorphic (Arri Alexa, flare lensa horizontal)",
    "High Contrast Black & White (Leica Monochrom)"
]

DB_LENSA_KHUSUS = [
    "Auto (Sesuaikan otomatis dengan View)",
    "24mm Tilt-Shift Lens (Wajib untuk eksterior: Garis vertikal lurus tegap)",
    "14mm Ultra-Wide Rectilinear (Interior sempit terlihat megah)",
    "50mm Prime Lens (Fokus detail objek, minim distorsi ruang)",
    "85mm Macro f/1.4 (Bokeh, fokus sangat dekat pada tekstur material)",
    "Drone Hasselblad 24mm eq (Khusus Aerial/Bird Eye View)"
]
# --- TAMBAHAN AKHIR FASE 2: TAPAK & VEGETASI ---

DB_TAPAK = [
    "Dense Urban Infill (Perkotaan padat, diapit gedung lain)",
    "Suburban Neighborhood (Perumahan asri, jalan aspal)",
    "Cliffside Ocean View (Tebing berbatu menghadap laut)",
    "Sloping Forest Terrain (Lereng bukit di dalam hutan)",
    "Minimalist Concrete Plaza (Alun-alun beton / Hardscape bersih)",
    "Desert / Arid Environment (Gurun pasir atau tanah kering)"
]

DB_VEGETASI = [
    "Lush Tropical (Palem, Monstera, Pakis, rimbun hijau)",
    "Zen Japanese Garden (Bonsai, Maple, Bambu, kerikil putih)",
    "Alpine / Pine Forest (Pohon Pinus, Cemara, nuansa dingin)",
    "Minimalist Manicured Lawn (Rumput potong rapi, semak kotak)",
    "Arid / Desert (Kaktus, Sukulen, Agave, tanpa rumput)",
    "None / Pure Hardscape (Tanpa tanaman, fokus pada material keras)"
]
# --- TAMBAHAN FASE 3: ENTERPRISE PRESETS ---
DB_PRESETS = {
    "Pilih Preset Bawaan...": None,
    "🏢 Cyberpunk Skyscraper (Malam)": {
        "tipe": "Futuristic Skyscraper", "gaya": "Zaha Hadid Style", "material": "reflective glass facade",
        "suasana": "Cinematic Night Lighting", "cuaca": "Cinematic Cyberpunk Smog (Asap/Polusi Neon)",
        "view": "[EXT] Worm's Eye View (Low Angle)", "temp_warna": "RGB / Neon Accents (Cyberpunk, Futuristic)",
        "fixture_ext": "Architectural Facade Up-lighting", "teknik_cahaya": "Cinematic Volumetric Lighting (God Rays)",
        "tapak": "Dense Urban Infill (Perkotaan padat, diapit gedung lain)", "vegetasi": "None / Pure Hardscape (Tanpa tanaman, fokus pada material keras)",
        "rasio": "Portrait / Story (9:16)", "presentasi": "📸 Clean Photorealistic",
        "skenario": "Standard Clear Architectural Shot", "engine": "Unreal Engine 5",
        "lensa_khusus": "14mm Ultra-Wide Rectilinear (Interior sempit terlihat megah)", "kamera_film": "Cinematic Anamorphic (Arri Alexa, flare lensa horizontal)",
        "weathering": "Subtle Weathering (Tanda pemakaian ringan, debu halus di sudut)"
    },
    "🌴 Tropical Luxury Villa (Senja)": {
        "tipe": "Tropical Villa", "gaya": "Biophilic/Green", "material": "sustainable bamboo and stone",
        "suasana": "Golden Hour (Sunset)", "cuaca": "Clear Blue Sky (Cerah)",
        "view": "[EXT] Eye Level (Human View)", "temp_warna": "3000K Soft White (Nyaman, Elegan)",
        "fixture_ext": "Warm Bollard Garden Lights & Pathway LEDs", "teknik_cahaya": "Soft Diffused Bounce Light",
        "tapak": "Cliffside Ocean View (Tebing berbatu menghadap laut)", "vegetasi": "Lush Tropical (Palem, Monstera, Pakis, rimbun hijau)",
        "rasio": "Landscape (16:9)", "presentasi": "📸 Clean Photorealistic",
        "skenario": "Standard Clear Architectural Shot", "engine": "Corona",
        "lensa_khusus": "50mm Prime Lens (Fokus detail objek, minim distorsi ruang)", "kamera_film": "Medium Format (Hasselblad, depth of field sangat detail & mewah)",
        "weathering": "Natural Patina & Aging (Oksidasi alami, lumut tipis di area lembap)"
    }
}
