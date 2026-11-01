// Episoadele seriei video (colecția „videouri”, src/content.config.ts) și ce se calculează din ele: ordinea, adresele
// de pe YouTube, durata și momentele de timp scrise pentru cititor.

import { type CollectionEntry, getCollection } from 'astro:content';
import { existsSync } from 'node:fs';
import { pluralize } from './format';

export type Video = CollectionEntry<'videouri'>;

/** Toate episoadele, în ordinea numerelor (cele fără număr, la sfârșit, după data publicării). */
export async function videouri(): Promise<Video[]> {
  const toate = await getCollection('videouri');
  return toate.sort(
    (a, b) =>
      (a.data.number ?? Number.POSITIVE_INFINITY) - (b.data.number ?? Number.POSITIVE_INFINITY) ||
      a.data.youtube.published.localeCompare(b.data.youtube.published),
  );
}

/** Un episod după id (numele fișierului fără .json); oprește build-ul dacă nu există. */
export async function video(id: string): Promise<Video> {
  const gasit = (await getCollection('videouri')).find((v) => v.id === id);
  if (!gasit) throw new Error(`Videoul „${id}” nu există în src/content/videouri/.`);
  return gasit;
}

export const paginaVideo = (v: Video) => `/videouri/${v.id}/`;

export const eticheta = (v: Video) => (v.data.number ? `Episodul ${v.data.number}` : 'Video');

/** Pe YouTube, de la momentul t, dacă e dat. */
export const youtubeUrl = (v: Video, t?: number) =>
  `https://www.youtube.com/watch?v=${v.data.youtube.id}${t ? `&t=${Math.floor(t)}s` : ''}`;

/** Playerul încorporat, de pe youtube-nocookie.com, pornit la momentul t. */
export const embedUrl = (v: Video, t = 0) => {
  const q = new URLSearchParams({ autoplay: '1', rel: '0', enablejsapi: '1', hl: 'ro', cc_lang_pref: 'ro' });
  if (t >= 1) q.set('start', String(Math.floor(t)));
  return `https://www.youtube-nocookie.com/embed/${v.data.youtube.id}?${q}`;
};

/** Miniatura episodului, servită de pe domeniul site-ului (public/videouri/), sau nimic dacă lipsește. */
export function miniatura(v: Video, marime: 'mare' | 'mica' = 'mare'): string | undefined {
  const fisier = `videouri/${v.id}${marime === 'mica' ? '-mica' : ''}.jpg`;
  return existsSync(`public/${fisier}`) ? `/${fisier}` : undefined;
}

/** Un moment din video, ca pe YouTube: 4:05, 1:02:07. */
export function ceas(t: number): string {
  const s = Math.floor(t);
  const [h, m, sec] = [Math.floor(s / 3600), Math.floor((s % 3600) / 60), s % 60];
  const doua = (n: number) => String(n).padStart(2, '0');
  return h ? `${h}:${doua(m)}:${doua(sec)}` : `${m}:${doua(sec)}`;
}

/** Durata, în cuvinte: 42 de minute, 1 oră și 5 minute. */
export function durata(t: number): string {
  const minute = Math.max(1, Math.round(t / 60));
  const [h, m] = [Math.floor(minute / 60), minute % 60];
  if (!h) return pluralize(m, 'minut', 'minute');
  const ore = pluralize(h, 'oră', 'ore');
  return m ? `${ore} și ${pluralize(m, 'minut', 'minute')}` : ore;
}

/** Data publicării: 31 octombrie 2026. */
export const dataPublicarii = (v: Video) =>
  new Intl.DateTimeFormat('ro-RO', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(
    new Date(v.data.youtube.published),
  );

/** Capitolul în care cade momentul t (indicele lui), sau -1 dacă videoul nu are capitole. */
export const capitolLa = (v: Video, t: number) => v.data.chapters.findLastIndex((c) => c.t <= t);

/** Paginile documentației care includ videoul cu <Video id="…" />. */
export async function paginiCuVideo(id: string) {
  const docs = await getCollection('docs');
  const cauta = new RegExp(`<Video\\b[^>]*\\bid=["'{\`]+${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'}\`]`);
  return docs
    .filter((d) => cauta.test(d.body ?? ''))
    .map((d) => ({ href: d.id === 'index' ? '/' : `/${d.id}/`, titlu: d.data.title }))
    .sort((a, b) => a.titlu.localeCompare(b.titlu, 'ro'));
}
