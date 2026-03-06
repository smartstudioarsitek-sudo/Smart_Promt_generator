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

    # 2. Cinematography & Lens (Fase 2 Update)
    if "Auto" not in s.lensa_khusus:
        lens = s.lensa_khusus.split(" (")[0] # Ambil teks sebelum tanda kurung
    else:
        lens = "Use wide angle 24mm lens" if is_interior else "Use 35mm-50mm lens"
        
    camera_setup = s.kamera_film.split(" (")[0]
    
    core += f"Perspective & View: {s.view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. Presentation Style: {style_description}. "
    
    # 3. Materials & Weathering (Fase 2 Update)
    weathering = s.weathering.split(" (")[0]
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. Material Condition/Weathering: {weathering}. "
    
    # 4. Lighting, Environment & Site Context (Fase 2 Final)
    # Bersihkan string dari penjelasan bahasa Indonesia
    tapak = s.tapak.split(" (")[0]
    vegetasi = s.vegetasi.split(" (")[0]
    
    lighting_setup = f"Natural Lighting/Time: {s.suasana}. Weather/Atmosphere: {s.cuaca}. "
    if "Auto" not in s.temp_warna:
        lighting_setup += f"Artificial Light Color Temp: {s.temp_warna.split(' (')[0]}. "
        
    fixture = s.fixture_int if is_interior else s.fixture_ext
    if "Tanpa" not in fixture:
        lighting_setup += f"Specific Lighting Fixtures: {fixture.split(' (')[0]}. "
        
    if "Standard" not in s.teknik_cahaya:
        lighting_setup += f"Advanced Lighting Technique: {s.teknik_cahaya.split(' (')[0]}. "

    # Gabungkan Konteks Tapak ke dalam core prompt
    core += f"Site Context & Topography: {tapak}. Landscaping & Vegetation: {vegetasi}. "
    core += f"{lighting_setup} Cinematic Storytelling: {s.skenario}. "
    
    if s.detail:
        core += f"Additional details: {s.detail}. "
        
    # 5. Engine & Quality
    core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {s.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {db.DB_RASIO[s.rasio]}."

    s.generated_prompt = core
    
