# app.py
import streamlit as st
import random
import database_params as db
import prompt_logic as pl

# ==========================================
# 1. INITIALIZE SESSION STATE
# ==========================================
if 'init' not in st.session_state:
    st.session_state.init = True
    
    # Set default values from database
    st.session_state.tipe = db.DB_TIPE[0]
    st.session_state.gaya = db.DB_GAYA[0]
    st.session_state.material = db.DB_MATERIAL[0]
    st.session_state.suasana = db.DB_SUASANA[0]
    st.session_state.cuaca = db.DB_CUACA_SIANG[0] # Default Cuaca
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
    st.session_state.use_sketch = False
    st.session_state.use_ref = False
    st.session_state.generated_prompt = ""
    st.session_state.weathering = db.DB_WEATHERING[0]
    st.session_state.kamera_film = db.DB_KAMERA_FILM[0]
    st.session_state.lensa_khusus = db.DB_LENSA_KHUSUS[0]

def handle_random():
    s = st.session_state
    s.tipe = random.choice(db.DB_TIPE)
    s.gaya = random.choice(db.DB_GAYA)
    s.material = random.choice(db.DB_MATERIAL)
    s.suasana = random.choice(db.DB_SUASANA)
    s.view = random.choice(db.DB_VIEW)
    s.skenario = random.choice(db.DB_SKENARIO)
    s.engine = random.choice(db.DB_ENGINE)

# ==========================================
# 2. UI RENDER (Streamlit Layout)
# ==========================================
st.set_page_config(page_title="SmartBIM Engineex v2.1", layout="wide", initial_sidebar_state="collapsed")

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
    st.markdown('<div class="header-box"><div style="display:flex; flex-direction:column;"><h1 class="title-text">SmartBIM Engineex <span style="color:#4338ca">v2.1</span></h1><p class="subtitle-text">Enterprise Prompt Builder</p></div></div>', unsafe_allow_html=True)
with col_head2:
    st.write("") 
    if st.button("🔄 Acak Parameter", use_container_width=True):
        handle_random()
        st.rerun()

col_left, col_right = st.columns([6, 6], gap="large")

# --- KIRI: PANEL INPUT (SISTEM TAB) ---
with col_left:
    # Membuat 4 Tab Utama
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Geometri & Material", "💡 Tata Cahaya", "🌍 Konteks Lingkungan", "📷 Sinema & Lensa"])
    
    with tab1:
        st.session_state.tipe = st.selectbox("Kategori Bangunan", db.DB_TIPE, index=db.DB_TIPE.index(st.session_state.tipe))
        st.session_state.gaya = st.selectbox("Gaya Arsitektur", db.DB_GAYA, index=db.DB_GAYA.index(st.session_state.gaya))
        st.session_state.material = st.selectbox("Material Utama (PBR)", db.DB_MATERIAL, index=db.DB_MATERIAL.index(st.session_state.material))
        
        # Tambahan Fase 2: Weathering
        st.session_state.weathering = st.selectbox("Kondisi Fisik / Keausan Material", db.DB_WEATHERING, index=db.DB_WEATHERING.index(st.session_state.weathering))
        
        st.session_state.detail = st.text_area("Detail Spesifik Khusus (Struktur/Bentuk)", value=st.session_state.detail, height=80)

    # ... (Biarkan tab2 dan tab3 seperti aslinya) ...
    

    with tab2:
        st.session_state.temp_warna = st.selectbox("Suhu Warna Lampu (Kelvin)", db.DB_TEMP_WARNA, index=db.DB_TEMP_WARNA.index(st.session_state.temp_warna))
        
        # Logika dinamis untuk Fixture
        is_interior_ui = "[INT]" in st.session_state.view
        if is_interior_ui:
            st.session_state.fixture_int = st.selectbox("Interior Lighting Fixtures", db.DB_FIXTURE_INT, index=db.DB_FIXTURE_INT.index(st.session_state.fixture_int))
        else:
            st.session_state.fixture_ext = st.selectbox("Exterior Lighting Fixtures", db.DB_FIXTURE_EXT, index=db.DB_FIXTURE_EXT.index(st.session_state.fixture_ext))
            
        st.session_state.teknik_cahaya = st.selectbox("Teknik Render Cahaya Tambahan", db.DB_TEKNIK_CAHAYA, index=db.DB_TEKNIK_CAHAYA.index(st.session_state.teknik_cahaya))

    with tab3:
        st.session_state.suasana = st.selectbox("Waktu & Pencahayaan Alami", db.DB_SUASANA, index=db.DB_SUASANA.index(st.session_state.suasana))
        
        # LOGIKA DINAMIS TINGKAT LANJUT: Cuaca berdasarkan Waktu
        is_night = any(k in st.session_state.suasana.lower() for k in ["night", "twilight", "sunset"])
        
        if is_night:
            st.session_state.cuaca = st.selectbox("Kondisi Atmosfer (Malam)", db.DB_CUACA_MALAM)
        else:
            st.session_state.cuaca = st.selectbox("Kondisi Atmosfer (Siang)", db.DB_CUACA_SIANG)
            
        st.session_state.skenario = st.selectbox("Skenario / Lingkungan", db.DB_SKENARIO, index=db.DB_SKENARIO.index(st.session_state.skenario))

    with tab4:
        st.session_state.view = st.selectbox("Kamera & Perspektif", db.DB_VIEW, index=db.DB_VIEW.index(st.session_state.view))
        
        # Tambahan Fase 2: Lensa & Kamera
        st.session_state.lensa_khusus = st.selectbox("Lensa Arsitektur Khusus", db.DB_LENSA_KHUSUS, index=db.DB_LENSA_KHUSUS.index(st.session_state.lensa_khusus))
        st.session_state.kamera_film = st.selectbox("Jenis Kamera & Film Stock", db.DB_KAMERA_FILM, index=db.DB_KAMERA_FILM.index(st.session_state.kamera_film))
        
        st.session_state.rasio = st.selectbox("Rasio Gambar", list(db.DB_RASIO.keys()), index=list(db.DB_RASIO.keys()).index(st.session_state.rasio))
        st.session_state.presentasi = st.selectbox("Gaya Render", list(db.DB_PRESENTASI.keys()), index=list(db.DB_PRESENTASI.keys()).index(st.session_state.presentasi))
        st.session_state.engine = st.selectbox("Render Engine", db.DB_ENGINE, index=db.DB_ENGINE.index(st.session_state.engine))
    

    st.markdown("---")
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        st.session_state.use_sketch = st.checkbox("Lampirkan Sketsa (CRITICAL)", value=st.session_state.use_sketch)
    with col_cb2:
        st.session_state.use_ref = st.checkbox("Lampirkan Referensi Style", value=st.session_state.use_ref)

    if st.button("✨ SUSUN PROMPT NEURAL", use_container_width=True, type="primary"):
        pl.construct_prompt()

# --- KANAN: PANEL OUTPUT ---
with col_right:
    st.subheader("🖥️ Hasil Neural Prompt")
    
    if st.session_state.generated_prompt:
        st.success("✅ Prompt Profesional siap! Copy teks di bawah ini dan paste ke Gemini Advanced.")
        st.code(st.session_state.generated_prompt, language="plaintext")
        if st.session_state.use_sketch or st.session_state.use_ref:
            st.warning("⚠️ **PENTING:** Upload file gambar Anda ke dalam kolom chat Gemini bersamaan dengan mem-paste prompt ini!")
    else:
        st.info("👈 Silakan jelajahi 4 Tab di sebelah kiri, sesuaikan parameter, lalu klik **SUSUN PROMPT NEURAL**.")
