// Regula lui „de” (WRITING-STYLE-GUIDE.md §2): 1 pagină, 2 pagini, 19 pagini, 20 de pagini, 101 pagini, 120 de pagini.
export const pluralize = (n: number, singular: string, plural: string): string => {
  if (n === 1) return `1 ${singular}`;
  const de = n !== 0 && (n % 100 >= 20 || n % 100 === 0);
  return de ? `${n} de ${plural}` : `${n} ${plural}`;
};

/** Durata, în cuvinte: 42 de minute, 1 oră și 5 minute (t în secunde). */
export function durata(t: number): string {
  const minute = Math.max(1, Math.round(t / 60));
  const [h, m] = [Math.floor(minute / 60), minute % 60];
  if (!h) return pluralize(m, 'minut', 'minute');
  const ore = pluralize(h, 'oră', 'ore');
  return m ? `${ore} și ${pluralize(m, 'minut', 'minute')}` : ore;
}

/** Data, ca în WRITING-STYLE-GUIDE.md §8: 17 octombrie 2026 (ziua din România). */
export const formatDate = (data: string | Date): string =>
  new Intl.DateTimeFormat('ro-RO', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'Europe/Bucharest',
  }).format(new Date(data));
