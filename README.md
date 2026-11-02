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
| [Rețele neuronale de la zero](https://inteligentartificiala.ro/laboratoare/retele-neuronale-de-la-zero/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/retele-neuronale-de-la-zero/retele-neuronale-de-la-zero.ipynb) |
| [Control continuu cu PPO în MuJoCo](https://inteligentartificiala.ro/laboratoare/control-continuu-ppo-halfcheetah/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/control-continuu-ppo-halfcheetah/control-continuu-ppo-halfcheetah.ipynb) |
| [Un model de limbaj de la zero (mvGPT)](https://inteligentartificiala.ro/laboratoare/model-lingvistic-de-la-zero/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/model-lingvistic-de-la-zero/model-lingvistic-de-la-zero.ipynb) |
| [Un model de limbaj local cu Transformers](https://inteligentartificiala.ro/laboratoare/model-local-transformers/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/model-local-transformers/model-local-transformers.ipynb) |
| [Imagini și sunete cu modele de difuzie](https://inteligentartificiala.ro/laboratoare/difuzie-imagini-si-sunete/prezentare/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inteligentArtificiala-ro/inteligentartificiala.ro/blob/main/public/laboratoare/difuzie-imagini-si-sunete/difuzie-imagini-si-sunete.ipynb) |

The notebooks of the Transformers and diffusion labs are generated from the code blocks of the lab pages, so changes go into the pages, not into the notebooks. The PPO, neural-networks-from-scratch and mvGPT notebooks are written by hand and run those labs' scripts.

### Weekly runs

Every Monday, [`verificare-laboratoare.yml`](.github/workflows/verificare-laboratoare.yml) runs every lab notebook from the first cell to the last, as in a fresh Colab runtime (root, Python 3.12, PyTorch preinstalled) but on a CPU-only GitHub Actions runner. The cells download the lab code from the live site, so the run checks what readers get, and a `!` or `%pip` command that fails stops the run. [`scripts/verificare-laboratoare.py`](scripts/verificare-laboratoare.py) runs each notebook with nbclient and merges the results into `verificari.json` on the `verificari` branch; the executed notebooks are kept as workflow artifacts for 30 days. When the workflow finishes, the deploy runs, copies `verificari.json` into `src/data/`, and each lab's introduction page shows the last run under the Colab button: the date and duration, or the cell where it stopped, with a link to the log. To see the results locally:

```bash
git fetch origin verificari && mkdir -p src/data && git show FETCH_HEAD:verificari.json > src/data/verificari.json
```

## Videos

The site has its own pages for the project's Romanian video series (https://www.youtube.com/@inteligentArtificiala): `/videouri/` lists the episodes and `/videouri/<id>/` shows one, with its chapters, code steps and transcript. Each episode is `src/content/videouri/<id>.json`, the `release.json` that aphrodite writes in the series' studio, copied here with its thumbnails (`public/videouri/`) by the studio's `scripts/site-sync.sh`. A documentation page includes an episode with `<Video id="<id>" />` (`src/components/Video.astro`), optionally from a chapter (`capitol="…"`) or a second (`la={754}`). The player loads from YouTube only when a reader presses play.

- Licenses: the site's own code and content are under the MIT licence ([`LICENSE`](LICENSE)); third-party parts (the theme, fonts, PyScript, the model in `public/modele/`) keep their own licences, listed in [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)

Every push to `main` is published automatically to GitHub Pages (`.github/workflows/deploy.yml`).
