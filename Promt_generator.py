import streamlit as st
import random

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

# ==========================================
# 3. INITIALIZE SESSION STATE
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
    st.session_state.generated_prompt = ""

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
    
    lens = "Use wide angle 24mm lens to capture the breadth of the space. " if is_interior else "Use 35mm-50mm lens to prevent geometric distortion. "
    core += f"Presentation Style: {style_description}. "
    core += f"Perspective & Lens: {st.session_state.view}. {lens}"
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. "
    core += f"Lighting/Atmosphere: {st.session_state.suasana}. "
    core += f"Cinematic Storytelling/Environment: {st.session_state.skenario}. "
    
    if st.session_state.detail:
        core += f"Additional details: {st.session_state.detail}. "
        
    core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {st.session_state.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {DB_RASIO[st.session_state.rasio]}."

    st.session_state.generated_prompt = core

# ==========================================
# 5. UI RENDER (Streamlit Layout)
# ==========================================
st.set_page_config(page_title="Smart Arch Prompt v2.1", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
<style>
    .header-box { background-color: #ffffff; padding: 1rem; border-bottom: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;}
    .title-text { color: #1a1c1e; font-weight: 900; margin: 0; font-size: 1.5rem; }
    .subtitle-text { color: #64748b; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.markdown('<div class="header-box"><div style="display:flex; flex-direction:column;"><h1 class="title-text">SmartBIM Prompt Generator <span style="color:#4338ca">v2.1</span></h1><p class="subtitle-text">PBR Neural Prompt Builder</p></div></div>', unsafe_allow_html=True)
with col_head2:
    st.write("") 
    if st.button("🔄 Acak Parameter", use_container_width=True):
        handle_random()
        st.rerun()

col_left, col_right = st.columns([6, 6], gap="large")

# --- KIRI: PANEL INPUT ---
with col_left:
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
    if st.button("✨ SUSUN PROMPT NEURAL", use_container_width=True, type="primary"):
        construct_prompt()

# --- KANAN: PANEL OUTPUT ---
with col_right:
    st.subheader("🖥️ Hasil Neural Prompt")
    
    if st.session_state.generated_prompt:
        st.success("✅ Prompt berhasil disusun! Silakan copy teks di bawah ini dan paste ke Gemini Advanced.")
        st.code(st.session_state.generated_prompt, language="plaintext")
        
        st.info("💡 **Tips Rendering di Gemini:**\nPastikan Anda meminta Gemini untuk membuat gambar menggunakan prompt di atas. Jika Anda ingin menyertakan gambar sketsa sebagai referensi, cukup upload gambar sketsa Anda di chat Gemini bersamaan dengan prompt ini.")
    else:
        st.info("👈 Silakan atur parameter di sebelah kiri dan klik **SUSUN PROMPT NEURAL**.")
