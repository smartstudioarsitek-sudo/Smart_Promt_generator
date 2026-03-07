# prompt_logic.py
import streamlit as st
import datetime
import re
import database_params as db

def enhance_with_pbr(material_string):
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
    
    # 🛠️ PERBAIKAN PRIORITAS 3 & CASE SENSITIVITY
    # Biarkan string asli utuh, jangan di-.lower() agar merek komersial (Zaha Hadid, Kodak, Alucobond) tidak rusak.
    enhanced = material_string 
    
    # Mengurutkan dari kata terpanjang ke terpendek agar "batu" tidak merusak "batu bata"
    sorted_keys = sorted(pbr_dictionary.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        # Gunakan regex \b (word boundary) dipadukan dengan re.IGNORECASE
        # Dengan ini, sistem bisa mendeteksi kata "Kayu", "KAYU", atau "kayu" 
        # TANPA harus mengubah sisa kalimat menjadi huruf kecil semua.
        pattern = re.compile(r'\b' + re.escape(key) + r'\b', re.IGNORECASE)
        enhanced = pattern.sub(pbr_dictionary[key], enhanced)
        
    return enhanced

def check_conflicts(s):
    conflicts = []
    
    # 🛠️ PERBAIKAN PRIORITAS 2: Gunakan getattr untuk menghindari AttributeError
    view = getattr(s, 'view', '')
    suasana = getattr(s, 'suasana', '')
    fixture_ext = getattr(s, 'fixture_ext', '')
    fixture_int = getattr(s, 'fixture_int', '')
    lensa_khusus = getattr(s, 'lensa_khusus', '')
    cuaca = getattr(s, 'cuaca', '')
    presentasi = getattr(s, 'presentasi', '')
    mode_render = getattr(s, 'mode_render', '')
    uploaded_sketch = getattr(s, 'uploaded_sketch', None)

    is_interior = "[INT]" in view
    is_night = any(k in suasana.lower() for k in ["night", "twilight", "sunset"])

    if is_night and ("Tanpa" in fixture_ext if not is_interior else "Tanpa" in fixture_int):
        conflicts.append("⚠️ **Peringatan Cahaya:** Anda memilih waktu Malam/Senja, tetapi **tidak memilih Fixture Lampu**. Render mungkin akan terlalu gelap atau kehilangan detail.")

    if "Drone" in view and "Macro" in lensa_khusus:
        conflicts.append("⚠️ **Peringatan Optik:** *Drone View* tidak logis dipadukan dengan *Lensa Macro*. Skala bangunan akan terlihat seperti miniatur mainan.")

    if is_interior and ("Rain" in cuaca or "Fog" in cuaca):
        conflicts.append("💡 **Saran Lingkungan:** Anda merender Interior dengan cuaca Hujan/Kabut di luar. Pastikan desain Anda memiliki jendela kaca besar agar efek cuaca ini terlihat dari dalam.")
        
    if uploaded_sketch is None and "Technical Concept" in presentasi:
        conflicts.append("⚠️ **Peringatan Presisi Geometri:** Anda menargetkan render konseptual teknis tetapi tidak mengunggah sketsa (Vision Constraint mati). Hasil render berisiko mengalami 'halusinasi' struktural AI.")
    
    if "Video" in mode_render and not getattr(s, 'engine_video', None):
        conflicts.append("⚠️ **Peringatan Koherensi Temporal:** Pastikan menggunakan prompt ini pada engine video berarsitektur NeRF (seperti Luma atau Kling) untuk menghindari flickering struktur.")
# 🛠️ PERBAIKAN PRIORITAS 4: Pencegahan Halusinasi Color Masking Kosong
    use_masking = getattr(s, 'use_color_masking', False)
    if use_masking:
        mask_values = [
            getattr(s, 'mask_white', ''), getattr(s, 'mask_gray', ''), getattr(s, 'mask_dark', ''),
            getattr(s, 'mask_brown', ''), getattr(s, 'mask_brick', ''), getattr(s, 'mask_blue', ''),
            getattr(s, 'mask_cream', ''), getattr(s, 'mask_green', '')
        ]
        # Jika semua nilai kosong atau hanya spasi
        if all(not val or not str(val).strip() for val in mask_values):
            conflicts.append("⚠️ **Peringatan Masking:** Fitur 'Semantic Color Masking' aktif, tetapi Anda tidak mendefinisikan satupun material. Pemetaan warna akan diabaikan oleh sistem agar AI tidak berhalusinasi.")
            
    return conflicts

def construct_prompt():
    s = st.session_state
    
    # 🛠️ PERBAIKAN PRIORITAS 2: Ekstraksi Variabel Aman dengan Nilai Bawaan Defensif
    view = getattr(s, 'view', db.DB_VIEW[0])
    tipe = getattr(s, 'tipe', db.DB_TIPE[0])
    gaya = getattr(s, 'gaya', db.DB_GAYA[0])
    material = getattr(s, 'material', db.DB_MATERIAL[0])
    suasana = getattr(s, 'suasana', db.DB_SUASANA[0])
    cuaca = getattr(s, 'cuaca', db.DB_CUACA_SIANG[0])
    temp_warna = getattr(s, 'temp_warna', db.DB_TEMP_WARNA[0])
    teknik_cahaya = getattr(s, 'teknik_cahaya', db.DB_TEKNIK_CAHAYA[0])
    lensa_khusus = getattr(s, 'lensa_khusus', db.DB_LENSA_KHUSUS[0])
    kamera_film = getattr(s, 'kamera_film', db.DB_KAMERA_FILM[0])
    weathering = getattr(s, 'weathering', db.DB_WEATHERING[0])
    tapak = getattr(s, 'tapak', db.DB_TAPAK[0])
    vegetasi = getattr(s, 'vegetasi', db.DB_VEGETASI[0])
    mode_render = getattr(s, 'mode_render', "📸 Image (Still Photo)")
    skenario = getattr(s, 'skenario', db.DB_SKENARIO[0])
    rasio = getattr(s, 'rasio', "Landscape (16:9)")
    detail = getattr(s, 'detail', "")
    
    is_interior = "[INT]" in view
    fixture = getattr(s, 'fixture_int', db.DB_FIXTURE_INT[0]) if is_interior else getattr(s, 'fixture_ext', db.DB_FIXTURE_EXT[0])
    
    arch_type_context = "interior architectural space" if is_interior else "exterior volumetric structure"
    pbr_material_desc = enhance_with_pbr(material)
    
    # --- 1. LINGKUNGAN & ATMOSFER ---
    lighting_setup = f"[ENVIRONMENTAL LIGHTING & ATMOSPHERE]: {suasana}. Weather conditions: {cuaca}. "
    if "Auto" not in temp_warna:
        lighting_setup += f"Artificial Light Color Temp: {temp_warna.split(' (')[0]}. "
        
    if "Tanpa" not in fixture:
        lighting_setup += f"Specific Lighting Fixtures: {fixture.split(' (')[0]}. "
        
    if "Standard" not in teknik_cahaya:
        lighting_setup += f"Advanced Lighting Technique: {teknik_cahaya.split(' (')[0]}. "

    # --- 2. SUBJEK ARSITEKTUR & GEOMETRI ---
    base_arch = f"[ARCHITECTURAL SUBJECT]: A high-end architectural visualization of a {tipe}. Focus on the {arch_type_context}. Design style: {gaya}. "
    
    uploaded_sketch = getattr(s, 'uploaded_sketch', None)
    if uploaded_sketch is not None:
        ai_control = getattr(s, 'ai_control', db.DB_AI_CONTROL[0])
        base_arch += f"\n[LAYER 2 RESTRICTION: {ai_control.upper()}]. STRICT MANDATE: Geometry, structural proportions, and absolute elevations must 100% follow the topology of the uploaded sketch. DO NOT hallucinate basic architectural elements.\n"

        if getattr(s, 'use_color_masking', False):
            # Pemanggilan aman untuk masking warna
            mask_mapping = {
                "WHITE/LIGHT": getattr(s, 'mask_white', ''),
                "GRAY": getattr(s, 'mask_gray', ''),
                "DARK/BLACK": getattr(s, 'mask_dark', ''),
                "BROWN/WOOD-TONE": getattr(s, 'mask_brown', ''),
                "BRICK-RED/TERRACOTTA": getattr(s, 'mask_brick', ''),
                "LIGHT BLUE/TRANSPARENT": getattr(s, 'mask_blue', ''),
                "CREAM/YELLOW": getattr(s, 'mask_cream', ''),
                "GREEN": getattr(s, 'mask_green', '')
            }
            
            # 🛠️ PERBAIKAN: Saring hanya material yang benar-benar diisi oleh user
            active_masks = {zone: pbr_val for zone, pbr_val in mask_mapping.items() if pbr_val and str(pbr_val).strip()}
            
            # Jika ada minimal 1 material yang valid, baru cetak mandat ke dalam prompt
            if active_masks:
                base_arch += "\n[MATERIAL MAPPING MANDATE]: Strictly map the following PBR materials to their corresponding visual color zones in the attached sketch/reference image:\n"
                
                for zone, pbr_val in active_masks.items():
                    base_arch += f"- {zone} SURFACES: {enhance_with_pbr(pbr_val)}\n"
                
                base_arch += "CRITICAL: DO NOT mix materials. Maintain sharp material transitions exactly as defined by the visual boundaries of these specific colors in the base image.\n"
                       
    if getattr(s, 'use_ref', False):
        base_arch += "Please match the overall mood, color palette, and lighting style of the ATTACHED REFERENCE IMAGE. "
    # --- 3. KOMPOSISI FOTOGRAFI & KAMERA ---
    if "Auto" not in lensa_khusus:
        lens = lensa_khusus.split(" (")[0]
    else:
        lens = "Use wide angle 24mm lens" if is_interior else "Use 35mm-50mm lens"
        
    camera_setup = kamera_film.split(" (")[0]
    
    # 🛠️ FASE 3: INJEKSI STANDAR 2G STUDIO (Koreksi Distorsi Optik)
    tilt_shift_mandate = ""
    if "Tilt-Shift" in lensa_khusus:
        tilt_shift_mandate = (
            "[OPTICAL CORRECTION MANDATE]: Enforce absolute 2-point perspective. "
            "Vertical lines of the architecture MUST remain perfectly straight, plumb, and parallel to the frame edges. "
            "NEGATIVE PROMPT: --no perspective distortion, converging vertical lines, keystone effect, warped structural geometry. "
        )
    
    composition_macros = (
        "[CINEMATIC COMPOSITION DIRECTIVES]: Strictly apply Rule of Thirds composition. "
        "Integrate natural leading lines converging towards the main architectural subject. "
        "Establish spatial scale using realistic depth of field with subtle blurred foreground elements (e.g., foliage or silhouettes). "
        f"{tilt_shift_mandate}"
    )
    # --- 4. MATERIAL & KONTEKS SITE ---
    context_setup = f"Physically Based Base Materials: {pbr_material_desc}. Material Condition/Weathering: {weathering.split(' (')[0]}. "
    context_setup += f"Site Context: {tapak.split(' (')[0]}. Landscaping: {vegetasi.split(' (')[0]}. "

    # 🛠️ FASE 3 (GRAND FINALE): INJEKSI STANDAR KUNKUN VISUAL (Cross-Override & Storytelling)
    
    # A. Sabotase Cuaca Terhadap Material (Weather-Material Override)
    if "Rain" in cuaca or "Hujan" in cuaca:
        context_setup += "[WEATHER-MATERIAL OVERRIDE]: Ground surfaces (especially asphalt or hardscapes) MUST be rendered as heavily puddled wet surfaces with extreme specular environmental and neon light bounce, exhibiting diffuse anisotropic water reflections. "
    elif "Mist" in cuaca or "Fog" in cuaca or "Kabut" in cuaca:
        context_setup += "[WEATHER-MATERIAL OVERRIDE]: Surfaces must exhibit subtle dampness, moisture clinging to material edges, and heavy atmospheric scattering reducing distant micro-contrast. "

    # B. Injeksi Skala Manusia & Penceritaan Emosional (Human Scale & Narrative)
    storytelling_mandate = ""
    # Jika skenario menghendaki elemen manusia atau vibe aktivitas sibuk
    if "Human" in skenario or "Lifestyle" in skenario or "Busy" in getattr(s, 'storytelling_vibe', ''):
        storytelling_mandate = "[CINEMATIC NARRATIVE]: Integrate scale-giving human figures exhibiting cinematic motion blur. Position them naturally to guide the eye towards the main architectural focal point, adding a profound sense of life, kinetic energy, and lived-in atmosphere. "
    else:
        # Skala halus untuk shot standar agar bangunan tidak terasa seperti kota mati
        storytelling_mandate = "[ARCHITECTURAL SCALE]: Subtly incorporate distant or partially obscured human silhouettes or signs of life (e.g., warm interior lighting hinting at occupancy) to establish realistic monumental proportions without distracting from the main geometry. "
        
    context_setup += storytelling_mandate
    

    # --- 5. PERAKITAN PROMPT FINAL & PERBAIKAN LOGIC BYPASS ---
    is_video = "Video" in mode_render
    
    if is_video:
        # Fallback cadangan jika pengguna memaksa render tanpa mengatur parameter video
        motion = getattr(s, 'camera_motion', db.DB_CAMERA_MOTION[0]).split(" (")[0]
        vibe = getattr(s, 'storytelling_vibe', db.DB_STORYTELLING_VIBE[0]).split(" (")[0]
        engine_video = getattr(s, 'engine_video', db.DB_ENGINE_VIDEO[0])
        
        core = f"{lighting_setup}\n\n"
        core += f"Cinematic architectural video sequence. [CAMERA CHOREOGRAPHY]: {motion}. [STORYTELLING & MICRO-DYNAMICS]: {vibe}. "
        core += f"{base_arch}\n{context_setup}\n"
        core += f"Perspective & View: {view}. Camera/Lens Spec: {lens}. Film Stock/Sensor: {camera_setup}. {composition_macros}\n"
        core += f"Quality: 8k resolution, ultra-fluid 60fps motion. Engine Target: {engine_video}. "
        core += "\n[CRITICAL TEMPORAL MANDATE]: Maintain absolute spatial and morphological coherence. Zero flickering, zero structural melting, and no identity drift during camera movement. Enforce NeRF-like spatial understanding."
    else:
        presentasi_val = getattr(s, 'presentasi', list(db.DB_PRESENTASI.keys())[0])
        style_description = db.DB_PRESENTASI.get(presentasi_val, db.DB_PRESENTASI[list(db.DB_PRESENTASI.keys())[0]])
        engine = getattr(s, 'engine', db.DB_ENGINE[0])
        
        core = f"{lighting_setup}\n\n"
        core += f"{base_arch}\n"
        core += f"{context_setup}\n"
        core += f"Camera & Optics: Perspective {view}. {lens}. {camera_setup}. {composition_macros}\n"
        core += f"Presentation Style: {style_description}. Cinematic Storytelling: {skenario}. "
        core += "\n[POST-PRODUCTION REQUIREMENT]: If supported by the generation engine, simulate or prepare output for Multi-pass EXR extraction including Z-Depth maps, Ambient Occlusion, Specular Highlights, and Cryptomatte ID masks for deep material logic editing. "
        
    if detail:
        core += f"\nAdditional architectural details: {detail}. "
        
    rasio_val = db.DB_RASIO.get(rasio, "16:9")
    if is_video:
        core += f"\nQuality: 8k resolution, ultra-fluid 60fps motion, cinematic global illumination, highly realistic physics. Aspect Ratio: {rasio_val}."
    else:
        core += f"\nQuality: 4k resolution, hyper-realistic textures, cinematic global illumination, {engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text. Aspect Ratio: {rasio_val}."

    s.generated_prompt = core
    s.conflicts = check_conflicts(s)

    # Sistem pelacakan Ledger yang sudah diamankan
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    mode_tag = "[VID]" if is_video else "[IMG]"
    title = f"{mode_tag} [{timestamp}] {tipe.split(' ')[0]} - {suasana.split(' ')[0]}"
    
    history_ledger = getattr(s, 'history_ledger', [])
    if not history_ledger or history_ledger[0]['prompt'] != core:
        history_ledger.insert(0, {"title": title, "prompt": core})
        if len(history_ledger) > 10:
            history_ledger.pop()
    s.history_ledger = history_ledger
