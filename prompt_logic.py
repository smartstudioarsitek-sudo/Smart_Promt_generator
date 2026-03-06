# prompt_logic.py
import streamlit as st
import datetime
import database_params as db

# prompt_logic.py (Update Fungsi PBR)
def enhance_with_pbr(material_string):
    pbr_dictionary = {
        "concrete": "exposed raw concrete with micro-surface roughness and subtle moisture staining",
        "wood": "timber wood with deep matte visible grain and low specular reflectivity",
        "kayu": "natural timber wood panels with detailed matte grain, subtle imperfections, and realistic warm bounce light", # Tambahan
        "marble": "highly polished marble with sharp specular reflections and subsurface scattering",
        "steel": "weathered steel with natural oxidation, high metallic value, and diffuse roughness",
        "glass": "ultra-clear architectural glass with realistic index of refraction and sharp environmental reflections",
        "brick": "rough terracotta masonry with displacement mapping and ambient occlusion in crevices",
        "cat": "smooth matte architectural wall paint (stucco/plaster) with subtle micro-bump textures to catch sunlight realistically", # Tambahan
        "aluminium": "anodized aluminium frames with brushed metallic finish and realistic anisotropic reflections" # Tambahan
    }
    enhanced = material_string.lower()
    for key, value in pbr_dictionary.items():
        if key in enhanced: # Ubah sedikit logikanya agar me-replace keyword yang ada di dalam string manual
            enhanced = enhanced.replace(key, value)
    return enhanced


# --- FASE 3: SISTEM VALIDASI KONFLIK ---
def check_conflicts(s):
    conflicts = []
    is_interior = "[INT]" in s.view
    is_night = any(k in s.suasana.lower() for k in ["night", "twilight"])

    # Konflik 1: Malam hari tanpa lampu
    if is_night and ("Tanpa" in s.fixture_ext if not is_interior else "Tanpa" in s.fixture_int):
        conflicts.append("⚠️ **Peringatan Cahaya:** Anda memilih waktu Malam/Senja, tetapi **tidak memilih Fixture Lampu**. Render mungkin akan terlalu gelap atau kehilangan detail.")

    # Konflik 2: Lensa Macro untuk Drone
    if "Drone" in s.view and "Macro" in s.lensa_khusus:
        conflicts.append("⚠️ **Peringatan Optik:** *Drone View* tidak logis dipadukan dengan *Lensa Macro*. Skala bangunan akan terlihat seperti miniatur mainan.")

    # Konflik 3: Interior tapi cuaca ekstrem tanpa konteks
    if is_interior and ("Rain" in s.cuaca or "Fog" in s.cuaca):
        conflicts.append("💡 **Saran Lingkungan:** Anda merender Interior dengan cuaca Hujan/Kabut di luar. Pastikan desain Anda memiliki jendela kaca besar agar efek cuaca ini terlihat dari dalam.")

    return conflicts

def construct_prompt():
    s = st.session_state
    
    style_description = db.DB_PRESENTASI[s.presentasi]
    is_interior = "[INT]" in s.view
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    pbr_material_desc = enhance_with_pbr(s.material)

    core = f"Generate a high-end architectural visualization of a {s.tipe}. Focus on the {arch_type_context}. Design style: {s.gaya}. "
    
    if s.uploaded_sketch is not None:
        core += "\n\n[CRITICAL VISION INSTRUCTION]: Analyze the exact geometry, proportions, and rooflines of the ATTACHED SKETCH. Map the requested materials exactly onto this structural wireframe. DO NOT invent new building shapes.\n\n"
    if s.use_ref:
        core += "Please match the overall mood, color palette, and lighting style of the ATTACHED REFERENCE IMAGE. "

    if "Auto" not in s.lensa_khusus:
        lens = s.lensa_khusus.split(" (")[0]
    else:
        lens = "Use wide angle 24mm lens" if is_interior else "Use 35mm-50mm lens"
        
    camera_setup = s.kamera_film.split(" (")[0]
    core += f"Perspective & View: {s.view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. Presentation Style: {style_description}. "
    
    weathering = s.weathering.split(" (")[0]
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. Material Condition/Weathering: {weathering}. "
    
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

    core += f"Site Context: {tapak}. Landscaping: {vegetasi}. {lighting_setup} Cinematic Storytelling: {s.skenario}. "
    
    if s.detail:
        core += f"Additional details: {s.detail}. "
        
    core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {s.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {db.DB_RASIO[s.rasio]}."

    s.generated_prompt = core
    s.conflicts = check_conflicts(s)

    # --- FASE 3: MENYIMPAN KE PROMPT LEDGER (RIWAYAT) ---
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    title = f"[{timestamp}] {s.tipe.split(' ')[0]} - {s.suasana.split(' ')[0]}"
    
    # Mencegah duplikasi riwayat yang sama persis secara berurutan
    if not s.history_ledger or s.history_ledger[0]['prompt'] != core:
        s.history_ledger.insert(0, {"title": title, "prompt": core})
        # Batasi riwayat maksimal 10
        if len(s.history_ledger) > 10:
            s.history_ledger.pop()
