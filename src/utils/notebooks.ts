import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { SITE } from '../consts';

// Notebookurile laboratoarelor stau în public/, în repozitoriul site-ului. Colab și GitHub le citesc de pe ramura
// `main`, așa că un notebook nou se deschide abia după ce ajunge pe GitHub. Căile sunt relative la public/.

/** Oprește build-ul dacă notebookul nu există în public/. */
export const verificaNotebook = (notebook: string): void => {
  if (!existsSync(join(process.cwd(), 'public', notebook))) {
    throw new Error(`Notebookul ${notebook} nu există în public/.`);
  }
};

export const colabUrl = (notebook: string): string =>
  `${SITE.repo.replace('https://github.com/', 'https://colab.research.google.com/github/')}/blob/main/public/${notebook}`;

export const githubUrl = (notebook: string): string => `${SITE.repo}/blob/main/public/${notebook}`;

/** Notebookul unui laborator: public/laboratoare/<laborator>/<laborator>.ipynb (unul pentru tot laboratorul). */
export const notebookLaborator = (laborator: string): string => `laboratoare/${laborator}/${laborator}.ipynb`;
