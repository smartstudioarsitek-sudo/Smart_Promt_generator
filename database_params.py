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
    "Eksterior Cat Dinding (Wall Paint / Stucco)",
    "Kayu Solid (Timber / Wood Panels)",
    "Kaca dan Aluminium (Glass & Aluminium Facade)",
    "concrete, glass, and wood accents",
    "white marble and gold trim", 
    "exposed brick and steel",
    "sustainable bamboo and stone", 
    "reflective glass facade", 
    "weathered corten steel",
    "polished travertin stone",
    "exposed terracotta brick, raw concrete, and warm timber wood"
]

DB_SUASANA = [
    "Sunny Day", "Golden Hour (Sunset)", "Blue Hour (Twilight)", 
    "Foggy Morning", "Cinematic Night Lighting", "Rainy Cyberpunk Mood",
    "Overcast Soft Light", "Soft Morning Ambient Light"
]

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
# Sistem Metadata (Flagging) untuk menggantikan deteksi hardcode "[INT]"
DB_VIEW_FLAGS = {
    "[EXT] Eye Level (Human View)": {"is_interior": False},
    "[EXT] Drone / Bird's Eye View": {"is_interior": False},
    "[EXT] Worm's Eye View (Low Angle)": {"is_interior": False},
    "[INT] Eye Level (Human View)": {"is_interior": True},
    "[INT] Wide Angle Interior": {"is_interior": True},
    "[INT] Close-up Detail Shot": {"is_interior": True}
}
# Info: Jika nanti Anda ingin menghapus tulisan "[INT]" dan mengubahnya menjadi 
# "Tampilan Dalam Ruangan", Anda cukup mengubah teks di DB_VIEW dan key di kamus ini, 
# sistem tidak akan pernah rusak lagi.
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
    "Clean Photorealistic": "clean, no text, pure photography style",
    "Technical Concept": "architectural concept sheet style, mixed media, photorealistic render overlaid with hand-drawn technical annotations",
    "Blueprint / Wireframe": "blueprint style, white lines on blue background, technical drawing, wireframe structural view",
    "Watercolor Sketch": "watercolor painting style, soft edges, artistic architectural sketch, ink outline"
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

DB_CAMERA_MOTION = [
    "Static Shot with Micro-Dynamics (Kamera diam, hanya elemen alam yang bergerak)",
    "Slow Dolly-In (Kamera perlahan maju mendekati bangunan secara dramatis)",
    "Drone Tracking Shot (Kamera melayang perlahan mengikuti jalan/objek)",
    "Low-Angle Pan (Kamera mendongak dan menoleh perlahan menampakkan fasad megah)",
    "Rack Focus (Fokus berpindah dari daun di depan ke bangunan di belakang)"
]

DB_STORYTELLING_VIBE = [
    "Quiet Morning Routine (Burung beterbangan lambat, angin sepoi-sepoi menggerakkan daun, nuansa damai)",
    "Afternoon Busy Life (Orang-orang berjalan blur / motion blur, bayangan matahari bergeser perlahan)",
    "Rainy Melancholy (Rintik hujan jatuh ke genangan air, memantulkan cahaya lampu, angin bertiup sedang)",
    "Golden Hour Romance (Cahaya senja menyapu tekstur material, partikel debu melayang di udara, sangat sinematik)"
]

DB_ENGINE_VIDEO = [
    "Google Veo (Terbaik untuk Integrasi Gemini, Cinematic Motion & Native Audio)",
    "Kling 3.0 Omni (Terbaik untuk Multi-shot & Koherensi Spasial)",
    "Luma Dream Machine (Terbaik untuk Navigasi Ruang Interior via NeRF)",
    "OpenAI Sora 2 (Terbaik untuk Transisi Skala Besar)",
    "Runway Gen-4.5 (Terbaik untuk Dynamic Motion Control)"
]

DB_AI_CONTROL = [
    "Canny Edge Detection (Fokus pada garis luar fasad tegak lurus)",
    "Depth Map (Fokus pada kedalaman ruang dan volume massa)",
    "MLSD / Lineart (Fokus pada struktur wireframe arsitektural kaku)",
    "Normal Map (Fokus pada topologi permukaan dan relief fasad)",
    "Semantic Segmentation / Color Masking (Pemetaan material absolut)"
]
DB_PRESETS = {
    "Cyberpunk Skyscraper (Malam)": {
        "tipe": "Futuristic Skyscraper", "gaya": "Zaha Hadid Style", "material": "reflective glass facade",
        "suasana": "Cinematic Night Lighting", "cuaca": "Cinematic Cyberpunk Smog (Asap/Polusi Neon)",
        "view": "[EXT] Worm's Eye View (Low Angle)", "temp_warna": "RGB / Neon Accents (Cyberpunk, Futuristic)",
        "fixture_ext": "Architectural Facade Up-lighting", "teknik_cahaya": "Cinematic Volumetric Lighting (God Rays)",
        "tapak": "Dense Urban Infill (Perkotaan padat, diapit gedung lain)", "vegetasi": "None / Pure Hardscape (Tanpa tanaman, fokus pada material keras)",
        "rasio": "Portrait / Story (9:16)", "presentasi": "Clean Photorealistic", # Pastikan ini sesuai dengan key DB_PRESENTASI yang baru
        "skenario": "Standard Clear Architectural Shot", "engine": "Unreal Engine 5",
        "lensa_khusus": "14mm Ultra-Wide Rectilinear (Interior sempit terlihat megah)", "kamera_film": "Cinematic Anamorphic (Arri Alexa, flare lensa horizontal)",
        "weathering": "Subtle Weathering (Tanda pemakaian ringan, debu halus di sudut)"
    }
}

# === KAMUS TERJEMAHAN MATERIAL PBR (INDONESIA -> ENGLISH PBR LOGIC) ===
KAMUS_PBR = {
    # --- Beton ---
    "Beton Ekspos Halus": "Smooth architectural concrete, low roughness, soft specular reflection",
    "Beton Kasar / Bekisting": "Raw architectural concrete, high roughness, micro-displacement map, visible formwork tie-holes",
    "Beton Pracetak (Precast)": "Precast concrete panels, uniform texture, subtle edge chamfers, clean joints",
    
    # --- Kaca ---
    "Kaca Jernih": "Clear Architectural Glass, IOR 1.52, dielectric transmission, sharp specular",
    "Kaca Buram (Frosted)": "Frosted architectural glass, high roughness, IOR 1.45, blurred dielectric transmission",
    "Kaca Reflektif (Cermin)": "Highly reflective mirror glass, metallic workflow, sharp environmental reflections, IOR 2.0",
    "Kaca Berwarna (Tinted)": "Tinted architectural glass, subtle color absorption, dielectric transmission, IOR 1.52",
    
    # --- Kayu ---
    "Kayu Solid (Glossy)": "Polished solid timber, clear coat specular, visible wood grain normal map",
    "Kayu Natural (Matte)": "Natural raw wood timber, high roughness, diffuse scattering, prominent grain displacement",
    "Kayu Ulin / Eksterior": "Weathered ironwood, desaturated albedo, deep cracks normal map, matte finish",
    
    # --- Pasangan Bata & Batu ---
    "Bata Merah Natural": "Terracotta brickwork, matte albedo, pronounced bump map on mortar joints",
    "Bata Putih / Expose": "Painted white brickwork, subtle mortar depth, diffuse reflection, low specular",
    "Batu Andesit": "Rough Andesite Stone, natural displacement map, high frequency micro-bump, porous surface",
    "Batu Alam Palimanan": "Palimanan sandstone, warm albedo, high roughness, natural stratification bump map",
    
    # --- Logam (Metal) ---
    "Baja Struktural (Brushed)": "Brushed structural steel, metallic workflow, low albedo, anisotropic reflections, micro-scratches",
    "Aluminium Anodized": "Anodized aluminum frame, semi-rough metallic, uniform scatter, subtle edge highlights",
    "Baja Karat (Corten)": "Weathered Corten steel, deep orange-brown rust albedo, high roughness, patchy displacement",
    "Tembaga / Perunggu": "Patinated bronze/copper, metallic workflow, subtle green oxidation, variable roughness",
    
    # --- Pelapis Permukaan (Finishing) ---
    "Cat Eksterior (Putih/Warna)": "Clean exterior stucco paint, subtle noise texture, matte finish, soft global illumination scattering",
    "Marmer Polished": "Polished Marble, highly reflective, subtle clear coat specular, natural veining albedo",
    "Granit Flamed": "Flamed Granite paving, high roughness, crystalline micro-bump, diffuse scattering",
    "Keramik Matte": "Matte ceramic tiles, subtle grout lines, low specular, uniform albedo",
    "Keramik Glossy": "Glossy ceramic tiles, high specular, sharp reflections, clean grout normal map",
    
    # --- Lainnya ---
    "Aspal Jalan": "Rough asphalt road surface, high frequency noise displacement, low albedo, subtle specular on wet patches",
    "Rumput Sintetis": "Artificial turf grass, subsurface scattering, individual blade normal map, matte albedo",
    "Kustom (Ketik Manual)": "" # Opsi fleksibel
}

# Membuat daftar nama material dalam bahasa Indonesia untuk ditampilkan di Dropdown
LIST_MATERIAL_PBR = list(KAMUS_PBR.keys())
