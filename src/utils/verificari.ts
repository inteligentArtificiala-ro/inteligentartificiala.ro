import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

// Rezultatele rulării automate a notebookurilor laboratoarelor (.github/workflows/verificare-laboratoare.yml,
// scripts/verificare-laboratoare.py). Sunt păstrate pe ramura `verificari` a repozitoriului, iar deploy.yml le copiază
// în src/data/verificari.json înainte de build. Fără fișier (de obicei local), paginile apar fără rezultate. Local, se
// pot aduce cu:
//
//   git fetch origin verificari && mkdir -p src/data && git show FETCH_HEAD:verificari.json > src/data/verificari.json

export interface Rulare {
  stare: 'reusita' | 'esuata';
  /** Începutul rulării, ISO 8601. */
  data: string;
  /** Durata, în secunde. */
  durata: number;
  /** Rularea din GitHub Actions. */
  jurnal?: string | null;
  mediu: { placaGrafica?: string | null };
  /** Celula la care s-a oprit rularea: indicele, primul rând de cod și eroarea. */
  eroare?: { celula?: number | null; sursa?: string | null; mesaj: string };
}

export interface VerificareLaborator {
  ultimaRulare: Rulare;
  ultimaRulareReusita?: Rulare;
}

const fisier = join(process.cwd(), 'src', 'data', 'verificari.json');
const laboratoare: Record<string, VerificareLaborator> = existsSync(fisier)
  ? (JSON.parse(readFileSync(fisier, 'utf8')).laboratoare ?? {})
  : {};

/** Ultimele rulări ale notebookului unui laborator (numele folderului din public/laboratoare/), dacă există. */
export const verificareLaborator = (laborator: string): VerificareLaborator | undefined => laboratoare[laborator];

/** Laboratorul unui notebook: laboratoare/<laborator>/<laborator>.ipynb. */
export const laboratorulNotebookului = (notebook: string): string => notebook.split('/')[1];
