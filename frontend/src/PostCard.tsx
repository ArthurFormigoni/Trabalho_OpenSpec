import { useCallback, useEffect, useRef, useState } from "react";
import { Heart, MessageCircle, Trash2 } from "lucide-react";
import type { Counts, Post } from "./posts";

type Comment = { id: number; body: string; created_at: string };
type Props = { post: Post; api: string; busy: boolean; sync: number; onDelete: (id: number) => void; onCounts: (state: Counts) => void; onError: (message: string) => void };

export default function PostCard({ post, api, busy, sync, onDelete, onCounts, onError }: Props) {
  const [open, setOpen] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [cursor, setCursor] = useState<number | null>(null);
  const [draft, setDraft] = useState("");
  const [liking, setLiking] = useState(false), [sending, setSending] = useState(false), [loading, setLoading] = useState(false);
  const likeLock = useRef(false), commentLock = useRef(false), request = useRef(0), paged = useRef(false);
  const load = useCallback(async (before?: number) => {
    const ticket = ++request.current;
    setLoading(true);
    try {
      const response = await fetch(`${api}/images/${post.id}/comments${before ? `?before_id=${before}` : ""}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Não foi possível carregar os comentários.");
      const page = await response.json() as { items: Comment[]; next_cursor: number | null };
      if (ticket !== request.current) return;
      setComments(current => [...new Map([...current, ...page.items].map(comment => [comment.id, comment])).values()].sort((a, b) => b.id - a.id));
      if (before || !paged.current) setCursor(page.next_cursor);
      if (before) paged.current = true;
    } catch (error) { if (ticket === request.current) onError((error as Error).message); }
    finally { if (ticket === request.current) setLoading(false); }
  }, [api, post.id, onError]);
  useEffect(() => { if (open) void load(); }, [open, post.comments_count, sync, load]);
  useEffect(() => () => { request.current++; }, []);
  async function like() {
    if (likeLock.current) return;
    likeLock.current = true; setLiking(true);
    try {
      const response = await fetch(`${api}/images/${post.id}/likes`, { method: "POST" });
      if (!response.ok) throw new Error("Não foi possível curtir. Tente novamente.");
      onCounts(await response.json() as Counts);
    } catch (error) { onError((error as Error).message); }
    finally { likeLock.current = false; setLiking(false); }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (commentLock.current || !draft.trim()) return;
    commentLock.current = true; setSending(true);
    try {
      const response = await fetch(`${api}/images/${post.id}/comments`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ body: draft.trim() }) });
      if (!response.ok) throw new Error("Não foi possível enviar o comentário.");
      const result = await response.json() as Counts & { comment: Comment };
      onCounts(result); setDraft("");
      setComments(current => [...new Map([result.comment, ...current].map(comment => [comment.id, comment])).values()].sort((a, b) => b.id - a.id));
      void load();
    } catch (error) { onError((error as Error).message); }
    finally { commentLock.current = false; setSending(false); }
  }
  return <article className="post-card">
    <div className="image-card"><img src={`${api}${post.image_url}`} alt="Imagem da galeria" /><button className="delete-button" aria-label={`Apagar imagem ${post.id}`} title="Apagar imagem" onClick={() => onDelete(post.id)} disabled={busy}><Trash2 size={17} /></button></div>
    <div className="post-actions"><button className="button secondary" onClick={() => void like()} disabled={liking} aria-label={`Curtir post ${post.id}`}><Heart size={18} /> {post.likes_count}</button><button className="button secondary" aria-expanded={open} aria-controls={`comments-${post.id}`} onClick={() => setOpen(value => !value)}><MessageCircle size={18} /> {post.comments_count}</button></div>
    {open && <section className="comments" id={`comments-${post.id}`} aria-label="Comentários">
      <form onSubmit={event => void submit(event)}><label htmlFor={`draft-${post.id}`}>Deixe um comentário</label><textarea id={`draft-${post.id}`} value={draft} onChange={event => setDraft(event.target.value)} maxLength={1000} disabled={sending} placeholder="Escreva aqui…" /><div className="comment-footer"><small>{draft.length}/1000 · Anônimo</small><button className="button primary" disabled={sending || !draft.trim()}>{sending ? "Enviando…" : "Enviar"}</button></div></form>
      {loading && <p role="status">Carregando comentários…</p>}
      {!comments.length && !loading && <p>Seja o primeiro a comentar.</p>}
      <ul>{comments.map(comment => <li key={comment.id}><strong>Anônimo</strong><time dateTime={comment.created_at}>{new Date(comment.created_at).toLocaleString()}</time><p>{comment.body}</p></li>)}</ul>
      {cursor !== null && <button className="button secondary" disabled={loading} onClick={() => void load(cursor)}>Comentários anteriores</button>}
    </section>}
  </article>;
}
