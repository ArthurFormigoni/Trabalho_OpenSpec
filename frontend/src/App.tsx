import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Camera, ImagePlus, LoaderCircle, Trash2, Upload } from "lucide-react";

type GalleryImage = { id: number; size_x: number; size_y: number; filesize_bytes: number; image_url: string };
const API_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

function App() {
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const showToast = useCallback((message: string) => { setToast(message); window.setTimeout(() => setToast(null), 4500); }, []);
  const loadImages = useCallback(async () => {
    setLoading(true);
    try { const response = await fetch(`${API_URL}/images`); if (!response.ok) throw new Error("Não foi possível carregar a galeria."); setImages(await response.json() as GalleryImage[]); }
    catch (error) { showToast(error instanceof Error ? error.message : "Não foi possível carregar a galeria."); }
    finally { setLoading(false); }
  }, [showToast]);
  useEffect(() => { void loadImages(); }, [loadImages]);
  async function uploadImage(file: File) {
    setBusy(true); const form = new FormData(); form.append("file", file);
    try { const response = await fetch(`${API_URL}/images`, { method: "POST", body: form }); if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail ?? "Não foi possível adicionar a imagem."); } await loadImages(); }
    catch (error) { showToast(error instanceof Error ? error.message : "Não foi possível adicionar a imagem."); }
    finally { setBusy(false); if (inputRef.current) inputRef.current.value = ""; }
  }
  async function deleteImage(id: number) {
    if (!window.confirm("Apagar esta imagem?")) return;
    setBusy(true);
    try { const response = await fetch(`${API_URL}/images/${id}`, { method: "DELETE" }); if (!response.ok) throw new Error("Não foi possível apagar a imagem."); setImages((current) => current.filter((image) => image.id !== id)); }
    catch (error) { showToast(error instanceof Error ? error.message : "Não foi possível apagar a imagem."); }
    finally { setBusy(false); }
  }
  const countLabel = useMemo(() => `${images.length} ${images.length === 1 ? "imagem" : "imagens"}`, [images.length]);
  return <main className="page-shell">
    <header className="hero"><div className="brand-mark"><Camera size={24} /></div><div><p className="eyebrow">PHOTO GALLERY</p><h1>Suas memórias, em mosaico.</h1><p className="subtitle">Uma galeria leve para guardar os momentos que importam.</p></div><button className="button primary" onClick={() => inputRef.current?.click()} disabled={busy}><ImagePlus size={18} /> Adicionar Imagem</button><input ref={inputRef} className="visually-hidden" type="file" accept="image/*,.heic,.heif,.tif,.tiff" onChange={(event) => { const file = event.target.files?.[0]; if (file) void uploadImage(file); }} /></header>
    <section className="gallery-section" aria-live="polite"><div className="section-heading"><div><p className="eyebrow">GALERIA</p><h2>{countLabel}</h2></div>{busy && <LoaderCircle className="spinner" size={20} />}</div>{loading ? <div className="empty-state"><LoaderCircle className="spinner" size={28} /><p>Carregando suas imagens...</p></div> : images.length === 0 ? <div className="empty-state"><Upload size={32} /><h3>Sua galeria está vazia</h3><p>Adicione uma imagem para começar o seu mosaico.</p><button className="button secondary" onClick={() => inputRef.current?.click()}>Adicionar primeira imagem</button></div> : <div className="gallery-grid">{images.map((image) => <article className="image-card" key={image.id}><img src={`${API_URL}${image.image_url}`} alt="Imagem da galeria" /><button className="delete-button" aria-label={`Apagar imagem ${image.id}`} title="Apagar imagem" onClick={() => void deleteImage(image.id)} disabled={busy}><Trash2 size={17} /></button></article>)}</div>}</section>
    {toast && <div className="toast" role="alert">{toast}</div>}
  </main>;
}

export default App;
