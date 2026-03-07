import streamlit as st
import random
import os
import io
from PIL import Image
import numpy as np

# Import Kanvas Inpainting
try:
    from streamlit_drawable_canvas import st_canvas
    HAS_CANVAS = True
except ImportError:
    HAS_CANVAS = False

import database_params as db
import prompt_logic as pl

# Import SDK Google GenAI
from google import genai
from google.genai import types


# ==========================================
# 0. KONFIGURASI HALAMAN (WAJIB PALING ATAS)
# ==========================================
st.set_page_config(page_title="SmartPromt Generator v2.1", layout="wide", initial_sidebar_state="expanded")


# ==========================================
# 1. KONFIGURASI KEAMANAN & API
# ==========================================
def get_api_key():
    """Mengambil API Key dengan Aman"""
    try:
        return st.secrets.get("GEMINI_API_KEY", st.secrets.get("GOOGLE_API_KEY", ""))
    except Exception:
        return os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

api_key_system = get_api_key()
client = None

with st.sidebar:
    st.markdown("### 🔐 Status Mesin Render")
    if api_key_system:
        st.success("🔒 API Key Terdeteksi")
        client = genai.Client(api_key=api_key_system)
    else:
        st.warning("⚠️ Mode Publik")
        api_key_input = st.text_input("🔑 Masukkan API Key Manual:", type="password")
        if api_key_input:
            client = genai.Client(api_key=api_key_input)
            st.success("✅ Kunci Manual Terkoneksi!")
        else:
            st.error("🚨 Kunci Akses Diperlukan!")
            st.stop()


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
    st.session_state.presentasi = "📸 Clean Photorealistic"
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
    
    st.session_state.custom_presets = {} 
    
    st.session_state.mode_render = "📸 Image (Still Photo)"
    st.session_state.camera_motion = db.DB_CAMERA_MOTION[0]
    st.session_state.storytelling_vibe = db.DB_STORYTELLING_VIBE[0]
    st.session_state.engine_video = db.DB_ENGINE_VIDEO[0]
    
    st.session_state.use_color_masking = False
    st.session_state.mask_red = "Beton Ekspos (Concrete)"
    st.session_state.mask_blue = "Batu Andesit (Andesite Stone)"
    st.session_state.mask_green = "Cat Putih (White Stucco)"
    st.session_state.mask_yellow = "Kayu Solid (Timber Wood)"
    st.session_state.mask_purple = "Kaca Jernih (Clear Glass)"
    st.session_state.mask_orange = "Bata Terracotta (Terracotta Brick)"
    st.session_state.mask_cyan = "Besi / Aluminium (Steel/Aluminium)"
    st.session_state.mask_magenta = "Marmer / Granit (Marble/Granite)"


def handle_random():
    s = st.session_state
    s.tipe = random.choice(db.DB_TIPE)
    s.gaya = random.choice(db.DB_GAYA)
    s.material = random.choice(db.DB_MATERIAL)
    s.suasana = random.choice(db.DB_SUASANA)
    s.view = random.choice(db.DB_VIEW)
    s.skenario = random.choice(db.DB_SKENARIO)
    s.engine = random.choice(db.DB_ENGINE)
    s.tapak = random.choice(db.DB_TAPAK)
    s.vegetasi = random.choice(db.DB_VEGETASI)

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
    st.markdown('<div class="header-box"><div style="display:flex; flex-direction:column;"><h1 class="title-text">SmartPromt Generator <span style="color:#4338ca">v2.1</span></h1><p class="subtitle-text">Enterprise Prompt Builder & Material ID Mapping</p></div></div>', unsafe_allow_html=True)
with col_head2:
    st.write("") 
    if st.button("🔄 Acak Parameter", use_container_width=True):
        handle_random()
        st.rerun()

col_left, col_right = st.columns([6, 6], gap="large")

with col_left:
    with st.expander("📂 Preset Manager (Load & Save)", expanded=False):
        preset_options = list(db.DB_PRESETS.keys()) + list(st.session_state.custom_presets.keys())
        selected_preset = st.selectbox("Pilih Profil Pengaturan:", preset_options)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("📥 Muat Preset", use_container_width=True):
                load_preset(selected_preset)
                st.rerun()
        with col_p2:
            new_preset_name = st.text_input("Nama Preset Baru:", placeholder="Misal: Villa Gaya Saya")
            if st.button("💾 Simpan Saat Ini", use_container_width=True) and new_preset_name:
                st.session_state.custom_presets[new_preset_name] = {
                    "tipe": st.session_state.tipe, "gaya": st.session_state.gaya, "material": st.session_state.material,
                    "suasana": st.session_state.suasana, "cuaca": st.session_state.cuaca, "view": st.session_state.view,
                    "temp_warna": st.session_state.temp_warna, "fixture_int": st.session_state.fixture_int,
                    "fixture_ext": st.session_state.fixture_ext, "teknik_cahaya": st.session_state.teknik_cahaya,
                    "tapak": st.session_state.tapak, "vegetasi": st.session_state.vegetasi, "rasio": st.session_state.rasio,
                    "presentasi": st.session_state.presentasi, "skenario": st.session_state.skenario, "engine": st.session_state.engine,
                    "lensa_khusus": st.session_state.lensa_khusus, "kamera_film": st.session_state.kamera_film, "weathering": st.session_state.weathering
                }
                st.success(f"Preset '{new_preset_name}' disimpan!")
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
        
        # 1. Gunakan variabel lokal untuk uploader, dan dukung jfif/webp
        uploaded_sketch_file = st.file_uploader("Upload Sketsa Garis / Base Image", type=["jpg", "png", "jpeg", "jfif", "webp"])
        
        if uploaded_sketch_file is not None:
            # 2. Buka gambar dengan PIL (Cara paling aman di Streamlit Cloud)
            sketch_img = Image.open(uploaded_sketch_file)
            st.image(sketch_img, caption="Preview Sketsa Aktual", use_column_width=True)
           
            
            # 3. Simpan status (Flag) ke memori agar logika prompt mendeteksinya
            st.session_state.uploaded_sketch = True 
            
            st.success("✅ Sketsa terdeteksi! 'Vision Constraint' akan diaktifkan.")
            st.session_state.ai_control = st.selectbox("Metode Restriksi Struktural AI (Lapisan 2):", db.DB_AI_CONTROL, index=db.DB_AI_CONTROL.index(st.session_state.ai_control)) 
        else:
            # 4. Kosongkan memori jika gambar dihapus/tidak ada
            st.session_state.uploaded_sketch = None
     
            
            # --- UI BARU UNTUK FITUR COLOR MASKING ---
            st.markdown("---")
            st.session_state.use_color_masking = st.checkbox("🎨 Aktifkan Semantic Color Masking (Material ID)", value=st.session_state.use_color_masking)
            if st.session_state.use_color_masking:
                st.info("💡 Pastikan Anda mengunggah gambar 'Color Mask' bersolusi tinggi dengan warna kontras (merah, biru, hijau murni, dsb) di chat Gemini.")
                c1, c2 = st.columns(2)
                with c1:
                    st.session_state.mask_red = st.text_input("🔴 Merah (Red Zone):", value=st.session_state.mask_red)
                    st.session_state.mask_green = st.text_input("🟢 Hijau (Green Zone):", value=st.session_state.mask_green)
                    st.session_state.mask_purple = st.text_input("🟣 Ungu (Purple Zone):", value=st.session_state.mask_purple)
                    st.session_state.mask_cyan = st.text_input("🩵 Cyan (Cyan Zone):", value=st.session_state.mask_cyan)
                with c2:
                    st.session_state.mask_blue = st.text_input("🔵 Biru (Blue Zone):", value=st.session_state.mask_blue)
                    st.session_state.mask_yellow = st.text_input("🟡 Kuning (Yellow Zone):", value=st.session_state.mask_yellow)
                    st.session_state.mask_orange = st.text_input("🟠 Oranye (Orange Zone):", value=st.session_state.mask_orange)
                    st.session_state.mask_magenta = st.text_input("🩷 Magenta (Magenta Zone):", value=st.session_state.mask_magenta)
                        
        st.markdown("---")
        st.session_state.tipe = st.selectbox("Kategori Bangunan", db.DB_TIPE, index=db.DB_TIPE.index(st.session_state.tipe))
        st.session_state.gaya = st.selectbox("Gaya Arsitektur", db.DB_GAYA, index=db.DB_GAYA.index(st.session_state.gaya))
        st.session_state.material = st.selectbox("Material Dasar Lingkungan (Base Material)", db.DB_MATERIAL, index=db.DB_MATERIAL.index(st.session_state.material))
        st.session_state.weathering = st.selectbox("Kondisi Fisik / Keausan Material", db.DB_WEATHERING, index=db.DB_WEATHERING.index(st.session_state.weathering))
        st.session_state.detail = st.text_area("Detail Spesifik Khusus (Struktur/Bentuk)", value=st.session_state.detail, height=80)

    with tab2:
        st.session_state.temp_warna = st.selectbox("Suhu Warna Lampu (Kelvin)", db.DB_TEMP_WARNA, index=db.DB_TEMP_WARNA.index(st.session_state.temp_warna))
        is_interior_ui = "[INT]" in st.session_state.view
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
            st.session_state.engine_video = st.selectbox("Engine Video Target (Lapisan Temporal)", db.DB_ENGINE_VIDEO, index=db.DB_ENGINE_VIDEO.index(st.session_state.engine_video))
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

# --- KOLOM KANAN (OUTPUT & INPAINTING) ---
with col_right:
    # KITA TAMBAHKAN 1 TAB BARU: 🖌️ Inpainting (Revisi)
    tab_out, tab_inpaint, tab_hist = st.tabs(["🖥️ Output (Prompt & Visual)", "🖌️ Inpainting (Revisi)", "📚 Prompt Ledger (Riwayat)"])
    
    with tab_out:
        if st.session_state.generated_prompt:
            st.success("✅ Logika arsitektural & komposisi fotografi siap dieksekusi!")
            
            st.markdown("#### 1️⃣ Eksekusi via Gemini Web / AI Lainnya (Gratis)")
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
            
    # ========================================================
    # TAB BARU: KANVAS INPAINTING (SUTRADARA REVISI)
    # ========================================================
    with tab_inpaint:
        st.markdown("### 🖌️ Kanvas Revisi (Inpainting)")
        st.info("Unggah gambar hasil render final Anda (dari Gemini/Midjourney/API), lalu 'lukis' area yang ingin direvisi.")
        
        if not HAS_CANVAS:
            st.error("🚨 Pustaka `streamlit-drawable-canvas` belum terdeteksi. Silakan install via terminal: `pip install streamlit-drawable-canvas`")
        else:
            base_img_file = st.file_uploader("🖼️ Unggah Gambar Base Render", type=["png", "jpg", "jpeg", "jfif", "webp"], key="inpaint_upload")
                        
            if base_img_file is not None:
                base_image = Image.open(base_img_file).convert("RGBA")
                
                # Skala gambar agar muat di UI (Maks lebar 600px)
                max_width = 600
                if base_image.width > max_width:
                    ratio = max_width / base_image.width
                    new_height = int(base_image.height * ratio)
                    base_image_resized = base_image.resize((max_width, new_height))
                else:
                    base_image_resized = base_image

                st.markdown("**1. Lukis Area Masking**")
                col_canvas_tools, col_canvas = st.columns([1, 3])
                
                with col_canvas_tools:
                    stroke_width = st.slider("Ukuran Kuas (Brush)", 10, 100, 40)
                    st.caption("Gunakan kuas untuk menutupi area yang ingin diubah. Area yang diwarnai putih akan diproses oleh AI.")
                
                with col_canvas:
                    # Komponen Kanvas Interaktif
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 255, 255, 0.7)", # Warna isian agak transparan
                        stroke_width=stroke_width,
                        stroke_color="#FFFFFF", # Kuas warna putih
                        background_image=base_image_resized,
                        update_streamlit=True,
                        height=base_image_resized.height,
                        width=base_image_resized.width,
                        drawing_mode="freedraw",
                        key="canvas_inpainting",
                    )
                
                st.markdown("---")
                st.markdown("**2. Instruksi Mikro (The One Edit Rule)**")
                st.write("Sesuai standar arsitektur, masukkan HANYA 1 perintah spesifik pendek (< 200 karakter) untuk area yang ditandai.")
                
                micro_prompt = st.text_input("Contoh: 'Change the wall paint to dark green' atau 'Add a modern leather sofa'", max_chars=200)
                
                if st.button("✨ Eksekusi Revisi", type="primary", use_container_width=True):
                    # Validasi 1: Pastikan pengguna sudah mencoret sesuatu di kanvas
                    if canvas_result.image_data is not None and np.any(canvas_result.image_data[:, :, 3] > 0):
                        # Validasi 2: Pastikan ada instruksi mikro
                        if micro_prompt:
                            with st.spinner("Mengirim masker dan instruksi ke Google AI (Inpainting)..."):
                                try:
                                    # 1. EKSTRAKSI MASKER (Hitam-Putih) dari coretan kanvas
                                    # Buat kanvas kosong warna hitam
                                    mask_array = np.zeros((base_image_resized.height, base_image_resized.width), dtype=np.uint8)
                                    # Area yang dicoret pengguna (Alpha > 0) diubah jadi warna putih (255)
                                    mask_array[canvas_result.image_data[:, :, 3] > 0] = 255
                                    # Konversi matriks angka menjadi file gambar Masker
                                    mask_image = Image.fromarray(mask_array, mode="L")
                                    
                                    # Pastikan gambar base formatnya RGB murni sebelum dikirim ke server
                                    base_rgb = base_image_resized.convert("RGB")
                                    
                                    # 2. PANGGIL API EDIT GAMBAR (MODUL 2)
                                    # Menggunakan model Imagen 4.0 yang stabil di akun Anda
                                    result = client.models.edit_images(
                                        model='imagen-4.0-generate-001',
                                        prompt=micro_prompt,
                                        base_image=base_rgb,
                                        mask_image=mask_image,
                                        config=types.EditImagesConfig(
                                            number_of_images=1,
                                            output_mime_type="image/jpeg",
                                            edit_mode="INPAINTING_INSERT" # Kunci agar tidak mengubah area di luar masker
                                        )
                                    )
                                    
                                    # 3. TAMPILKAN HASILNYA
                                    st.success("✅ Revisi Selesai! (Aturan 'The One Edit Rule' berhasil diterapkan)")
                                    
                                    for generated_image in result.generated_images:
                                        edited_img = Image.open(io.BytesIO(generated_image.image.image_bytes))
                                        
                                        # Tampilkan gambar berdampingan (Sebelum vs Sesudah)
                                        col_res1, col_res2 = st.columns(2)
                                        with col_res1:
                                            st.image(base_rgb, caption="Gambar Asli", use_column_width=True)
                                            
                                        with col_res2:
                                            st.image(edited_img, caption=f"Hasil Revisi", use_column_width=True)
                                            
                                            
                                        # Tombol Unduh Revisi
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

    with tab_hist:
        if not st.session_state.history_ledger:
            st.caption("Riwayat prompt Anda akan muncul di sini (Maksimal 10 terakhir).")
        else:
            for i, item in enumerate(st.session_state.history_ledger):
                with st.expander(f"{item['title']} (Terbaru)" if i==0 else item['title'], expanded=(i==0)):
                    st.code(item['prompt'], language="markdown")
