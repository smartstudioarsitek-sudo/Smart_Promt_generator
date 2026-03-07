# prompt_logic.py
import streamlit as st
import datetime
import database_params as db

def enhance_with_pbr(material_string):
    # ... (fungsi ini biarkan sama seperti sebelumnya) ...
    if not material_string:
        return ""
    pbr_dictionary = {
        "concrete": "exposed raw concrete with mathematical displacement maps, subtle moisture staining, and micro-surface roughness",
        "wood": "timber wood with deep matte visible grain, authentic contact shadows, and signs of subtle aging (organized chaos)",
        "kayu": "natural timber wood panels with detailed matte grain, subtle imperfections, and realistic warm bounce light",
        "marble": "highly polished marble with sharp specular reflections, subsurface scattering, and slight wear on high-traffic areas",
        "steel": "weathered steel with natural oxidation, diffuse roughness maps, and realistic metallic micro-imperfections",
        "glass": "ultra-clear architectural glass with realistic index of refraction and sharp environmental reflections",
        "brick": "rough terracotta masonry with displacement mapping and ambient occlusion in crevices",
        "cat": "smooth matte architectural wall paint (stucco/plaster) with subtle micro-bump textures to catch sunlight realistically",
        "aluminium": "anodized aluminium frames with brushed metallic finish and realistic anisotropic reflections",
        "andesit": "rough cut andesite stone masonry with strong normal maps and ambient occlusion",
        "batu": "natural stone cladding with deep displacement and distinct mortar joints"
    }
    enhanced = material_string.lower()
    for key, value in pbr_dictionary.items():
        if key in enhanced:
            enhanced = enhanced.replace(key, value)
    return enhanced

def check_conflicts(s):
    # ... (fungsi ini biarkan sama seperti sebelumnya) ...
    conflicts = []
    is_interior = "[INT]" in s.view
    is_night = any(k in s.suasana.lower() for k in ["night", "twilight"])

    if is_night and ("Tanpa" in s.fixture_ext if not is_interior else "Tanpa" in s.fixture_int):
        conflicts.append("⚠️ **Peringatan Cahaya:** Anda memilih waktu Malam/Senja, tetapi **tidak memilih Fixture Lampu**. Render mungkin akan terlalu gelap atau kehilangan detail.")

    if "Drone" in s.view and "Macro" in s.lensa_khusus:
        conflicts.append("⚠️ **Peringatan Optik:** *Drone View* tidak logis dipadukan dengan *Lensa Macro*. Skala bangunan akan terlihat seperti miniatur mainan.")

    if is_interior and ("Rain" in s.cuaca or "Fog" in s.cuaca):
        conflicts.append("💡 **Saran Lingkungan:** Anda merender Interior dengan cuaca Hujan/Kabut di luar. Pastikan desain Anda memiliki jendela kaca besar agar efek cuaca ini terlihat dari dalam.")
        
    if s.uploaded_sketch is None and "Technical Concept" in s.presentasi:
        conflicts.append("⚠️ **Peringatan Presisi Geometri:** Anda menargetkan render konseptual teknis tetapi tidak mengunggah sketsa (Vision Constraint mati). Hasil render berisiko mengalami 'halusinasi' struktural AI.")
    
    if "Video" in s.mode_render and not hasattr(s, 'engine_video'):
        conflicts.append("⚠️ **Peringatan Koherensi Temporal:** Pastikan menggunakan prompt ini pada engine video berarsitektur NeRF (seperti Luma atau Kling) untuk menghindari flickering struktur.")

    return conflicts

def construct_prompt():
    s = st.session_state
    
    is_interior = "[INT]" in s.view
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    pbr_material_desc = enhance_with_pbr(s.material)
    
    # --- 1. LINGKUNGAN & ATMOSFER (Prioritas Kunkun Visual) ---
    # Ditempatkan paling awal agar AI mengunci "mood" dan "suhu cahaya" lebih dulu
    lighting_setup = f"[ENVIRONMENTAL LIGHTING & ATMOSPHERE]: {s.suasana}. Weather conditions: {s.cuaca}. "
    if "Auto" not in s.temp_warna:
        lighting_setup += f"Artificial Light Color Temp: {s.temp_warna.split(' (')[0]}. "
        
    fixture = s.fixture_int if is_interior else s.fixture_ext
    if "Tanpa" not in fixture:
        lighting_setup += f"Specific Lighting Fixtures: {fixture.split(' (')[0]}. "
        
    if "Standard" not in s.teknik_cahaya:
        lighting_setup += f"Advanced Lighting Technique: {s.teknik_cahaya.split(' (')[0]}. "

    # --- 2. SUBJEK ARSITEKTUR & GEOMETRI ---
    base_arch = f"[ARCHITECTURAL SUBJECT]: A high-end architectural visualization of a {s.tipe}. Focus on the {arch_type_context}. Design style: {s.gaya}. "
    
    if s.uploaded_sketch is not None:
        base_arch += f"\n[LAYER 2 RESTRICTION: {s.ai_control.upper()}]. STRICT MANDATE: Geometry, structural proportions, and absolute elevations must 100% follow the topology of the uploaded sketch. DO NOT hallucinate basic architectural elements.\n"
        
        # LOGIKA VISUAL COLOR MASKING (SKETCHUP STANDARDS)
        if s.use_color_masking:
            base_arch += "\n[MATERIAL MAPPING MANDATE]: Strictly map the following PBR materials to their corresponding visual color zones in the attached sketch/reference image:\n"
            if s.mask_white: base_arch += f"- WHITE/LIGHT SURFACES: {enhance_with_pbr(s.mask_white)}\n"
            if s.mask_gray: base_arch += f"- GRAY SURFACES: {enhance_with_pbr(s.mask_gray)}\n"
            if s.mask_dark: base_arch += f"- DARK/BLACK SURFACES: {enhance_with_pbr(s.mask_dark)}\n"
            if s.mask_brown: base_arch += f"- BROWN/WOOD-TONE SURFACES: {enhance_with_pbr(s.mask_brown)}\n"
            if s.mask_brick: base_arch += f"- BRICK-RED/TERRACOTTA SURFACES: {enhance_with_pbr(s.mask_brick)}\n"
            if s.mask_blue: base_arch += f"- LIGHT BLUE/TRANSPARENT SURFACES: {enhance_with_pbr(s.mask_blue)}\n"
            if s.mask_cream: base_arch += f"- CREAM/YELLOW SURFACES: {enhance_with_pbr(s.mask_cream)}\n"
            if s.mask_green: base_arch += f"- GREEN SURFACES: {enhance_with_pbr(s.mask_green)}\n"
            base_arch += "CRITICAL: DO NOT mix materials. Maintain sharp material transitions exactly as defined by the visual boundaries of these specific colors in the base image.\n"
        
                    
    if s.use_ref:
        base_arch += "Please match the overall mood, color palette, and lighting style of the ATTACHED REFERENCE IMAGE. "

    # --- 3. KOMPOSISI FOTOGRAFI & KAMERA (Prioritas 2G Studio) ---
    if "Auto" not in s.lensa_khusus:
        lens = s.lensa_khusus.split(" (")[0]
    else:
        lens = "Use wide angle 24mm lens" if is_interior else "Use 35mm-50mm lens"
        
    camera_setup = s.kamera_film.split(" (")[0]
    
    # Makro tersembunyi untuk mendisiplinkan AI (Rule of Thirds, dll)
    composition_macros = (
        "[CINEMATIC COMPOSITION DIRECTIVES]: Strictly apply Rule of Thirds composition. "
        "Integrate natural leading lines converging towards the main architectural subject. "
        "Establish spatial scale using realistic depth of field with subtle blurred foreground elements (e.g., foliage or silhouettes)."
    )

    # --- 4. MATERIAL & KONTEKS SITE ---
    context_setup = f"Physically Based Base Materials: {pbr_material_desc}. Material Condition/Weathering: {s.weathering.split(' (')[0]}. "
    context_setup += f"Site Context: {s.tapak.split(' (')[0]}. Landscaping: {s.vegetasi.split(' (')[0]}. "

    # --- 5. PERAKITAN PROMPT FINAL (Berdasarkan Hierarki) ---
    is_video = "Video" in s.mode_render
    
    if is_video:
        motion = s.camera_motion.split(" (")[0]
        vibe = s.storytelling_vibe.split(" (")[0]
        
        core = f"{lighting_setup}\n\n"
        core += f"Cinematic architectural video sequence. [CAMERA CHOREOGRAPHY]: {motion}. [STORYTELLING & MICRO-DYNAMICS]: {vibe}. "
        core += f"{base_arch}\n{context_setup}\n"
        core += f"Perspective & View: {s.view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. {composition_macros}\n"
        core += f"Quality: 8k resolution, ultra-fluid 60fps motion. Engine Target: {s.engine_video}. "
        core += "\n[CRITICAL TEMPORAL MANDATE]: Maintain absolute spatial and morphological coherence. Zero flickering, zero structural melting, and no identity drift during camera movement. Enforce NeRF-like spatial understanding."
    else:
        style_description = db.DB_PRESENTASI[s.presentasi]
        
        # Eksekusi Perakitan Terstruktur
        core = f"{lighting_setup}\n\n"
        core += f"{base_arch}\n"
        core += f"{context_setup}\n"
        core += f"Camera & Optics: Perspective {s.view}. {lens}. {camera_setup}. {composition_macros}\n"
        core += f"Presentation Style: {style_description}. Cinematic Storytelling: {s.skenario}. "
        
        core += "\n[POST-PRODUCTION REQUIREMENT]: If supported by the generation engine, simulate or prepare output for Multi-pass EXR extraction including Z-Depth maps, Ambient Occlusion, Specular Highlights, and Cryptomatte ID masks for deep material logic editing. "
        
    if s.detail:
        core += f"\nAdditional architectural details: {s.detail}. "
        
    if is_video:
        core += f"\nQuality: 8k resolution, ultra-fluid 60fps motion, cinematic global illumination, highly realistic physics. Aspect Ratio: {db.DB_RASIO[s.rasio]}."
    else:
        core += f"\nQuality: 4k resolution, hyper-realistic textures, cinematic global illumination, {s.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {db.DB_RASIO[s.rasio]}."

    s.generated_prompt = core
    s.conflicts = check_conflicts(s)

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    mode_tag = "[VID]" if is_video else "[IMG]"
    title = f"{mode_tag} [{timestamp}] {s.tipe.split(' ')[0]} - {s.suasana.split(' ')[0]}"
    
    if not s.history_ledger or s.history_ledger[0]['prompt'] != core:
        s.history_ledger.insert(0, {"title": title, "prompt": core})
        if len(s.history_ledger) > 10:
            s.history_ledger.pop()
