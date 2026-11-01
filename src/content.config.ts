import { defineCollection } from 'astro:content';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { LEVELS, type Level } from './consts';

// Câmpuri suplimentare pentru paginile de documentație (opționale, ca paginile simple să nu aibă nevoie de ele).
const docFields = z.object({
  pubDate: z.coerce.date().optional(),
  authors: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  level: z.enum(Object.keys(LEVELS) as [Level, ...Level[]]).optional(),
});

const docs = defineCollection({
  loader: docsLoader(),
  schema: docsSchema({ extend: docFields }),
});

// Textele interfeței Starlight, ajustate după WRITING-STYLE-GUIDE.md.
const i18n = defineCollection({ loader: i18nLoader(), schema: i18nSchema() });

const contributori = defineCollection({
  loader: glob({ pattern: '*.{yaml,yml}', base: './src/content/contributori' }),
  schema: z.object({
    name: z.string(),
    url: z.url(),
    role: z.string().optional(),
    bio: z.string().optional(),
  }),
});

// Episoadele seriei video, câte un fișier pentru fiecare episod publicat pe YouTube: release.json-ul scris de
// aphrodite în studioul seriei (inteligentartificiala-series), copiat aici de scripts/site-sync.sh din studio,
// cu miniatura în public/videouri/. Momentele (t) sunt în secunde de la începutul videoului.
const moment = z.number().nonnegative();

const videouri = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/videouri' }),
  schema: z.object({
    number: z.number().int().optional(),
    title: z.string(),
    youtubeTitle: z.string(),
    headline: z.string().optional(),
    subtitle: z.string().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).default([]),
    duration: moment,
    youtube: z.object({ id: z.string(), published: z.iso.date() }),
    chapters: z.array(z.object({ t: moment, title: z.string() })).default([]),
    transcript: z.array(z.object({ t: moment, text: z.string() })).default([]),
    code: z
      .object({
        repo: z.url(),
        end: z.string(),
        steps: z.array(z.object({ t: moment, from: z.string().optional(), to: z.string() })),
      })
      .optional(),
  }),
});

export const collections = { docs, i18n, contributori, videouri };
