import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Home, Layers, Palette, Sun, Camera, Settings, Sparkles, 
  Image as ImageIcon, Download, RefreshCw, Cpu, PenTool, 
  Info, Upload, Lock, Unlock, X, AlertCircle, Video, CheckCircle
} from 'lucide-react';

// ==========================================
// 1. DATABASE & CONFIGURATIONS
// ==========================================
const DB_TIPE = [
  "Modern Minimalist House", "Grand Mosque (Masjid)", "Tropical Villa", 
  "Industrial Office", "Futuristic Skyscraper", "Bamboo Eco-Lodge",
  "Luxury Penthouse", "Cultural Center", "Parametric Pavilion",
  "Tropical Modern Townhouse"
];

const DB_GAYA = [
  "Futuristic", "Contemporary", "Islamic Modern", "Biophilic/Green", 
  "Brutalist", "Zaha Hadid Style", "Parametric Design", 
  "Scandinavian (Japandi)", "Industrial",
  "Tropical Brutalism with Exposed Brick"
];

const DB_MATERIAL = [
  "concrete, glass, and wood accents", "white marble and gold trim", 
  "exposed brick and steel", "sustainable bamboo and stone", 
  "reflective glass facade", "weathered corten steel",
  "polished travertin stone",
  "exposed terracotta brick, raw concrete, and warm timber wood"
];

const DB_SUASANA = [
  "Golden Hour (Sunset)", "Blue Hour (Twilight)", "Sunny Day", 
  "Foggy Morning", "Cinematic Night Lighting", "Rainy Cyberpunk Mood",
  "Overcast Soft Light", "Soft Morning Ambient Light"
];

const DB_VIEW = [
  "[EXT] Eye Level (Human View)", "[EXT] Drone / Bird's Eye View", "[EXT] Worm's Eye View (Low Angle)",
  "[INT] Eye Level (Human View)", "[INT] Wide Angle Interior", "[INT] Close-up Detail Shot"
];

const DB_PRESENTASI = {
  "📸 Clean Photorealistic": "clean, no text, pure photography style",
  "📏 Technical Concept": "architectural concept sheet style, mixed media, photorealistic render overlaid with hand-drawn technical annotations, dimension lines, measurement arrows, material callouts, handwritten notes, sketch aesthetic",
  "📝 Blueprint / Wireframe": "blueprint style, white lines on blue background, technical drawing, wireframe structural view",
  "🎨 Watercolor Sketch": "watercolor painting style, soft edges, artistic architectural sketch, ink outline"
};

const DB_SKENARIO = [
  "Standard Clear Architectural Shot",
  "Macro Foreground: Sharp focus on falling flower petals (Bokeh)",
  "Cinematic Wet Reflections: Rain puddles reflecting light",
  "Foggy Morning Mist: Thin mist with soft lighting",
  "Dramatic Interior Sunbeams: Sharp god rays on concrete",
  "Human Scale & Lifestyle: Featuring people on balcony",
  "Carport Focus: Luxury cars under concrete overhang"
];

const DB_RASIO = {
  "Landscape (16:9)": "16:9",
  "Portrait / Story (9:16)": "9:16",
  "Square / Feed (1:1)": "1:1",
  "Classic Photo (4:3)": "4:3",
  "Ultra Wide (4:1)": "4:1" 
};

const DB_ENGINE = ["Unreal Engine 5", "V-Ray", "Octane", "Corona", "Lumion"];

// ==========================================
// 2. UTILITY FUNCTIONS
// ==========================================
const enhanceWithPBR = (materialString) => {
  const pbrDictionary = {
    "concrete": "exposed raw concrete with micro-surface roughness and subtle moisture staining",
    "wood": "timber wood with deep matte visible grain and low specular reflectivity",
    "marble": "highly polished marble with sharp specular reflections and subsurface scattering",
    "steel": "weathered steel with natural oxidation, high metallic value, and diffuse roughness",
    "glass": "ultra-clear architectural glass with realistic index of refraction and sharp environmental reflections",
    "brick": "rough terracotta masonry with displacement mapping and ambient occlusion in crevices"
  };
  
  let enhanced = materialString.toLowerCase();
  for (const [key, value] of Object.entries(pbrDictionary)) {
    enhanced = enhanced.replace(key, value);
  }
  return enhanced;
};

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = (error) => reject(error);
  });
};

// ==========================================
// 3. CUSTOM HOOK: ASYNC VIDEO POLLING
// ==========================================
const useVideoPolling = (statusEndpoint) => {
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [pollingStatus, setPollingStatus] = useState("");
  const [error, setError] = useState(null);
  
  // Menggunakan useRef agar nilai delay persisten di dalam siklus rekursif
  const delayRef = useRef(5000); 

  const startPolling = useCallback(async (jobId) => {
    setIsVideoReady(false);
    setVideoUrl(null);
    setError(null);
    setPollingStatus("Menginisiasi render video di server...");
    delayRef.current = 5000; // Reset delay awal (5 detik)

    let isPollingActive = true;

    const poll = async () => {
      if (!isPollingActive) return;

      try {
        setPollingStatus("Mengecek status render video...");
        
        // PANGGILAN PRODUKSI KE BACKEND BFF
        const response = await fetch(`${statusEndpoint}?jobId=${jobId}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`Server API Error: ${response.status}`);
        
        const data = await response.json();
        // Ekspektasi respons Backend: { status: 'running' | 'completed' | 'failed', videoUrl?: 'https...' }

        if (data.status === 'completed' && data.videoUrl) {
          setPollingStatus("Render Video Selesai!");
          setIsVideoReady(true);
          setVideoUrl(data.videoUrl);
          isPollingActive = false; // Hentikan siklus
        } else if (data.status === 'failed') {
          throw new Error(data.message || "Pembuatan video gagal di sisi penyedia AI.");
        } else {
          // Status masih 'pending' atau 'running', terapkan Exponential Backoff
          setPollingStatus(`Merender... (Pengecekan ulang dalam ${delayRef.current / 1000} detik)`);
          delayRef.current = Math.min(delayRef.current * 1.5, 30000); // Maksimal delay 30 detik
          setTimeout(poll, delayRef.current);
        }

      } catch (err) {
        setError(err.message);
        setPollingStatus("Proses terhenti karena kesalahan.");
        isPollingActive = false;
      }
    };

    // Eksekusi siklus pertama
    setTimeout(poll, delayRef.current);

    return () => { isPollingActive = false; }; // Cleanup function
  }, [statusEndpoint]);

  return { isVideoReady, videoUrl, pollingStatus, error, startPolling };
};


// ==========================================
// 4. MAIN APPLICATION COMPONENT
// ==========================================
const App = () => {
  // --- STATE ---
  const [targetAi, setTargetAi] = useState('Gemini 3.1 Flash Image');
  const [formData, setFormData] = useState({
    tipe: DB_TIPE[0],
    gaya: DB_GAYA[0],
    material: DB_MATERIAL[0],
    suasana: DB_SUASANA[0],
    view: DB_VIEW[0],
    rasio: "Landscape (16:9)",
    presentasi: "📸 Clean Photorealistic",
    skenario: DB_SKENARIO[0],
    engine: DB_ENGINE[0],
    detail: "",
    lockSketch: true
  });
  
  const [sketchImage, setSketchImage] = useState(null);
  const [styleRefImage, setStyleRefImage] = useState(null);
  const [generatedPrompt, setGeneratedPrompt] = useState("");
  const [renderImage, setRenderImage] = useState(null);
  
  // Fitur Tambahan Gemini & Video
  const [useGrounding, setUseGrounding] = useState(true);
  const [motionPrompt, setMotionPrompt] = useState("Slow cinematic pan, maintaining strict structural rigidity and realistic lighting.");

  // Loading States
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRendering, setIsRendering] = useState(false);
  const [isVideoGenerating, setIsVideoGenerating] = useState(false);
  const [appErrorMsg, setAppErrorMsg] = useState(null);

  const fileInputSketch = useRef(null);
  const fileInputStyle = useRef(null);

  // Inisiasi Custom Hook Video
  const { 
      isVideoReady, 
      videoUrl, 
      pollingStatus, 
      error: videoError, 
      startPolling 
  } = useVideoPolling('/api/video/status'); // Ganti dengan endpoint BFF status video Anda

  // --- LOGIC: UPLOAD HANDLER ---
  const handleFileUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    setAppErrorMsg(null);
    
    // Validasi ukuran untuk model 3.1 Flash (Maks 7MB)
    if (file.size > 7 * 1024 * 1024) {
      setAppErrorMsg(`Ukuran file maksimal 7MB. File Anda: ${(file.size / (1024*1024)).toFixed(2)}MB`);
      return;
    }

    try {
      const base64 = await fileToBase64(file);
      const previewUrl = URL.createObjectURL(file);
      const mimeType = file.type;

      if (type === 'sketch') {
        setSketchImage({ base64, previewUrl, mimeType });
      } else {
        setStyleRefImage({ base64, previewUrl, mimeType });
      }
    } catch (err) {
      console.error("Upload Error:", err);
      setAppErrorMsg("Gagal memproses file gambar.");
    }
  };

  const handleRandom = () => {
    setFormData(prev => ({
      ...prev,
      tipe: DB_TIPE[Math.floor(Math.random() * DB_TIPE.length)],
      gaya: DB_GAYA[Math.floor(Math.random() * DB_GAYA.length)],
      material: DB_MATERIAL[Math.floor(Math.random() * DB_MATERIAL.length)],
      suasana: DB_SUASANA[Math.floor(Math.random() * DB_SUASANA.length)],
      view: DB_VIEW[Math.floor(Math.random() * DB_VIEW.length)],
      skenario: DB_SKENARIO[Math.floor(Math.random() * DB_SKENARIO.length)],
      engine: DB_ENGINE[Math.floor(Math.random() * DB_ENGINE.length)],
    }));
  };

  // --- LOGIC: HIERARCHICAL PROMPT ENGINEER ---
  const constructPrompt = () => {
    const { tipe, gaya, material, suasana, view, rasio, presentasi, skenario, engine, detail, lockSketch } = formData;
    const styleDescription = DB_PRESENTASI[presentasi];
    
    // 1. Deteksi Interior vs Eksterior
    const isInterior = view.includes("[INT]");
    const archTypeContext = isInterior ? "interior architectural space" : "exterior volumetric structure";
    
    // 2. Terapkan PBR Mapping
    const pbrMaterialDesc = enhanceWithPBR(material);

    let core = `Generate a high-end architectural visualization of a ${tipe}. Focus on the ${archTypeContext}. Design style: ${gaya}. `;
    
    if (sketchImage) {
      core += `Follow the structural outlines and geometry provided in the SKETCH IMAGE strictly. `;
      if (lockSketch) core += `CRITICAL CONSTRAINT: Maintain the exact spatial arrangement, scale, and silhouette from the input sketch. `;
    }

    core += `Presentation Style: ${styleDescription}. `;
    core += `Perspective & Lens: ${view}. ${isInterior ? "Use wide angle 24mm lens to capture the breadth of the space. " : "Use 35mm-50mm lens to prevent geometric distortion. "}`;
    core += `Physically Based Materials (PBR): ${pbrMaterialDesc}. `;
    core += `Lighting/Atmosphere: ${suasana}. `;
    core += `Cinematic Storytelling/Environment: ${skenario}. `;
    
    if (detail) core += `Additional details: ${detail}. `;
    core += `Quality: 4k resolution, hyper-realistic textures, cinematic global illumination, ${engine} engine aesthetic. --no unrealistic scale, warped geometry, chromatic aberration, text`;

    return core;
  };

  const handleGeneratePrompt = () => {
    setIsGenerating(true);
    setAppErrorMsg(null);
    // Simulasi delay singkat agar UI terasa memproses
    setTimeout(() => {
      setGeneratedPrompt(constructPrompt());
      setIsGenerating(false);
    }, 400);
  };

  // --- LOGIC: SECURE BFF IMAGE RENDER ---
  const handleRenderImage = async () => {
    if (!generatedPrompt) return;
    setIsRendering(true);
    setRenderImage(null);
    setAppErrorMsg(null);

    // Klien tidak menyimpan API Key. Menembak endpoint BFF produksi.
    const bffImageEndpoint = "/api/render/image"; 

    const payload = {
      prompt: generatedPrompt,
      aspectRatio: DB_RASIO[formData.rasio],
      useSearchGrounding: useGrounding, // Flag untuk Gemini 3.1
      sketch: sketchImage ? { mimeType: sketchImage.mimeType, data: sketchImage.base64 } : null,
      style: styleRefImage ? { mimeType: styleRefImage.mimeType, data: styleRefImage.base64 } : null
    };

    try {
      const response = await fetch(bffImageEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || `BFF menolak permintaan (Status ${response.status})`);
      }

      const result = await response.json();
      
      // Ekspektasi BFF merespons dengan Base64 gambar
      if (result.imageBase64) {
        setRenderImage(`data:image/jpeg;base64,${result.imageBase64}`);
      } else {
        throw new Error("BFF berhasil merespons, tetapi gagal memberikan format base64 gambar.");
      }
    } catch (err) {
      console.error("Image Render Error:", err);
      setAppErrorMsg(err.message);
    } finally {
      setIsRendering(false);
    }
  };

  // --- LOGIC: IMAGE TO VIDEO (I2V) TRIGGER ---
  const handleTriggerVideo = async () => {
    if (!renderImage) return;
    setIsVideoGenerating(true);
    setAppErrorMsg(null);

    const bffVideoStartEndpoint = "/api/video/start";

    const payload = {
        baseImage: renderImage, 
        motionPrompt: motionPrompt,
        duration: "standard" // Parameter tambahan untuk API Kling/Runway
    };

    try {
        const response = await fetch(bffVideoStartEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || `BFF Gagal memulai tugas video (Status ${response.status})`);
        }

        const result = await response.json();
        
        if (result.jobId) {
            // Memulai proses polling ke BFF menggunakan custom hook
            startPolling(result.jobId);
        } else {
            throw new Error("BFF tidak mengembalikan Job ID yang valid.");
        }
    } catch (err) {
        console.error("Video Trigger Error:", err);
        setAppErrorMsg(err.message);
        setIsVideoGenerating(false);
    }
  };

  // Manajemen Status Peringatan Hook Video
  useEffect(() => {
    if (isVideoReady || videoError) {
        setIsVideoGenerating(false);
        if (videoError) setAppErrorMsg(videoError);
    }
  }, [isVideoReady, videoError]);

  // ==========================================
  // 5. JSX RENDER
  // ==========================================
  return (
    <div className="min-h-screen bg-[#fcfcfd] text-[#1a1c1e] font-sans pb-28">
      {/* --- NAVBAR --- */}
      <header className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-50 px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="bg-[#4338ca] p-2.5 rounded-2xl text-white">
            <Home size={22} />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tighter">Smart Arch Studio <span className="text-[#4338ca]">v2.1 (Enterprise)</span></h1>
            <p className="text-[9px] text-[#64748b] font-bold uppercase tracking-widest">Secure Generative BIM Visualizer</p>
          </div>
        </div>
        <button 
          onClick={handleRandom}
          className="flex items-center gap-2 px-4 py-2 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#475569] rounded-xl transition-all text-[11px] font-bold"
        >
          <RefreshCw size={14} /> Acak Parameter
        </button>
      </header>

      <main className="max-w-7xl mx-auto mt-8 px-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* --- KIRI: PANEL INPUT --- */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* MULTIMODAL UPLOAD AREA */}
          <section className="bg-white p-6 rounded-[2rem] border border-[#e2e8f0] shadow-sm">
             <div className="flex justify-between items-center mb-5">
               <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#94a3b8] flex items-center gap-2">
                 <Upload size={14} /> Source Immersives (Max 7MB)
               </h2>
               <div className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded text-[9px] font-bold">MULTIMODAL ON</div>
             </div>
             
             <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
               {/* Sketch Upload */}
               <div className="space-y-3">
                 <div className="flex justify-between items-center">
                   <label className="text-[11px] font-bold text-[#475569]">Sketsa Dasar (Blueprint)</label>
                   {sketchImage && (
                     <button 
                      onClick={() => setFormData({...formData, lockSketch: !formData.lockSketch})}
                      className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[9px] font-bold transition-all ${formData.lockSketch ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-400'}`}
                     >
                       {formData.lockSketch ? <Lock size={10} /> : <Unlock size={10} />}
                       {formData.lockSketch ? 'LOCKED' : 'UNLOCKED'}
                     </button>
                   )}
                 </div>
                 <div 
                    onClick={() => fileInputSketch.current.click()}
                    className={`relative aspect-video rounded-2xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center overflow-hidden ${sketchImage ? 'border-indigo-500 bg-indigo-50' : 'border-[#e2e8f0] hover:border-indigo-300 bg-[#f8fafc]'}`}
                 >
                   {sketchImage ? (
                     <>
                       <img src={sketchImage.previewUrl} className="w-full h-full object-cover" alt="Sketch" />
                       <button 
                        onClick={(e) => { e.stopPropagation(); setSketchImage(null); }}
                        className="absolute top-2 right-2 bg-white/90 p-1.5 rounded-full text-red-500 shadow-md"
                       ><X size={14}/></button>
                     </>
                   ) : (
                     <div className="text-center p-4">
                       <PenTool size={20} className="mx-auto mb-2 text-[#cbd5e1]" />
                       <p className="text-[10px] font-bold text-[#94a3b8] uppercase">Upload Sketsa</p>
                     </div>
                   )}
                 </div>
                 <input type="file" ref={fileInputSketch} hidden onChange={(e) => handleFileUpload(e, 'sketch')} accept="image/*" />
               </div>

               {/* Style Ref Upload */}
               <div className="space-y-3">
                 <label className="text-[11px] font-bold text-[#475569]">Referensi Mood & Warna</label>
                 <div 
                    onClick={() => fileInputStyle.current.click()}
                    className={`relative aspect-video rounded-2xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center overflow-hidden ${styleRefImage ? 'border-amber-500 bg-amber-50' : 'border-[#e2e8f0] hover:border-amber-300 bg-[#f8fafc]'}`}
                 >
                   {styleRefImage ? (
                     <>
                       <img src={styleRefImage.previewUrl} className="w-full h-full object-cover" alt="Style" />
                       <button 
                        onClick={(e) => { e.stopPropagation(); setStyleRefImage(null); }}
                        className="absolute top-2 right-2 bg-white/90 p-1.5 rounded-full text-red-500 shadow-md"
                       ><X size={14}/></button>
                     </>
                   ) : (
                     <div className="text-center p-4">
                       <Palette size={20} className="mx-auto mb-2 text-[#cbd5e1]" />
                       <p className="text-[10px] font-bold text-[#94a3b8] uppercase">Upload Referensi</p>
                     </div>
                   )}
                 </div>
                 <input type="file" ref={fileInputStyle} hidden onChange={(e) => handleFileUpload(e, 'style')} accept="image/*" />
               </div>
             </div>
          </section>

          {/* PROJECT DEFINITION (PARAMS) */}
          <section className="bg-white p-7 rounded-[2rem] border border-[#e2e8f0] shadow-sm space-y-6">
            <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#94a3b8] flex items-center gap-2">
              <Settings size={14} /> Project Definition
            </h2>
            
            {/* Baris 1: Tipe & Material */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Kategori Bangunan</label>
                <select 
                  className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                  value={formData.tipe}
                  onChange={(e) => setFormData({...formData, tipe: e.target.value})}
                >
                  {DB_TIPE.map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Material Utama (PBR)</label>
                <select 
                  className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                  value={formData.material}
                  onChange={(e) => setFormData({...formData, material: e.target.value})}
                >
                  {DB_MATERIAL.map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
            </div>

            {/* Baris 2: View & Suasana */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Kamera & Perspektif</label>
                    <select 
                    className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                    value={formData.view}
                    onChange={(e) => setFormData({...formData, view: e.target.value})}
                    >
                    {DB_VIEW.map(t => <option key={t}>{t}</option>)}
                    </select>
                </div>
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Pencahayaan / Waktu</label>
                    <select 
                    className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                    value={formData.suasana}
                    onChange={(e) => setFormData({...formData, suasana: e.target.value})}
                    >
                    {DB_SUASANA.map(t => <option key={t}>{t}</option>)}
                    </select>
                </div>
            </div>

            {/* Baris 3: Presentasi & Rasio */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Gaya Render</label>
                <select 
                  className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                  value={formData.presentasi}
                  onChange={(e) => setFormData({...formData, presentasi: e.target.value})}
                >
                  {Object.keys(DB_PRESENTASI).map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">Rasio Gambar</label>
                <select 
                  className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold text-[#1e293b]"
                  value={formData.rasio}
                  onChange={(e) => setFormData({...formData, rasio: e.target.value})}
                >
                  {Object.keys(DB_RASIO).map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
            </div>

            {/* Baris 4: Konfigurasi Lanjutan (Video & Grounding) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-5 border-t border-[#f1f5f9]">
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">
                    Gemini Search Grounding
                    </label>
                    <div className="flex items-center gap-3 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 h-[46px]">
                    <input 
                        type="checkbox" 
                        checked={useGrounding}
                        onChange={(e) => setUseGrounding(e.target.checked)}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                    />
                    <span className="text-[11px] font-bold text-[#475569]">
                        Gunakan data web live untuk akurasi konteks
                    </span>
                    </div>
                </div>

                <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-[#64748b] uppercase tracking-tight ml-1">
                    Motion Prompt (Animasi Video)
                    </label>
                    <input 
                    type="text"
                    className="w-full h-[46px] bg-[#f8fafc] border border-[#e2e8f0] rounded-xl px-3 outline-none focus:ring-2 focus:ring-purple-500 text-sm font-semibold text-[#1e293b]"
                    value={motionPrompt}
                    onChange={(e) => setMotionPrompt(e.target.value)}
                    placeholder="Contoh: Slow cinematic drone fly-through..."
                    />
                </div>
            </div>
          </section>

          <button 
            onClick={handleGeneratePrompt}
            disabled={isGenerating}
            className="w-full bg-[#4338ca] hover:bg-[#3730a3] text-white font-black py-5 rounded-[2rem] shadow-xl shadow-indigo-100 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
          >
            {isGenerating ? <RefreshCw className="animate-spin" /> : <Sparkles size={18} />}
            SUSUN PROMPT NEURAL
          </button>
        </div>

        {/* --- KANAN: PANEL OUTPUT & RENDER --- */}
        <div className="lg:col-span-5 space-y-6">
          
          <div className="bg-[#0f172a] rounded-[2.5rem] p-8 text-white shadow-2xl relative overflow-hidden flex flex-col min-h-[650px] border border-slate-800">
            <div className="absolute top-0 right-0 p-10 opacity-5 pointer-events-none">
              <Cpu size={120} />
            </div>

            <div className="flex justify-between items-center mb-6 z-10">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${appErrorMsg ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'}`}></div>
                <span className="text-[9px] font-black uppercase tracking-widest text-[#94a3b8]">BFF Proxy Active</span>
              </div>
              <div className="flex bg-[#1e293b] p-1 rounded-xl">
                 <button 
                  onClick={() => setTargetAi('Gemini 3.1 Flash Image')}
                  className={`px-3 py-1 text-[9px] font-black rounded-lg transition-all ${targetAi.includes('Gemini') ? 'bg-indigo-600 text-white' : 'text-[#64748b]'}`}
                 >GEMINI 3.1</button>
              </div>
            </div>

            {/* Kotak Review Prompt */}
            <div className="bg-[#1e293b]/50 border border-slate-700 p-4 rounded-2xl mb-6 flex-grow-0 z-10">
              <h3 className="text-[10px] text-[#94a3b8] font-bold uppercase mb-2">PBR Neural Prompt:</h3>
              <p className="text-xs text-[#cbd5e1] font-mono leading-relaxed break-words min-h-[80px]">
                {generatedPrompt || "Tekan tombol di sebelah kiri untuk menyusun prompt hierarkis..."}
              </p>
            </div>

            {/* Manajemen Error Universal */}
            {appErrorMsg && (
                <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-xl text-red-400 text-[11px] font-bold mb-4 z-10 flex items-start gap-2">
                    <AlertCircle size={16} className="shrink-0" />
                    <p className="leading-snug">{appErrorMsg}</p>
                </div>
            )}

            {/* Display Area (Gambar / Video / Loading Status) */}
            <div className="flex-1 w-full bg-[#1e293b] rounded-2xl border border-slate-700 mb-6 flex items-center justify-center overflow-hidden z-10 relative">
                {videoUrl ? (
                    <video src={videoUrl} controls autoPlay loop className="w-full h-full object-cover" />
                ) : renderImage ? (
                    <img src={renderImage} alt="Rendered Architecture" className="w-full h-full object-cover" />
                ) : (
                    <div className="text-center p-6 flex flex-col items-center">
                        {isVideoGenerating ? (
                            <>
                                <RefreshCw size={28} className="text-purple-400 animate-spin mb-3" />
                                <p className="text-xs font-bold text-purple-300 tracking-wide uppercase">{pollingStatus}</p>
                            </>
                        ) : isRendering ? (
                            <>
                                <RefreshCw size={28} className="text-emerald-400 animate-spin mb-3" />
                                <p className="text-xs font-bold text-emerald-300 tracking-wide uppercase">Merender Gambar (BFF)...</p>
                            </>
                        ) : (
                            <>
                                <ImageIcon size={32} className="text-slate-600 mb-3" />
                                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Viewport Standby</p>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Render Actions */}
            <div className="flex gap-3 z-10 mt-auto">
              <button 
                onClick={handleRenderImage}
                disabled={!generatedPrompt || isRendering || isVideoGenerating}
                className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-black py-4 rounded-2xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRendering ? <RefreshCw size={16} className="animate-spin" /> : <ImageIcon size={16} />}
                <span className="text-[11px]">{isRendering ? "MEMPROSES..." : "RENDER IMAGE (BFF)"}</span>
              </button>

              <button 
                onClick={handleTriggerVideo}
                disabled={!renderImage || isVideoGenerating || isRendering}
                className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black py-4 rounded-2xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isVideoGenerating ? <RefreshCw size={16} className="animate-spin" /> : <Video size={16} />}
                <span className="text-[11px]">{isVideoGenerating ? "POLLING..." : "GENERATE VIDEO"}</span>
              </button>
            </div>
            
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
