// @ts-check

import { unified } from '@astrojs/markdown-remark';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import starlightThemeExquisitus from 'starlight-theme-exquisitus';
import vendor from './src/integrations/vendor.mjs';
import rehypeBibliography from './src/plugins/rehype-bibliography.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://inteligentartificiala.ro',
  trailingSlash: 'ignore',
  redirects: {
    '/concepte-de-baza/comportament-agentic': '/comportament-agentic/ce-este-comportamentul-agentic/',
  },
  integrations: [
    starlight({
      title: 'Inteligență Artificială',
      description:
        'Documentație în limba română despre inteligența artificială, de la conceptele de bază până la implementarea modelelor de limbaj mari (LLM).',
      favicon: '/favicon.png',
      defaultLocale: 'root',
      locales: {
        root: { label: 'Română', lang: 'ro' },
      },
      credits: false,
      // Data ultimei modificări vine din istoricul git (în CI, checkout-ul trebuie să aducă tot istoricul).
      lastUpdated: true,
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/inteligentArtificiala-ro',
        },
        {
          icon: 'youtube',
          label: 'YouTube',
          href: 'https://www.youtube.com/@inteligentArtificiala',
        },
      ],
      plugins: [starlightThemeExquisitus()],
      customCss: [
        '@fontsource-variable/source-sans-3/wght.css',
        '@fontsource-variable/source-sans-3/wght-italic.css',
        '@fontsource-variable/source-serif-4/opsz.css',
        '@fontsource-variable/source-serif-4/opsz-italic.css',
        'katex/dist/katex.min.css',
        './src/styles/custom.css',
      ],
      // O singură temă de culori: blocurile de cod rămân întunecate și în modul luminos (fundalul, în custom.css).
      expressiveCode: { themes: ['vitesse-dark'], styleOverrides: { borderRadius: '4px' } },
      components: {
        Head: './src/components/starlight/Head.astro',
        Header: './src/components/starlight/Header.astro',
        SiteTitle: './src/components/starlight/SiteTitle.astro',
        Footer: './src/components/starlight/Footer.astro',
        Hero: './src/components/starlight/Hero.astro',
        PageTitle: './src/components/starlight/PageTitle.astro',
      },
      // Grupurile din bara laterală sunt strânse, în afară de cel al paginii curente, pe care Starlight îl deschide singur.
      sidebar: [
        {
          label: 'Concepte de bază',
          collapsed: true,
          items: [{ autogenerate: { directory: 'concepte-de-baza' } }],
        },
        {
          label: 'Rețele neuronale',
          collapsed: true,
          items: [{ autogenerate: { directory: 'retele-neuronale' } }],
        },
        {
          label: 'Rețele neuronale pe grafuri',
          collapsed: true,
          items: [{ autogenerate: { directory: 'retele-neuronale-pe-grafuri' } }],
        },
        {
          label: 'Învățare prin consolidare',
          collapsed: true,
          items: [{ autogenerate: { directory: 'invatare-prin-consolidare' } }],
        },
        {
          label: 'Modele de limbaj mari (LLM)',
          collapsed: true,
          items: [{ autogenerate: { directory: 'modele-lingvistice' } }],
        },
        {
          label: 'Comportament agentic',
          collapsed: true,
          items: [{ autogenerate: { directory: 'comportament-agentic' } }],
        },
        {
          label: 'Modele de difuzie',
          collapsed: true,
          items: [{ autogenerate: { directory: 'modele-de-difuzie' } }],
        },
        {
          label: 'Laboratoare',
          collapsed: true,
          items: [
            { label: 'Prezentare generală', slug: 'laboratoare' },
            {
              label: 'Rețele neuronale de la zero',
              collapsed: true,
              items: [{ autogenerate: { directory: 'laboratoare/retele-neuronale-de-la-zero' } }],
            },
            {
              label: 'Control continuu cu PPO în MuJoCo',
              collapsed: true,
              items: [{ autogenerate: { directory: 'laboratoare/control-continuu-ppo-halfcheetah' } }],
            },
            {
              label: 'Un model de limbaj de la zero',
              collapsed: true,
              items: [{ autogenerate: { directory: 'laboratoare/model-lingvistic-de-la-zero' } }],
            },
            {
              label: 'Un model de limbaj local cu Transformers',
              collapsed: true,
              items: [{ autogenerate: { directory: 'laboratoare/model-local-transformers' } }],
            },
            {
              label: 'Imagini și sunete cu modele de difuzie',
              collapsed: true,
              items: [{ autogenerate: { directory: 'laboratoare/difuzie-imagini-si-sunete' } }],
            },
          ],
        },
        // Seria video: lista episoadelor (src/pages/videouri/), câte o pagină pentru fiecare episod.
        { label: 'Videouri', link: '/videouri/' },
        {
          label: 'Proiect',
          collapsed: true,
          items: [
            { label: 'Despre proiect', slug: 'despre' },
            { label: 'Glosar de termeni', slug: 'glosar' },
            { label: 'Resurse utile', slug: 'resurse-utile' },
            { label: 'Contribuitori', slug: 'contribuitori' },
            { label: 'Cookie-uri', slug: 'cookie-uri' },
          ],
        },
      ],
    }),
    mdx(),
    sitemap(),
    // PyScript și ONNX Runtime, servite de pe domeniul site-ului (src/integrations/vendor.mjs).
    vendor(),
  ],
  markdown: {
    // Formulele ($...$ și $$...$$) sunt randate cu KaTeX la build, fără JavaScript în browser.
    processor: unified({
      remarkPlugins: [remarkMath],
      // Bibliografia de la sfârșitul paginilor: structură, id-uri și legături înapoi la citări (src/plugins/).
      rehypePlugins: [rehypeKatex, rehypeBibliography],
      // Ghilimelele drepte din proză devin ghilimele românești: „…” și «…».
      smartypants: {
        openingQuotes: { double: '„', single: '«' },
        closingQuotes: { double: '”', single: '»' },
      },
    }),
  },
});
