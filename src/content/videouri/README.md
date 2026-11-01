# Videouri

Câte un fișier `<id>.json` pentru fiecare episod publicat al seriei video: `release.json`-ul scris de aphrodite în
studioul seriei (`inteligentartificiala-series/episodes/<id>/release.json`), copiat aici de `scripts/site-sync.sh` din
studio, împreună cu miniaturile `public/videouri/<id>.jpg` (1280×720) și `<id>-mica.jpg` (640×360). Nu se editează de
mână: se schimbă episodul în studio și se copiază din nou.

Schema este colecția `videouri` din `src/content.config.ts`; paginile sunt `src/pages/videouri/`.
