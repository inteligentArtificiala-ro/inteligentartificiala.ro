# inteligentartificiala.ro

Documentation in Romanian about artificial intelligence, from basic concepts to the implementation of large language models. Built with [Astro](https://astro.build), [Starlight](https://starlight.astro.build) and the [Exquisitus](https://github.com/anaxite/starlight-theme-exquisitus) theme.

```bash
npm install
npm run dev          # http://localhost:4321
npm run dev:search   # build + preview, with search working
npm run build        # dist/ + search index
npm run check        # types and lint
```

## Labs and Colab notebooks

Every lab has one Jupyter notebook, `public/laboratoare/<lab>/<lab>.ipynb`, with all of its code. Google Colab opens it straight from this repository's `main` branch, and each lab's introduction page links to it.

| Lab | Colab |
| --- | --- |
| [Un model de limbaj local cu Transformers](https://inteligentartificiala.ro/laboratoare/model-local-transformers/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/model-local-transformers/model-local-transformers.ipynb) |
| [Imagini și sunete cu modele de difuzie](https://inteligentartificiala.ro/laboratoare/difuzie-imagini-si-sunete/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/difuzie-imagini-si-sunete/difuzie-imagini-si-sunete.ipynb) |
| [Un model de limbaj de la zero (mvGPT)](https://inteligentartificiala.ro/laboratoare/model-lingvistic-de-la-zero/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/model-lingvistic-de-la-zero/model-lingvistic-de-la-zero.ipynb) |
| [Control continuu cu PPO în MuJoCo](https://inteligentartificiala.ro/laboratoare/control-continuu-ppo-halfcheetah/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/control-continuu-ppo-halfcheetah/control-continuu-ppo-halfcheetah.ipynb) |

The notebooks of the first two labs are generated from the code blocks of the lab pages, so changes go into the pages, not into the notebooks. The mvGPT and PPO notebooks run those labs' scripts.

## Videos

The site has its own pages for the project's Romanian video series (https://www.youtube.com/@inteligentArtificiala): `/videouri/` lists the episodes and `/videouri/<id>/` shows one, with its chapters, code steps and transcript. Each episode is `src/content/videouri/<id>.json`, the `release.json` that aphrodite writes in the series' studio, copied here with its thumbnails (`public/videouri/`) by the studio's `scripts/site-sync.sh`. A documentation page includes an episode with `<Video id="<id>" />` (`src/components/Video.astro`), optionally from a chapter (`capitol="…"`) or a second (`la={754}`). The player loads from YouTube only when a reader presses play.

- Licenses: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)

Every push to `main` is published automatically to GitHub Pages (`.github/workflows/deploy.yml`).
