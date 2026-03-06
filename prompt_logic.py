# prompt_logic.py
import streamlit as st
import database_params as db

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

def construct_prompt():
    # Ambil data dari Session State Streamlit
    s = st.session_state
    
    style_description = db.DB_PRESENTASI[s.presentasi]
    is_interior = "[INT]" in s.view
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    pbr_material_desc = enhance_with_pbr(s.material)

    # 1. Base Geometry & Constraints
    core = f"Generate a high-end architectural visualization of a {s.tipe}. Focus on the {arch_type_context}. Design style: {s.gaya}. "
    if s.use_sketch:
        core += "CRITICAL CONSTRAINT: Please strictly follow the structural outlines, geometry, layout, and silhouette provided in the ATTACHED SKETCH IMAGE. "
    if s.use_ref:
        core += "Please match the overall mood, color palette, and lighting style of the ATTACHED REFERENCE IMAGE. "

    # 2. Cinematography & Lens
    lens = "Use wide angle 24mm lens to capture the breadth of the space. " if is_interior else "Use 35mm-50mm lens to prevent geometric distortion. "
    core += f"Perspective & Lens: {s.view}. {lens} Presentation Style: {style_description}. "
    
    # 3. Materials
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. "
    
    # 4. Lighting & Environment (Termasuk Cuaca Dinamis)
    lighting_setup = f"Natural Lighting/Time: {s.suasana}. Weather/Atmosphere: {s.cuaca}. "
    
    if "Auto" not in s.temp_warna:
        clean_temp = s.temp_warna.split(" (")[0]
        lighting_setup += f"Artificial Light Color Temperature: {clean_temp}. "
        
    fixture = s.fixture_int if is_interior else s.fixture_ext
    if "Tanpa" not in fixture:
        clean_fixture = fixture.split(" (")[0]
        lighting_setup += f"Specific Lighting Fixtures: {clean_fixture}. "
        
    if "Standard" not in s.teknik_cahaya:
        clean_teknik = s.teknik_cahaya.split(" (")[0]
        lighting_setup += f"Advanced Lighting Technique: {clean_teknik}. "

    core += f"{lighting_setup} Cinematic Storytelling: {s.skenario}. "
    
    if s.detail:
        core += f"Additional details: {s.detail}. "
        
    # 5. Engine & Quality
    core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {s.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {db.DB_RASIO[s.rasio]}."

    s.generated_prompt = core
