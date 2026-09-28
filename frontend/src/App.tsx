import { useCallback, useEffect, useRef, useState } from "react";
import { Camera, ImagePlus, LoaderCircle, Upload } from "lucide-react";
import PostCard from "./PostCard";
import { applyCounts, mergeSnapshot, socketUrl, type Post, type Counts } from "./posts";

const API_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

function App() {
  const [images, setImages] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false);
  const [live, setLive] = useState(false), [sync, setSync] = useState(0);
  const [toast, setToast] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const epoch = useRef(0), refreshing = useRef(false), again = useRef(false);
  const toastTimer = useRef<ReturnType<typeof setTimeout>>();
  const showToast = useCallback((message: string) => {
    setToast(message); clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 4500);
  }, []);
  const loadImages = useCallback(async () => {
    again.current = true;
    if (refreshing.current) return;
    refreshing.current = true;
    try {
      while (again.current) {
        again.current = false;
        const version = epoch.current;
        const response = await fetch(`${API_URL}/images`, { cache: "no-store" });
        if (!response.ok) throw new Error("Não foi possível carregar a galeria.");
        const data = await response.json() as Post[];
        if (version !== epoch.current) { again.current = true; continue; }
        setImages(current => mergeSnapshot(current, data));
        setSync(value => value + 1);
      }
    } catch (error) { showToast((error as Error).message); }
    finally { refreshing.current = false; setLoading(false); }
  }, [showToast]);
  const onCounts = useCallback((state: Counts) => {
    epoch.current++;
    setImages(current => applyCounts(current, state));
  }, []);
  useEffect(() => {
    let stopped = false, socket: WebSocket | undefined, timer: ReturnType<typeof setTimeout>, delay = 1000, lastMessage = Date.now();
    function connect() {
      if (stopped) return;
      socket = new WebSocket(socketUrl(API_URL, window.location.origin));
      socket.onopen = () => { delay = 1000; lastMessage = Date.now(); void loadImages(); };
      socket.onmessage = event => {
        lastMessage = Date.now();
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "status" || payload.type === "heartbeat") {
            setLive(Boolean(payload.live));
            if (payload.type === "status") void loadImages();
          } else if (payload.type === "post.updated") {
            onCounts(payload.data);
          } else if (payload.type === "image.deleted") {
            epoch.current++; setImages(current => current.filter(post => post.id !== payload.image_id));
            void loadImages();
          } else if (payload.type === "image.created") {
            epoch.current++; void loadImages();
          }
        } catch { /* Periodic synchronization recovers malformed or missed events. */ }
      };
      socket.onerror = () => socket?.close();
      socket.onclose = () => {
        setLive(false);
        if (!stopped) { timer = setTimeout(connect, delay + Math.random() * 500); delay = Math.min(delay * 2, 30000); }
      };
    }
    void loadImages(); connect();
    const poll = setInterval(() => { if (!document.hidden) void loadImages(); if (Date.now() - lastMessage > 45000) socket?.close(); }, 30000);
    const foreground = () => { if (!document.hidden) void loadImages(); };
    document.addEventListener("visibilitychange", foreground);
    return () => { stopped = true; clearTimeout(timer); clearInterval(poll); clearTimeout(toastTimer.current); socket?.close(); document.removeEventListener("visibilitychange", foreground); };
  }, [loadImages, onCounts]);
  async function uploadImage(file: File) {
    setBusy(true); const form = new FormData(); form.append("file", file);
    try {
      const response = await fetch(`${API_URL}/images`, { method: "POST", body: form });
      if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail ?? "Não foi possível adicionar a imagem."); }
      epoch.current++; await loadImages();
    } catch (error) { showToast((error as Error).message); }
    finally { setBusy(false); if (inputRef.current) inputRef.current.value = ""; }
  }
  async function deleteImage(id: number) {
    if (!window.confirm("Apagar esta imagem e seus comentários?")) return;
    setBusy(true);
    try {
      const response = await fetch(`${API_URL}/images/${id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Não foi possível apagar a imagem.");
      epoch.current++; setImages(current => current.filter(post => post.id !== id));
    } catch (error) { showToast((error as Error).message); }
    finally { setBusy(false); }
  }
  return <main className="page-shell">
    <header className="hero"><div className="brand-mark"><Camera size={24} /></div><div><p className="eyebrow">PHOTO GALLERY</p><h1>Suas memórias, em mosaico.</h1><p className="subtitle">Compartilhe momentos, curta e converse.</p></div><button className="button primary" onClick={() => inputRef.current?.click()} disabled={busy}><ImagePlus size={18} /> Adicionar Imagem</button><input ref={inputRef} className="visually-hidden" type="file" accept="image/*,.heic,.heif,.tif,.tiff" onChange={event => { const file = event.target.files?.[0]; if (file) void uploadImage(file); }} /></header>
    <section className="gallery-section"><div className="section-heading"><div><p className="eyebrow">GALERIA</p><h2>{images.length} {images.length === 1 ? "post" : "posts"}</h2><small className="live-status" role="status">{live ? "Atualizações ao vivo" : "Ao vivo indisponível · atualização periódica ativa"}</small></div>{busy && <LoaderCircle className="spinner" size={20} />}</div>
      {loading ? <div className="empty-state"><LoaderCircle className="spinner" size={28} /><p>Carregando suas imagens...</p></div> : !images.length ? <div className="empty-state"><Upload size={32} /><h3>Sua galeria está vazia</h3><p>Adicione uma imagem para começar.</p><button className="button secondary" onClick={() => inputRef.current?.click()}>Adicionar primeira imagem</button></div> : <div className="gallery-grid">{images.map(post => <PostCard key={post.id} post={post} api={API_URL} busy={busy} sync={sync} onDelete={id => void deleteImage(id)} onCounts={onCounts} onError={showToast} />)}</div>}
    </section>{toast && <div className="toast" role="alert">{toast}</div>}
  </main>;
}
export default App;
