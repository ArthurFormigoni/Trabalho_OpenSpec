export type Post = { id: number; size_x: number; size_y: number; filesize_bytes: number; image_url: string; likes_count: number; comments_count: number; revision: number };
export type Counts = { image_id: number; likes_count: number; comments_count: number; revision: number };
export function applyCounts(posts: Post[], state: Counts): Post[] {
  return posts.map(post => post.id === state.image_id && state.revision >= post.revision ? { ...post, likes_count: state.likes_count, comments_count: state.comments_count, revision: state.revision } : post);
}
export function mergeSnapshot(current: Post[], incoming: Post[]): Post[] {
  return incoming.map(post => {
    const existing = current.find(item => item.id === post.id && item.image_url === post.image_url);
    return existing && existing.revision > post.revision ? existing : post;
  });
}
export function socketUrl(api: string, origin: string): string {
  const url = new URL(`${api}/ws`, origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}
