import streamlit as st
import random
import base64
import requests
import time
import requests
import urllib.parse
import random
from google import genai
from google.genai import types


# ==========================================
# 1. DATABASE & CONFIGURATIONS
# ==========================================
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
    "Golden Hour (Sunset)", "Blue Hour (Twilight)", "Sunny Day", 
    "Foggy Morning", "Cinematic Night Lighting", "Rainy Cyberpunk Mood",
    "Overcast Soft Light", "Soft Morning Ambient Light"
]

DB_VIEW = [
    "[EXT] Eye Level (Human View)", "[EXT] Drone / Bird's Eye View", "[EXT] Worm's Eye View (Low Angle)",
    "[INT] Eye Level (Human View)", "[INT] Wide Angle Interior", "[INT] Close-up Detail Shot"
]

DB_PRESENTASI = {
    "📸 Clean Photorealistic": "clean, no text, pure photography style",
    "📏 Technical Concept": "architectural concept sheet style, mixed media, photorealistic render overlaid with hand-drawn technical annotations, dimension lines, measurement arrows, material callouts, handwritten notes, sketch aesthetic",
    "📝 Blueprint / Wireframe": "blueprint style, white lines on blue background, technical drawing, wireframe structural view",
    "🎨 Watercolor Sketch": "watercolor painting style, soft edges, artistic architectural sketch, ink outline"
}

DB_SKENARIO = [
    "Standard Clear Architectural Shot",
    "Macro Foreground: Sharp focus on falling flower petals (Bokeh)",
    "Cinematic Wet Reflections: Rain puddles reflecting light",
    "Foggy Morning Mist: Thin mist with soft lighting",
    "Dramatic Interior Sunbeams: Sharp god rays on concrete",
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

# Konfigurasi URL BFF Server (Ubah sesuai dengan server backend nyata Anda)
BFF_BASE_URL = "http://localhost:8000" 

# ==========================================
# 2. UTILITY FUNCTIONS
# ==========================================
def enhance_with_pbr(material_string):
    pbr_dictionary = {
        "concrete": "exposed raw concrete with micro-surface roughness and subtle moisture staining",
        "wood": "timber wood with deep matte visible grain and low specular reflectivity",
        "marble": "highly polished marble with sharp specular reflections and subsurface scattering",
        "steel": "weathered steel with natural oxidation, high metallic value, and diffuse roughness",
        "glass": "ultra-clear architectural glass with realistic index of refraction and sharp environmental reflections",
        "brick": "rough terracotta masonry with displacement mapping and ambient occlusion in crevices"
    }
    
    enhanced = material_string.lower()
    for key, value in pbr_dictionary.items():
        enhanced = enhanced.replace(key, value)
    return enhanced

def get_base64_of_bytes(file_bytes):
    return base64.b64encode(file_bytes).decode()

# ==========================================
# 3. INITIALIZE SESSION STATE (Setara useState)
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.tipe = DB_TIPE[0]
    st.session_state.gaya = DB_GAYA[0]
    st.session_state.material = DB_MATERIAL[0]
    st.session_state.suasana = DB_SUASANA[0]
    st.session_state.view = DB_VIEW[0]
    st.session_state.rasio = "Landscape (16:9)"
    st.session_state.presentasi = "📸 Clean Photorealistic"
    st.session_state.skenario = DB_SKENARIO[0]
    st.session_state.engine = DB_ENGINE[0]
    st.session_state.detail = ""
    st.session_state.lock_sketch = True
    st.session_state.use_grounding = True
    st.session_state.motion_prompt = "Slow cinematic pan, maintaining strict structural rigidity and realistic lighting."
    
    st.session_state.generated_prompt = ""
    st.session_state.sketch_image = None
    st.session_state.style_image = None
    st.session_state.render_image_base64 = None
    st.session_state.video_url = None
    st.session_state.app_error = None

# ==========================================
# 4. LOGIC FUNCTIONS
# ==========================================
def handle_random():
    st.session_state.tipe = random.choice(DB_TIPE)
    st.session_state.gaya = random.choice(DB_GAYA)
    st.session_state.material = random.choice(DB_MATERIAL)
    st.session_state.suasana = random.choice(DB_SUASANA)
    st.session_state.view = random.choice(DB_VIEW)
    st.session_state.skenario = random.choice(DB_SKENARIO)
    st.session_state.engine = random.choice(DB_ENGINE)

def construct_prompt():
    style_description = DB_PRESENTASI[st.session_state.presentasi]
    
    is_interior = "[INT]" in st.session_state.view
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    
    pbr_material_desc = enhance_with_pbr(st.session_state.material)

    core = f"Generate a high-end architectural visualization of a {st.session_state.tipe}. Focus on the {arch_type_context}. Design style: {st.session_state.gaya}. "
    
    if st.session_state.sketch_image:
        core += "Follow the structural outlines and geometry provided in the SKETCH IMAGE strictly. "
        if st.session_state.lock_sketch:
            core += "CRITICAL CONSTRAINT: Maintain the exact spatial arrangement, scale, and silhouette from the input sketch. "

    lens = "Use wide angle 24mm lens to capture the breadth of the space. " if is_interior else "Use 35mm-50mm lens to prevent geometric distortion. "
    core += f"Presentation Style: {style_description}. "
    core += f"Perspective & Lens: {st.session_state.view}. {lens}"
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. "
    core += f"Lighting/Atmosphere: {st.session_state.suasana}. "
    core += f"Cinematic Storytelling/Environment: {st.session_state.skenario}. "
    
    if st.session_state.detail:
        core += f"Additional details: {st.session_state.detail}. "
        
    core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {st.session_state.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text"

    st.session_state.generated_prompt = core
    st.session_state.app_error = None

def handle_render_image():
    if not st.session_state.generated_prompt:
        st.session_state.app_error = "Silakan susun prompt terlebih dahulu."
        return

    # 1. Mapping Resolusi Aktual (Pollinations menggunakan pixel, bukan rasio string)
    rasio_mapping = {
        "Landscape (16:9)": (1920, 1080),
        "Portrait / Story (9:16)": (1080, 1920),
        "Square / Feed (1:1)": (1024, 1024),
        "Classic Photo (4:3)": (1440, 1080),
        "Ultra Wide (4:1)": (1920, 512)
    }
    width, height = rasio_mapping.get(st.session_state.rasio, (1920, 1080))

    # 2. Persiapkan URL dan Parameter
    # Encode prompt agar aman dikirim lewat URL
    safe_prompt = urllib.parse.quote(st.session_state.generated_prompt)
    
    # Gunakan seed acak agar hasil render berbeda meskipun prompt-nya persis sama
    seed = random.randint(1, 1000000)
    
    # Endpoint Pollinations (model=flux untuk hasil paling fotorealistis, nologo=true hilangkan watermark)
    endpoint = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

    try:
        # 3. Eksekusi Request Langsung
        # Pollinations langsung mengembalikan file gambar mentah (bytes), bukan JSON
        response = requests.get(endpoint)
        
        if not response.ok:
            raise Exception(f"Gagal merender gambar dari server eksternal (Status {response.status_code})")
            
        # 4. Konversi gambar menjadi Base64 agar kompatibel dengan state UI Streamlit
        image_bytes = response.content
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        st.session_state.render_image_base64 = b64_image
        st.session_state.app_error = None
            
    except Exception as e:
        st.session_state.app_error = f"Render API Error: {str(e)}"

# ==========================================
# 5. UI RENDER (Streamlit Layout)
# ==========================================
st.set_page_config(page_title="Smart Arch Studio v2.1", layout="wide", initial_sidebar_state="collapsed")
# --- SIDEBAR UNTUK API KEY ---
with st.sidebar:
    st.header("🔑 Konfigurasi API")
    st.session_state.api_key = st.text_input("Masukkan Gemini API Key", type="password")
    st.markdown("[Dapatkan API Key di Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.subheader("📡 Diagnostic Scanner")
    
    if st.button("Deteksi Model Tersedia", use_container_width=True):
        if not st.session_state.get("api_key"):
            st.error("Masukkan API Key terlebih dahulu di atas.")
        else:
            with st.spinner("Mendeteksi..."):
                api_key = st.session_state.api_key
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                
                try:
                    response = requests.get(url)
                    if response.ok:
                        models = response.json().get("models", [])
                        
                        # Kita filter dan tampilkan semua model yang aktif
                        st.success(f"Ditemukan {len(models)} model aktif!")
                        
                        with st.expander("Lihat Daftar Lengkap Model", expanded=True):
                            for m in models:
                                name = m.get("name", "").replace("models/", "")
                                methods = m.get("supportedGenerationMethods", [])
                                
                                # Highlight model gambar jika ada
                                if "imagen" in name.lower():
                                    st.markdown(f"🎨 **{name}**")
                                    st.caption(f"Metode: {', '.join(methods)}")
                                else:
                                    st.markdown(f"📄 {name}")
                    else:
                        st.error(f"Gagal mendeteksi. Server membalas: {response.status_code}")
                except Exception as e:
                    st.error(f"Koneksi terputus: {str(e)}")

# Custom CSS untuk warna dan styling menyerupai Tailwind
st.markdown("""
<style>
    .header-box { background-color: #ffffff; padding: 1rem; border-bottom: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;}
    .title-text { color: #1a1c1e; font-weight: 900; margin: 0; font-size: 1.5rem; }
    .subtitle-text { color: #64748b; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.markdown('<div class="header-box"><div style="display:flex; flex-direction:column;"><h1 class="title-text">Smart Arch Studio <span style="color:#4338ca">v2.1 (Enterprise)</span></h1><p class="subtitle-text">Secure Generative BIM Visualizer</p></div></div>', unsafe_allow_html=True)
with col_head2:
    st.write("") # spacing
    if st.button("🔄 Acak Parameter", use_container_width=True):
        handle_random()
        st.rerun()

# Layout Utama
col_left, col_right = st.columns([6, 6], gap="large")

# --- KIRI: PANEL INPUT ---
with col_left:
    st.subheader("📤 Source Immersives (Max 7MB)")
    col_sketch, col_style = st.columns(2)
    
    with col_sketch:
        st.markdown("**Sketsa Dasar (Blueprint)**")
        st.session_state.lock_sketch = st.checkbox("LOCKED (Maintain Spatial Arrangement)", value=st.session_state.lock_sketch)
        sketch_file = st.file_uploader("Upload Sketsa", type=["png", "jpg", "jpeg"], key="sketch_up")
        if sketch_file:
            if sketch_file.size > 7 * 1024 * 1024:
                st.error("Ukuran file maksimal 7MB.")
            else:
                mime_type = sketch_file.type
                b64_data = get_base64_of_bytes(sketch_file.read())
                st.session_state.sketch_image = {"mimeType": mime_type, "data": b64_data}
                st.image(sketch_file, use_container_width=True)
        else:
            st.session_state.sketch_image = None
            
    with col_style:
        st.markdown("**Referensi Mood & Warna**")
        style_file = st.file_uploader("Upload Referensi", type=["png", "jpg", "jpeg"], key="style_up")
        if style_file:
            if style_file.size > 7 * 1024 * 1024:
                st.error("Ukuran file maksimal 7MB.")
            else:
                mime_type = style_file.type
                b64_data = get_base64_of_bytes(style_file.read())
                st.session_state.style_image = {"mimeType": mime_type, "data": b64_data}
                st.image(style_file, use_container_width=True)
        else:
            st.session_state.style_image = None

    st.markdown("---")
    st.subheader("⚙️ Project Definition")
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.session_state.tipe = st.selectbox("Kategori Bangunan", DB_TIPE, index=DB_TIPE.index(st.session_state.tipe))
    with row1_col2:
        st.session_state.material = st.selectbox("Material Utama (PBR)", DB_MATERIAL, index=DB_MATERIAL.index(st.session_state.material))
        
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.session_state.view = st.selectbox("Kamera & Perspektif", DB_VIEW, index=DB_VIEW.index(st.session_state.view))
    with row2_col2:
        st.session_state.suasana = st.selectbox("Pencahayaan / Waktu", DB_SUASANA, index=DB_SUASANA.index(st.session_state.suasana))
        
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.session_state.presentasi = st.selectbox("Gaya Render", list(DB_PRESENTASI.keys()), index=list(DB_PRESENTASI.keys()).index(st.session_state.presentasi))
    with row3_col2:
        st.session_state.rasio = st.selectbox("Rasio Gambar", list(DB_RASIO.keys()), index=list(DB_RASIO.keys()).index(st.session_state.rasio))
        
    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        st.session_state.gaya = st.selectbox("Gaya Arsitektur", DB_GAYA, index=DB_GAYA.index(st.session_state.gaya))
    with row4_col2:
        st.session_state.skenario = st.selectbox("Skenario / Lingkungan", DB_SKENARIO, index=DB_SKENARIO.index(st.session_state.skenario))

    st.session_state.engine = st.selectbox("Render Engine", DB_ENGINE, index=DB_ENGINE.index(st.session_state.engine))
    st.session_state.detail = st.text_input("Detail Tambahan (Opsional)", value=st.session_state.detail)

    st.markdown("---")
    st.markdown("**Konfigurasi Lanjutan (Video & Grounding)**")
    st.session_state.use_grounding = st.checkbox("Gemini Search Grounding (Gunakan data web live untuk akurasi konteks)", value=st.session_state.use_grounding)
    st.session_state.motion_prompt = st.text_input("Motion Prompt (Animasi Video)", value=st.session_state.motion_prompt)

    if st.button("✨ SUSUN PROMPT NEURAL", use_container_width=True, type="primary"):
        construct_prompt()

# --- KANAN: PANEL OUTPUT & RENDER ---
with col_right:
    st.subheader("🖥️ Neural Output Panel")
    
    if st.session_state.app_error:
        st.error(f"Peringatan: {st.session_state.app_error}")
        
    st.markdown("**PBR Neural Prompt:**")
    st.code(st.session_state.generated_prompt if st.session_state.generated_prompt else "Tekan tombol 'SUSUN PROMPT NEURAL' di sebelah kiri...", language="plaintext")

    # Display Area
    st.markdown("---")
    display_container = st.container(border=True)
    with display_container:
        if st.session_state.video_url:
            st.video(st.session_state.video_url)
        elif st.session_state.render_image_base64:
            image_bytes = base64.b64decode(st.session_state.render_image_base64)
            st.image(image_bytes, use_container_width=True)
        else:
            st.info("Viewport Standby. Silakan generate prompt dan render gambar.")
            
    # Action Buttons
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("🖼️ RENDER IMAGE (BFF)", use_container_width=True, disabled=not bool(st.session_state.generated_prompt)):
            with st.spinner("Memproses Render Image di Server..."):
                handle_render_image()
                st.rerun()
                
    with action_col2:
        if st.button("🎬 GENERATE VIDEO", use_container_width=True, disabled=not bool(st.session_state.render_image_base64)):
            handle_trigger_video()
            st.rerun()
