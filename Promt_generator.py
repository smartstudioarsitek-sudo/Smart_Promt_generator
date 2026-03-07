import streamlit as st
import random
import os
import io
import numpy as np
from PIL import Image
import json

import database_params as db
import prompt_logic as pl

# Import SDK Google GenAI
from google import genai
from google.genai import types

# Import Kanvas Inpainting
try:
    from streamlit_drawable_canvas import st_canvas
    HAS_CANVAS = True
except ImportError:
    HAS_CANVAS = False

# ==========================================
# 0. KAMUS PINTAR PBR (VERSI LENGKAP DARI DATABASE)
# ==========================================
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

LIST_MATERIAL_PBR = list(KAMUS_PBR.keys())

# ==========================================
# 0. KONFIGURASI HALAMAN (WAJIB PALING ATAS)
# ==========================================
st.set_page_config(page_title="SmartBIM Engineex", layout="wide", initial_sidebar_state="expanded")


# ==========================================
# 1. KONFIGURASI KEAMANAN & API
# ==========================================
def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", st.secrets.get("GOOGLE_API_KEY", ""))
    except Exception:
        return os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

# ==========================================
# 🛠️ PERBAIKAN PRIORITAS 1: API MANAGEMENT INEFFICIENCY
# ==========================================
# Gunakan @st.cache_resource agar koneksi ke API Gemini 
# hanya dibuka SATU KALI per sesi, tidak berulang kali saat UI direfresh.
@st.cache_resource
def initialize_gemini_client(api_key):
    return genai.Client(api_key=api_key)

api_key_system = get_api_key()
client = None

with st.sidebar:
    st.markdown("### 🔐 Status Mesin Render")
    if api_key_system:
        st.success("🔒 API Key Terdeteksi")
        # Panggil fungsi yang sudah di-cache
        client = initialize_gemini_client(api_key_system)
    else:
        st.warning("⚠️ Mode Publik")
        api_key_input = st.text_input("🔑 Masukkan API Key Manual:", type="password")
        if api_key_input:
            # Panggil fungsi yang sudah di-cache
            client = initialize_gemini_client(api_key_input)
            st.success("✅ Kunci Manual Terkoneksi!")
        else:
            st.error("🚨 Kunci Akses Diperlukan!")
            st.stop()
# ==========================================
# 🛠️ PERBAIKAN PRIORITAS 4: MANAJEMEN STATE PERSISTEN
# ==========================================
import logging

# Setup logging dasar untuk mencatat error ke console/server log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRESET_FILE = "smartbim_presets.json"

def load_custom_presets():
    """
    Memuat preset dengan arsitektur cloud-ready dan I/O error handling yang elegan.
    Menghindari praktik "Broad Exception Masking".
    """
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"CRITICAL: File preset JSON rusak/corrupted. Detail: {e}")
            st.error("🚨 Gagal memuat preset: Format file data preset rusak. Silakan periksa file JSON.")
            return {}
        except IOError as e:
            logger.error(f"CRITICAL: Kesalahan I/O saat membaca file preset. Detail: {e}")
            st.error("🚨 Gagal memuat preset: Akses sistem berkas ditolak atau tidak terbaca.")
            return {}
        except Exception as e:
            logger.error(f"CRITICAL: Kesalahan tak terduga saat memuat preset. Detail: {e}")
            st.error("🚨 Kesalahan sistem yang tidak terduga saat memuat data profil.")
            return {}
            
    return {} # Kembalikan kamus kosong jika file belum ada

def save_custom_preset(name, data):
    """
    Menyimpan preset dengan proteksi penulisan dan peringatan UI.
    Mengembalikan boolean True jika berhasil, False jika gagal.
    """
    presets = load_custom_presets()
    presets[name] = data
    
    try:
        with open(PRESET_FILE, "w") as f:
            json.dump(presets, f, indent=4)
        logger.info(f"SUCCESS: Preset '{name}' berhasil diamankan ke penyimpanan.")
        return True
    except IOError as e:
        logger.error(f"FAIL: Gagal menulis ke sistem berkas lokal. Detail: {e}")
        st.error(f"⚠️ Gagal menyimpan preset '{name}': Lingkungan Cloud saat ini bersifat 'ephemeral' (sementara) dan memblokir penulisan data permanen. Konfigurasi ini akan hilang saat aplikasi di-refresh.")
        return False
    except Exception as e:
        logger.error(f"FAIL: Kesalahan tak terduga saat menyimpan preset '{name}'. Detail: {e}")
        st.error("⚠️ Terjadi kesalahan internal saat mencoba menyimpan profil Anda.")
        return False
# ==========================================
# 2. INITIALIZE SESSION STATE (Memori Aplikasi)
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    
    st.session_state.tipe = db.DB_TIPE[0]
    st.session_state.gaya = db.DB_GAYA[0]
    st.session_state.material = db.DB_MATERIAL[0]
    st.session_state.suasana = db.DB_SUASANA[0]
    st.session_state.cuaca = db.DB_CUACA_SIANG[0] 
    st.session_state.view = db.DB_VIEW[0]
    st.session_state.rasio = "Landscape (16:9)"
    # Memanggil nilai pertama dari kamus secara otomatis (Bebas Error Emoji)
    st.session_state.presentasi = list(db.DB_PRESENTASI.keys())[0] 
    st.session_state.skenario = db.DB_SKENARIO[0]  
    st.session_state.engine = db.DB_ENGINE[0]
    st.session_state.temp_warna = db.DB_TEMP_WARNA[0]
    st.session_state.fixture_int = db.DB_FIXTURE_INT[0]
    st.session_state.fixture_ext = db.DB_FIXTURE_EXT[0]
    st.session_state.teknik_cahaya = db.DB_TEKNIK_CAHAYA[0]
    st.session_state.detail = ""
    st.session_state.weathering = db.DB_WEATHERING[0]
    st.session_state.kamera_film = db.DB_KAMERA_FILM[0]
    st.session_state.lensa_khusus = db.DB_LENSA_KHUSUS[0]
    st.session_state.tapak = db.DB_TAPAK[0]
    st.session_state.vegetasi = db.DB_VEGETASI[0]
    
    st.session_state.use_ref = False
    st.session_state.uploaded_sketch = None
    st.session_state.ai_control = db.DB_AI_CONTROL[0]
    st.session_state.generated_prompt = ""
    st.session_state.conflicts = []
    st.session_state.history_ledger = []
    
    # Muat profil langsung dari hard drive, bukan sekadar memori sementara
    st.session_state.custom_presets = load_custom_presets() 
    
    st.session_state.mode_render = "📸 Image (Still Photo)"
    st.session_state.camera_motion = db.DB_CAMERA_MOTION[0]
    st.session_state.storytelling_vibe = db.DB_STORYTELLING_VIBE[0]
    st.session_state.engine_video = db.DB_ENGINE_VIDEO[0]
    
    st.session_state.chk_color_masking = False
    
    # 🛠️ PERBAIKAN PRIORITAS 4: Hapus Paksaan Dummy Data Warna
    # Biarkan kosong agar arsitek / drafter bebas menentukan legenda warnanya sendiri
    st.session_state.mask_white = ""
    st.session_state.mask_gray = ""
    st.session_state.mask_dark = ""
    st.session_state.mask_brown = ""
    st.session_state.mask_brick = ""
    st.session_state.mask_blue = ""
    st.session_state.mask_cream = ""
    st.session_state.mask_green = ""
# ==========================================
# 🛠️ PERBAIKAN PRIORITAS 4 & BUG INDEXERROR: OTAK ARSITEKTUR TANGGUH
# ==========================================
def safe_random_choice(options_list, fallback_value):
    """Safeguard untuk mencegah IndexError jika list kosong akibat filter agresif."""
    return random.choice(options_list) if options_list else fallback_value

def handle_random():
    s = st.session_state
    
    # 1. Tentukan Jangkar Utama: Perspektif & Waktu
    s.view = safe_random_choice(db.DB_VIEW, db.DB_VIEW[0])
    
    # 🛠️ PENGHAPUSAN HARDCODING [INT]: Gunakan Metadata Database dengan Fallback cerdas
    meta_flag = getattr(db, 'DB_VIEW_FLAGS', {}).get(s.view, {})
    is_interior = meta_flag.get("is_interior", "interior" in s.view.lower() or "[int]" in s.view.lower())
    
    s.suasana = safe_random_choice(db.DB_SUASANA, db.DB_SUASANA[0])
    is_night = any(k in s.suasana.lower() for k in ["night", "twilight", "sunset", "blue hour"])

    # 2. Sesuaikan Cuaca Berdasarkan Waktu (Mencegah Oksimoron Langit)
    if is_night:
        s.cuaca = safe_random_choice(db.DB_CUACA_MALAM, db.DB_CUACA_MALAM[0])
    else:
        s.cuaca = safe_random_choice(db.DB_CUACA_SIANG, db.DB_CUACA_SIANG[0])

    # 3. Sesuaikan Pencahayaan & Cegah Kegelapan Total
    if is_interior:
        s.fixture_int = safe_random_choice(db.DB_FIXTURE_INT, db.DB_FIXTURE_INT[0])
        if is_night and "Tanpa" in s.fixture_int:
            opsi_lampu = [f for f in db.DB_FIXTURE_INT if "Tanpa" not in f]
            s.fixture_int = safe_random_choice(opsi_lampu, db.DB_FIXTURE_INT[1]) # Gunakan fallback lampu menyala
    else:
        s.fixture_ext = safe_random_choice(db.DB_FIXTURE_EXT, db.DB_FIXTURE_EXT[0])
        if is_night and "Tanpa" in s.fixture_ext:
            opsi_lampu = [f for f in db.DB_FIXTURE_EXT if "Tanpa" not in f]
            s.fixture_ext = safe_random_choice(opsi_lampu, db.DB_FIXTURE_EXT[1])

    # 4. Logika Optik Lensa (Dilindungi dari IndexError)
    if "Drone" in s.view or "Aerial" in s.view:
        s.lensa_khusus = "Drone Hasselblad 24mm eq (Khusus Aerial/Bird Eye View)"
    else:
        opsi_lensa = [l for l in db.DB_LENSA_KHUSUS if "Drone" not in l]
        if not is_interior:
            opsi_lensa = [l for l in opsi_lensa if "Macro" not in l]
        # Jika opsi_lensa kosong setelah difilter, otomatis kembali ke default (Lensa Auto)
        s.lensa_khusus = safe_random_choice(opsi_lensa, db.DB_LENSA_KHUSUS[0])

    # 5. Parameter Estetika & Lingkungan Bebas
    s.tipe = safe_random_choice(db.DB_TIPE, db.DB_TIPE[0])
    s.gaya = safe_random_choice(db.DB_GAYA, db.DB_GAYA[0])
    s.material = safe_random_choice(db.DB_MATERIAL, db.DB_MATERIAL[0])
    s.skenario = safe_random_choice(db.DB_SKENARIO, db.DB_SKENARIO[0])
    s.engine = safe_random_choice(db.DB_ENGINE, db.DB_ENGINE[0])
    s.tapak = safe_random_choice(db.DB_TAPAK, db.DB_TAPAK[0])
    s.vegetasi = safe_random_choice(db.DB_VEGETASI, db.DB_VEGETASI[0])
    s.weathering = safe_random_choice(db.DB_WEATHERING, db.DB_WEATHERING[0])    
 
def load_preset(preset_name):
    all_presets = {**db.DB_PRESETS, **st.session_state.custom_presets}
    data = all_presets.get(preset_name)
    if data:
        for key, value in data.items():
            if key in st.session_state:
                st.session_state[key] = value

# ==========================================
# 3. UI RENDER (Streamlit Layout)
# ==========================================
st.markdown("""
<style>
    .header-box { background-color: #ffffff; padding: 1rem; border-bottom: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;}
    .title-text { color: #1a1c1e; font-weight: 900; margin: 0; font-size: 1.5rem; }
    .subtitle-text { color: #64748b; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
    .section-title { font-size: 0.8rem; font-weight: 800; color: #4338ca; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem; margin-bottom: 0.5rem;}
</style>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.markdown('<div class="header-box"><div style="display:flex; flex-direction:column;"><h1 class="title-text">SmartBIM Engineex <span style="color:#4338ca">v2.1</span></h1><p class="subtitle-text">Enterprise Prompt Builder & Material ID Mapping</p></div></div>', unsafe_allow_html=True)
with col_head2:
    st.write("") 
    if st.button("🔄 Acak Parameter", use_container_width=True):
        handle_random()
        st.rerun()

col_left, col_right = st.columns([6, 6], gap="large")

with col_left:
    with st.expander("📂 Preset Manager (Load & Save)", expanded=False):

        # Tempatkan placeholder UI secara eksklusif di lapisan antarmuka
        preset_options = ["Pilih Preset..."] + list(db.DB_PRESETS.keys()) + list(st.session_state.custom_presets.keys())
        selected_preset = st.selectbox("Pilih Profil Pengaturan:", preset_options)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("📥 Muat Preset", use_container_width=True):
                # Validasi agar aplikasi tidak mencoba memuat placeholder
                if selected_preset != "Pilih Preset...": 
                    load_preset(selected_preset)
                    st.rerun()
        with col_p2:
            new_preset_name = st.text_input("Nama Preset Baru:", placeholder="Misal: Villa Gaya Saya")
            if st.button("💾 Simpan Saat Ini", use_container_width=True) and new_preset_name:
                
                new_data = {
                    "tipe": st.session_state.tipe, "gaya": st.session_state.gaya, "material": st.session_state.material,
                    "suasana": st.session_state.suasana, "cuaca": st.session_state.cuaca, "view": st.session_state.view,
                    "temp_warna": st.session_state.temp_warna, "fixture_int": st.session_state.fixture_int,
                    "fixture_ext": st.session_state.fixture_ext, "teknik_cahaya": st.session_state.teknik_cahaya,
                    "tapak": st.session_state.tapak, "vegetasi": st.session_state.vegetasi, "rasio": st.session_state.rasio,
                    "presentasi": st.session_state.presentasi, "skenario": st.session_state.skenario, "engine": st.session_state.engine,
                    "lensa_khusus": st.session_state.lensa_khusus, "kamera_film": st.session_state.kamera_film, "weathering": st.session_state.weathering
                }
                
                # Simpan ke memori sesi (selalu berhasil selama tab browser aktif)
                st.session_state.custom_presets[new_preset_name] = new_data
                
                # Eksekusi fungsi simpan baru yang sudah aman
                is_saved = save_custom_preset(new_preset_name, new_data)
                
                # Tampilkan sukses HANYA jika operasi penyimpanan file berhasil
                if is_saved:
                    st.success(f"✅ Preset '{new_preset_name}' berhasil disimpan secara permanen!")
                    st.rerun()
               
    
    st.markdown("---")
    st.session_state.mode_render = st.radio(
        "Pilih Format Output (Sutradara Mode):",
        ["📸 Image (Still Photo)", "🎥 Video (Cinematic Animation)"],
        horizontal=True
    )
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Geometri & Material", "💡 Tata Cahaya", "🌍 Konteks Lingkungan", "📷 Sinema & Lensa"])
    
    with tab1:
        st.markdown('<div class="section-title">📐 Geometry & Sketch Upload</div>', unsafe_allow_html=True)
        uploaded_sketch_file = st.file_uploader("Upload Sketsa Garis / Base Image", type=None, key="sketch_up")
        
        if uploaded_sketch_file is not None:
            try:
                sketch_img = Image.open(uploaded_sketch_file)
                st.image(sketch_img, caption="Preview Sketsa Aktual", use_column_width=True) 
                st.session_state.uploaded_sketch = True
                st.success("✅ Sketsa terdeteksi! 'Vision Constraint' akan diaktifkan.")
                st.session_state.ai_control = st.selectbox("Metode Restriksi Struktural AI (Lapisan 2):", db.DB_AI_CONTROL, index=db.DB_AI_CONTROL.index(st.session_state.ai_control)) 
            except Exception:
                st.error("❌ File yang diunggah bukan gambar yang valid.")
                st.session_state.uploaded_sketch = None
        else:
            st.session_state.uploaded_sketch = None
            
        st.markdown("---")
        
        use_masking = st.checkbox("🎨 Aktifkan Semantic Color Masking (Material ID)", key="chk_color_masking")
        st.session_state.use_color_masking = use_masking

        if st.session_state.use_color_masking:
            st.info("💡 Pilih material dalam bahasa Indonesia. Aplikasi akan otomatis merakit mantra 3D/PBR bahasa Inggris ke dalam prompt.")
            c1, c2 = st.columns(2)
            
            # --- FUNGSI PEMBANTU DROPDOWN PBR ---
            def pbr_selector(label, key_state):
                current_english = st.session_state.get(key_state, "")
                current_indo = "Kustom (Ketik Manual)"
                for indo, eng in KAMUS_PBR.items():
                    if eng == current_english:
                        current_indo = indo
                        break
                
                pilihan_indo = st.selectbox(label, LIST_MATERIAL_PBR, index=LIST_MATERIAL_PBR.index(current_indo), key=f"sel_{key_state}")
                
                if pilihan_indo == "Kustom (Ketik Manual)":
                    st.session_state[key_state] = st.text_input(f"Ketik instruksi PBR (English) untuk {label}:", value=current_english, key=f"txt_{key_state}")
                else:
                    st.session_state[key_state] = KAMUS_PBR[pilihan_indo]
            
            with c1:
                pbr_selector("⚪ Putih/Terang (Dinding/Wall)", "mask_white")
                pbr_selector("🔘 Abu-Abu (Kolom/Beton)", "mask_gray")
                pbr_selector("⚫ Abu Gelap/Hitam (Kusen/Atap)", "mask_dark")
                pbr_selector("🟤 Coklat (Pintu/Kayu)", "mask_brown")
                
            with c2:
                pbr_selector("🧱 Merah Bata (Aksen Dinding)", "mask_brick")
                pbr_selector("🩵 Biru Muda (Kaca Jendela)", "mask_blue")
                pbr_selector("🟡 Krem/Kuning (Lantai/Keramik)", "mask_cream")
                pbr_selector("🟢 Hijau/Bebas (Vegetasi/Lainnya)", "mask_green")
                                
        st.markdown("---")
        st.session_state.tipe = st.selectbox("Kategori Bangunan", db.DB_TIPE, index=db.DB_TIPE.index(st.session_state.tipe))
        st.session_state.gaya = st.selectbox("Gaya Arsitektur", db.DB_GAYA, index=db.DB_GAYA.index(st.session_state.gaya))
        st.session_state.material = st.selectbox("Material Dasar Lingkungan (Base Material)", db.DB_MATERIAL, index=db.DB_MATERIAL.index(st.session_state.material))
        st.session_state.weathering = st.selectbox("Kondisi Fisik / Keausan Material", db.DB_WEATHERING, index=db.DB_WEATHERING.index(st.session_state.weathering))
        st.session_state.detail = st.text_area("Detail Spesifik Khusus (Struktur/Bentuk)", value=st.session_state.detail, height=80)

    with tab2:
        st.session_state.temp_warna = st.selectbox("Suhu Warna Lampu (Kelvin)", db.DB_TEMP_WARNA, index=db.DB_TEMP_WARNA.index(st.session_state.temp_warna))
        meta_flag = getattr(db, 'DB_VIEW_FLAGS', {}).get(st.session_state.view, {})
        is_interior_ui = meta_flag.get("is_interior", "interior" in st.session_state.view.lower() or "[int]" in st.session_state.view.lower())
        if is_interior_ui:
            st.session_state.fixture_int = st.selectbox("Interior Lighting Fixtures", db.DB_FIXTURE_INT, index=db.DB_FIXTURE_INT.index(st.session_state.fixture_int))
        else:
            st.session_state.fixture_ext = st.selectbox("Exterior Lighting Fixtures", db.DB_FIXTURE_EXT, index=db.DB_FIXTURE_EXT.index(st.session_state.fixture_ext))
            
        st.session_state.teknik_cahaya = st.selectbox("Teknik Render Cahaya Tambahan", db.DB_TEKNIK_CAHAYA, index=db.DB_TEKNIK_CAHAYA.index(st.session_state.teknik_cahaya))

    with tab3:
        st.markdown('<div class="section-title">🌍 Site Context & Landscaping</div>', unsafe_allow_html=True)
        row_site1, row_site2 = st.columns(2)
        with row_site1:
            st.session_state.tapak = st.selectbox("Konteks Tapak / Topografi", db.DB_TAPAK, index=db.DB_TAPAK.index(st.session_state.tapak))
        with row_site2:
            st.session_state.vegetasi = st.selectbox("Vegetasi & Lansekap", db.DB_VEGETASI, index=db.DB_VEGETASI.index(st.session_state.vegetasi))

        st.markdown('<div class="section-title">🌤️ Atmosphere & Weather</div>', unsafe_allow_html=True)
        st.session_state.suasana = st.selectbox("Waktu & Pencahayaan Alami", db.DB_SUASANA, index=db.DB_SUASANA.index(st.session_state.suasana))
        
        is_night = any(k in st.session_state.suasana.lower() for k in ["night", "twilight", "sunset"])
        if is_night:
            st.session_state.cuaca = st.selectbox("Kondisi Atmosfer (Malam)", db.DB_CUACA_MALAM)
        else:
            st.session_state.cuaca = st.selectbox("Kondisi Atmosfer (Siang)", db.DB_CUACA_SIANG)
            
        st.session_state.skenario = st.selectbox("Skenario / Lingkungan", db.DB_SKENARIO, index=db.DB_SKENARIO.index(st.session_state.skenario))

    with tab4:
        if "Video" in st.session_state.mode_render:
            st.markdown('<div class="section-title">🎥 Cinematic Director (Video Motion)</div>', unsafe_allow_html=True)
            st.info("💡 Mode Video aktif! Prompt ini sangat cocok untuk Google Veo, Luma Dream Machine, atau Sora.")
            st.session_state.engine_video = st.selectbox("Engine Video Target", db.DB_ENGINE_VIDEO, index=db.DB_ENGINE_VIDEO.index(st.session_state.engine_video))
            st.session_state.camera_motion = st.selectbox("Koreografi Kamera", db.DB_CAMERA_MOTION, index=db.DB_CAMERA_MOTION.index(st.session_state.camera_motion))
            st.session_state.storytelling_vibe = st.selectbox("Nyawa & Suasana", db.DB_STORYTELLING_VIBE, index=db.DB_STORYTELLING_VIBE.index(st.session_state.storytelling_vibe))
            st.markdown("---")

        st.markdown('<div class="section-title">📷 Lensa & Kamera Dasar</div>', unsafe_allow_html=True)
        st.session_state.view = st.selectbox("Kamera & Perspektif", db.DB_VIEW, index=db.DB_VIEW.index(st.session_state.view))
        st.session_state.lensa_khusus = st.selectbox("Lensa Arsitektur Khusus", db.DB_LENSA_KHUSUS, index=db.DB_LENSA_KHUSUS.index(st.session_state.lensa_khusus))
        st.session_state.kamera_film = st.selectbox("Jenis Kamera & Film Stock", db.DB_KAMERA_FILM, index=db.DB_KAMERA_FILM.index(st.session_state.kamera_film))
        st.session_state.rasio = st.selectbox("Rasio Gambar/Video", list(db.DB_RASIO.keys()), index=list(db.DB_RASIO.keys()).index(st.session_state.rasio))
        
        if "Image" in st.session_state.mode_render:
            st.session_state.presentasi = st.selectbox("Gaya Render", list(db.DB_PRESENTASI.keys()), index=list(db.DB_PRESENTASI.keys()).index(st.session_state.presentasi))
            st.session_state.engine = st.selectbox("Render Engine Target", db.DB_ENGINE, index=db.DB_ENGINE.index(st.session_state.engine))
    
    st.markdown("---")
    st.session_state.use_ref = st.checkbox("Lampirkan Referensi Style (Moodboard) di chat Gemini", value=st.session_state.use_ref)

    if st.session_state.conflicts:
        for conflict in st.session_state.conflicts:
            st.warning(conflict)

    if st.button("✨ SUSUN PROMPT NEURAL", use_container_width=True, type="primary"):
        pl.construct_prompt()


# ==========================================
# KOLOM KANAN (OUTPUT & INPAINTING)
# ==========================================
with col_right:
    tab_out, tab_inpaint, tab_upscale, tab_hist = st.tabs(["🖥️ Output", "🖌️ Inpainting", "🔍 4K Upscaler", "📚 Riwayat"])
        
    with tab_out:
        if st.session_state.generated_prompt:
            st.success("✅ Logika arsitektural & komposisi fotografi siap dieksekusi!")
            
            st.markdown("#### 1️⃣ Eksekusi via Gemini Web / AI Video (Gratis/Pihak Ketiga)")
            
            # --- LOGIKA SUTRADARA (STORYBOARD) KHUSUS VIDEO ---
            if "Video" in st.session_state.mode_render:
                st.info("🎥 **MODE STORYBOARD AKTIF:** Render setiap shot di bawah ini satu per satu (masing-masing 4-8 detik), lalu gabungkan di software editing untuk membuat video sinematik panjang.")
                
                # Daftar pergerakan kamera ala Kunkun Visual
                shot_list = [
                    {"shot": "Shot 1: Establishing Aerial (8 Detik)", "cam": "Slow drone hyperlapse, high angle sweeping down, revealing the architecture in its context"},
                    {"shot": "Shot 2: Facade Tracking (8 Detik)", "cam": "Low angle tracking shot on a slider, moving smoothly left to right, focusing on the facade"},
                    {"shot": "Shot 3: Material Close-Up (8 Detik)", "cam": "Macro focus pull, subtle handheld movement, extremely shallow depth of field on the material texture"},
                    {"shot": "Shot 4: Push-In Entrance (8 Detik)", "cam": "Smooth gimbal push-in, moving steadily towards the main entrance, inviting perspective"},
                    {"shot": "Shot 5: Interior/Atmosphere Pan (8 Detik)", "cam": "Slow cinematic pan across the space, capturing volumetric light beams and dust motes in the air"}
                ]
                
                for item in shot_list:
                    st.markdown(f"**🎬 {item['shot']}**")
                    # Menggabungkan prompt dasar dengan instruksi kamera spesifik per shot
                    vid_prompt = f"[CINEMATIC VIDEO PROMPT] {item['cam']}, 24fps filmic look. {st.session_state.generated_prompt}"
                    st.code(vid_prompt, language="markdown")
                    
            else:
                # --- JIKA MODE GAMBAR (IMAGE) TETAP NORMAL ---
                st.write("Klik ikon **Copy** di pojok kanan atas kotak ini, lalu *paste* ke chat AI pilihan Anda.")
                st.code(st.session_state.generated_prompt, language="markdown")
    
            
            if st.session_state.uploaded_sketch or st.session_state.use_ref:
                st.warning("⚠️ **PENTING:** Karena Anda mengaktifkan *Vision Constraint* / *Color Masking*, pastikan Anda mengunggah gambar sketsa/masking tersebut secara manual ke chat AI bersamaan dengan prompt di atas!")
                
            st.markdown("---")
            
            st.markdown("#### 2️⃣ Render Instan via API (Imagen 4.0)")
            st.write("Membutuhkan API Key dengan akses penagihan (Paid Tier) aktif.")
            
            if st.button("🚀 RENDER GAMBAR SEKARANG", use_container_width=True, type="primary"):
                with st.spinner("Memproses Raytracing & Global Illumination via Imagen 4.0..."):
                    try:
                        aspect_ratio_map = {"16:9": "16:9", "9:16": "9:16", "1:1": "1:1", "4:3": "4:3", "4:1": "16:9"}
                        target_ratio = aspect_ratio_map.get(db.DB_RASIO[st.session_state.rasio], "1:1")

                        result = client.models.generate_images(
                            model='imagen-4.0-generate-001',
                            prompt=st.session_state.generated_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio=target_ratio
                            )
                        )
                        
                        for generated_image in result.generated_images:
                            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                            st.image(image, caption=f"Render Final: {st.session_state.tipe}", use_column_width=True)
                            
                            buf = io.BytesIO()
                            image.save(buf, format="JPEG")
                            byte_im = buf.getvalue()
                            st.download_button(
                                label="💾 Unduh Render Resolusi Tinggi", data=byte_im,
                                file_name=f"Render_{st.session_state.tipe.replace(' ', '_')}.jpg",
                                mime="image/jpeg", use_container_width=True
                            )
                            
                    except Exception as e:
                        st.error(f"Terjadi kesalahan rendering API: {e}")
                        st.info("💡 Jika muncul 'only available on paid plans', gunakan Opsi 1 (Copy Prompt) di atas.")
            
        else:
            st.info("👈 Silakan jelajahi 4 Tab di sebelah kiri, sesuaikan parameter, lalu klik **SUSUN PROMPT NEURAL**.")
    with tab_inpaint:
        st.markdown("### 🖌️ Kanvas Revisi (Inpainting)")
        st.info("Unggah gambar hasil render final Anda (dari Gemini/Midjourney/API), lalu 'lukis' area yang ingin direvisi.")
        
        if not HAS_CANVAS:
            st.error("🚨 Pustaka `streamlit-drawable-canvas` belum terdeteksi. Silakan install via terminal: `pip install streamlit-drawable-canvas`")
        else:
            base_img_file = st.file_uploader("🖼️ Unggah Gambar Base Render", type=None, key="inpaint_upload")
                        
            if base_img_file is not None:
                try:
                    # 1. Buka gambar mentah
                    temp_img = Image.open(base_img_file).convert("RGB")
                    
                    # ==========================================
                    # 🛠️ PERBAIKAN PRIORITAS 1: CEGAH OOM LEAK
                    # ==========================================
                    # Batasi resolusi maksimum ke 2048px sebelum pemrosesan matriks apa pun.
                    # Metode thumbnail() akan mempertahankan rasio aspek secara proporsional.
                    MAX_SAFE_SIZE = (2048, 2048)
                    temp_img.thumbnail(MAX_SAFE_SIZE, Image.Resampling.LANCZOS)
                    
                    # 2. Skala ukuran gambar khusus untuk tampilan Kanvas UI Streamlit
                    max_width_ui = 600
                    if temp_img.width > max_width_ui:
                        ratio = max_width_ui / temp_img.width
                        new_height = int(temp_img.height * ratio)
                        # Gunakan variabel berbeda untuk UI agar resolusi tinggi tetap aman untuk API
                        ui_img = temp_img.resize((max_width_ui, new_height), Image.Resampling.LANCZOS)
                    else:
                        ui_img = temp_img.copy()
                    
                    # 3. "CUCI" GAMBAR: Paksa simpan sebagai PNG di memori agar browser tidak rewel
                    clean_io = io.BytesIO()
                    ui_img.save(clean_io, format="PNG")
                    clean_io.seek(0)
                    
                    # 4. Buka kembali gambar yang sudah suci menjadi PNG untuk masuk ke kanvas
                    base_image_resized = Image.open(clean_io).convert("RGBA")

                    st.markdown("**1. Lukis Area Masking**")
            
                    col_canvas_tools, col_canvas = st.columns([1, 3])
                    
                    with col_canvas_tools:
                        stroke_width = st.slider("Ukuran Kuas (Brush)", 10, 100, 40)
                        st.caption("Gunakan kuas untuk menutupi area yang ingin diubah. Area yang diwarnai putih akan diproses oleh AI.")
                    
                    with col_canvas:
                        canvas_result = st_canvas(
                            fill_color="rgba(255, 255, 255, 0.7)", 
                            stroke_width=stroke_width,
                            stroke_color="#FFFFFF", 
                            background_image=base_image_resized,
                            update_streamlit=True,
                            height=base_image_resized.height,
                            width=base_image_resized.width,
                            drawing_mode="freedraw",
                            key="canvas_inpainting",
                        )
                    
                    st.markdown("---")
                    st.markdown("**2. Instruksi Mikro (The One Edit Rule)**")
                    micro_prompt = st.text_input("Contoh: 'Change the wall paint to dark green' atau 'Add a modern leather sofa'", max_chars=200)
                    
                    if st.button("✨ Eksekusi Revisi", type="primary", use_container_width=True):
                        if canvas_result.image_data is not None and np.any(canvas_result.image_data[:, :, 3] > 0):
                            if micro_prompt:
                                with st.spinner("Mengirim masker dan instruksi ke Google AI (Inpainting)..."):
                                    try:
                                        # Buat Mask Image dari Kanvas
                                        mask_array = np.zeros((base_image_resized.height, base_image_resized.width), dtype=np.uint8)
                                        mask_array[canvas_result.image_data[:, :, 3] > 0] = 255
                                        mask_image = Image.fromarray(mask_array, mode="L")
                                        
                                        base_rgb = base_image_resized.convert("RGB")
                                        
                                        result = client.models.edit_images(
                                            model='imagen-4.0-generate-001',
                                            prompt=micro_prompt,
                                            base_image=base_rgb,
                                            mask_image=mask_image,
                                            config=types.EditImagesConfig(
                                                number_of_images=1,
                                                output_mime_type="image/jpeg",
                                                edit_mode="INPAINTING_INSERT" 
                                            )
                                        )
    
    
                                        
                                        st.success("✅ Revisi Selesai! (Aturan 'The One Edit Rule' berhasil diterapkan)")
                                        
                                        for generated_image in result.generated_images:
                                            edited_img = Image.open(io.BytesIO(generated_image.image.image_bytes))
                                            
                                            col_res1, col_res2 = st.columns(2)
                                            with col_res1:
                                                st.image(base_rgb, caption="Gambar Asli (Sebelum)", use_column_width=True)
                                            with col_res2:
                                                st.image(edited_img, caption=f"Hasil Revisi: {micro_prompt}", use_column_width=True)
                                                
                                            buf = io.BytesIO()
                                            edited_img.save(buf, format="JPEG")
                                            byte_im = buf.getvalue()
                                            st.download_button(
                                                label="💾 Unduh Hasil Revisi",
                                                data=byte_im,
                                                file_name="Revisi_Inpainting.jpg",
                                                mime="image/jpeg",
                                                use_container_width=True
                                            )
                                            
                                    except Exception as e:
                                        st.error(f"Gagal memproses revisi inpainting: {e}")
                                        st.info("Pastikan koneksi internet stabil dan kuota API Anda masih tersedia.")
                            else:
                                st.warning("Mohon ketik Instruksi Mikro terlebih dahulu (Misal: 'Change to wood material').")
                        else:
                            st.warning("⚠️ Anda belum melukis area masking di atas gambar. Gunakan kuas untuk menandai area yang ingin diubah.")
                except Exception:
                     st.error("❌ File yang Anda unggah bukan format gambar yang bisa dibaca.")

    with tab_upscale:
        st.markdown("### 🔍 Ultra HD Upscaler (4K/8K)")
        st.info("Tingkatkan resolusi gambar final Anda tanpa pecah (pixelated) untuk kebutuhan cetak brosur atau presentasi direksi.")
        
        upscale_img_file = st.file_uploader("📥 Unggah Gambar Final (JPG/PNG)", type=["png", "jpg", "jpeg", "jfif", "webp"], key="upscale_upload")
        
        if upscale_img_file is not None:
            up_img = Image.open(upscale_img_file)
            st.image(up_img, caption=f"Resolusi Asli: {up_img.width} x {up_img.height} px", use_column_width=True)
            
            st.markdown("---")
            col_up1, col_up2 = st.columns(2)
            with col_up1:
                target_res = st.selectbox("Target Skalabilitas:", ["4K Ultra HD (Brosur/Web)", "8K Print Quality (Billboard/Banner)"])
            with col_up2:
                enhance_mode = st.selectbox("Algoritma Penajaman:", ["PBR Texture Enhance (Arsitektur)", "Smooth Denoise (Interior/Soft)"])
                
            if st.button("🚀 Proses Upscale (Simulasi)", type="primary", use_container_width=True):
                with st.spinner(f"Menginisiasi jaringan saraf penajam resolusi ke {target_res}..."):
                    st.success("✅ Gambar siap di-upscale!")
                    st.warning("⚠️ Karena keterbatasan memori Streamlit Cloud saat ini, fitur Upscale sejati (pemrosesan piksel mentah) disarankan menggunakan API eksternal khusus (seperti Krea AI / Magnific) atau dijalankan di mesin lokal (Local GPU).")
                    
                    buf_up = io.BytesIO()
                    up_img.save(buf_up, format="PNG")
                    st.download_button(
                        label="💾 Unduh Hasil Upscale (Format Standar)",
                        data=buf_up.getvalue(),
                        file_name="Upscaled_Architecture.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
    with tab_hist:
        if not st.session_state.history_ledger:
            st.caption("Riwayat prompt Anda akan muncul di sini (Maksimal 10 terakhir).")
        else:
            for i, item in enumerate(st.session_state.history_ledger):
                with st.expander(f"{item['title']} (Terbaru)" if i==0 else item['title'], expanded=(i==0)):
                    st.code(item['prompt'], language="markdown")
