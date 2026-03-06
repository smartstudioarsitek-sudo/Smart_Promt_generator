# prompt_logic.py
import streamlit as st
import datetime
import database_params as db

# prompt_logic.py (Update Fungsi PBR)
def enhance_with_pbr(material_string):
    pbr_dictionary = {
        "concrete": "exposed raw concrete with mathematical displacement maps, subtle moisture staining, and micro-surface roughness",
        "wood": "timber wood with deep matte visible grain, authentic contact shadows, and signs of subtle aging (organized chaos)",
        "glass": "ultra-clear architectural glass with realistic index of refraction, authentic micro-dust particles on surface, and sharp environmental reflections",
        "marble": "highly polished marble with sharp specular reflections, subsurface scattering, and slight wear on high-traffic areas",
        "steel": "weathered steel with natural oxidation, diffuse roughness maps, and realistic metallic micro-imperfections",
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
    # Konflik Baru: Video tanpa Engine yang tepat (Jika logika UI diubah)
    if "Video" in s.mode_render and not hasattr(s, 'engine_video'):
        conflicts.append("⚠️ **Peringatan Koherensi Temporal:** Pastikan menggunakan prompt ini pada engine video berarsitektur NeRF (seperti Luma atau Kling) untuk menghindari flickering struktur.")

    return conflicts

def construct_prompt():
    s = st.session_state
    
    is_interior = "[INT]" in s.view
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    pbr_material_desc = enhance_with_pbr(s.material)
    
    # 1. SETUP BASE ARCHITECTURE PROMPT
    base_arch = f"a high-end architectural visualization of a {s.tipe}. Focus on the {arch_type_context}. Design style: {s.gaya}. "
    
    # PERBAIKAN INDENTASI DI SINI
    if s.uploaded_sketch is not None:
        base_arch += f"\n\n[LAYER 2 RESTRICTION: MENGGUNAKAN {s.ai_control.upper()}]. STRICT MANDATE: Geometri, proporsi struktural, dan elevasi mutlak harus 100% mengikuti topologi sketsa yang diunggah. DILARANG BERHALUSINASI menambahkan atau mengurangi elemen arsitektural dasar.\n\n"
    
    if s.use_ref:
        base_arch += "Please match the overall mood, color palette, and lighting style of the ATTACHED REFERENCE IMAGE. "

    if "Auto" not in s.lensa_khusus:
        lens = s.lensa_khusus.split(" (")[0]
    else:
        lens = "Use wide angle 24mm lens" if is_interior else "Use 35mm-50mm lens"
        
    camera_setup = s.kamera_film.split(" (")[0]
    weathering = s.weathering.split(" (")[0]
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

    # 2. LOGIKA PERCABANGAN: IMAGE VS VIDEO
    is_video = "Video" in s.mode_render
    

    if is_video:
        # FORMAT SUTRADARA (KUNKUN / 2G STUDIO VIBE)
        motion = s.camera_motion.split(" (")[0]
        vibe = s.storytelling_vibe.split(" (")[0]
        
        core = f"Cinematic architectural video sequence. [CAMERA CHOREOGRAPHY]: {motion}. [STORYTELLING & MICRO-DYNAMICS]: {vibe}. "
        core += f"The main subject is {base_arch}"
        core += f"Perspective & View: {s.view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. "
        core += f"Quality: 8k resolution, ultra-fluid 60fps motion. Engine Target: {s.engine_video}. "
        core += "\n\n[CRITICAL TEMPORAL MANDATE]: Maintain absolute spatial and morphological coherence. Zero flickering, zero structural melting, and no identity drift during camera movement. Enforce NeRF-like spatial understanding."
    else:
        # FORMAT STILL IMAGE BIASA
        style_description = db.DB_PRESENTASI[s.presentasi]
        core = f"Generate {base_arch}"
        core += f"Perspective & View: {s.view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. Presentation Style: {style_description}. "
    
    # 3. GABUNGKAN ELEMEN BERSAMA (MATERIAL, LINGKUNGAN, DLL)
    core += f"Physically Based Materials (PBR): {pbr_material_desc}. Material Condition/Weathering: {weathering}. "
    core += f"Site Context: {tapak}. Landscaping: {vegetasi}. {lighting_setup} "
    
    if not is_video:
        core += f"Cinematic Storytelling: {s.skenario}. " # Di image masuk skenario biasa
        core += "\n\n[POST-PRODUCTION REQUIREMENT]: If supported by the generation engine, simulate or prepare output for Multi-pass EXR extraction including Z-Depth maps, Ambient Occlusion, Specular Highlights, and Cryptomatte ID masks for deep material logic editing."
        
    if s.detail:
        core += f"Additional architectural details: {s.detail}. "
        
    if is_video:
        core += f"Quality: 8k resolution, ultra-fluid 60fps motion, cinematic global illumination, highly realistic physics. Aspect Ratio: {db.DB_RASIO[s.rasio]}."
    else:
        core += f"Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, {s.engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {db.DB_RASIO[s.rasio]}."

    s.generated_prompt = core
    s.conflicts = check_conflicts(s)

    # --- SIMPAN KE PROMPT LEDGER (RIWAYAT) ---
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    mode_tag = "[VID]" if is_video else "[IMG]"
    title = f"{mode_tag} [{timestamp}] {s.tipe.split(' ')[0]} - {s.suasana.split(' ')[0]}"
    
    if not s.history_ledger or s.history_ledger[0]['prompt'] != core:
        s.history_ledger.insert(0, {"title": title, "prompt": core})
        if len(s.history_ledger) > 10:
            s.history_ledger.pop()

