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
      },
      sidebar: [
        {
          label: 'Concepte de bază',
          items: [{ autogenerate: { directory: 'concepte-de-baza' } }],
        },
        {
          label: 'Rețele neuronale',
          items: [{ autogenerate: { directory: 'retele-neuronale' } }],
        },
        {
          label: 'Învățare prin consolidare',
          items: [{ autogenerate: { directory: 'invatare-prin-consolidare' } }],
        },
        {
          label: 'Modele de limbaj mari (LLM)',
          items: [{ autogenerate: { directory: 'modele-lingvistice' } }],
        },
        {
          label: 'Comportament agentic',
          items: [{ autogenerate: { directory: 'comportament-agentic' } }],
        },
        {
          label: 'Modele de difuzie',
          items: [{ autogenerate: { directory: 'modele-de-difuzie' } }],
        },
        {
          label: 'Laboratoare',
          items: [
            { label: 'Prezentare generală', slug: 'laboratoare' },
            {
              label: 'Un model de limbaj local cu Transformers',
              items: [{ autogenerate: { directory: 'laboratoare/model-local-transformers' } }],
            },
            {
              label: 'Imagini și sunete cu modele de difuzie',
              items: [{ autogenerate: { directory: 'laboratoare/difuzie-imagini-si-sunete' } }],
            },
            {
              label: 'Un model de limbaj de la zero',
              items: [{ autogenerate: { directory: 'laboratoare/model-lingvistic-de-la-zero' } }],
            },
            {
              label: 'Control continuu cu PPO în MuJoCo',
              items: [{ autogenerate: { directory: 'laboratoare/control-continuu-ppo-halfcheetah' } }],
            },
          ],
        },
        {
          label: 'Proiect',
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
      rehypePlugins: [rehypeKatex],
      // Ghilimelele drepte din proză devin ghilimele românești: „…” și «…».
      smartypants: {
        openingQuotes: { double: '„', single: '«' },
        closingQuotes: { double: '”', single: '»' },
      },
    }),
  },
});
