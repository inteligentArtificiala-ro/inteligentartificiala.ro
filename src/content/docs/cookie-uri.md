---
title: Cookie-uri și confidențialitate
description: Ce date colectează site-ul, cu ce scop și cum poate fi retras acordul pentru cookie-urile de analiză.
---

_Actualizat pe 1 noiembrie 2026_

## Pe scurt

:::note[Pe scurt]
InteligentArtificiala.ro folosește două servicii externe care pot plasa cookie-uri. Google Analytics se încarcă **doar după acceptare**, din bannerul afișat la prima vizită. Playerul YouTube se încarcă **doar la apăsarea butonului de redare** al unui video. Fără acord și fără redarea unui video, pe site nu rulează niciun script Google.
:::

## Google Analytics

Statisticile de trafic arată ce pagini sunt citite și cum ajung vizitatorii pe site. Serviciul este oferit de Google Ireland Limited. După acceptare, Google Analytics poate colecta, de exemplu, paginile vizitate, sursa traficului, tipul de dispozitiv și de browser și o localizare aproximativă. Semnalele pentru publicitate sunt dezactivate.

| Cookie   | Scop                         | Durată |
| -------- | ---------------------------- | ------ |
| `_ga`    | deosebește vizitatorii unici | 2 ani  |
| `_ga_*`  | păstrează starea sesiunii    | 2 ani  |

Temeiul prelucrării este consimțământul (art. 6 alin. (1) lit. a) din Regulamentul (UE) 2016/679, GDPR).

## Retragerea acordului

:::tip[Retragerea acordului]
Acordul poate fi retras oricând din linkul „Setări cookie-uri” din subsolul fiecărei pagini. La refuz, cookie-urile Google Analytics sunt șterse din browser.
:::

## Ce se salvează local

Alegerea din banner este păstrată în browser, în `localStorage`, sub cheia `consimtamant-analiza`, ca bannerul să nu apară din nou la fiecare pagină. Valoarea nu este trimisă nicăieri. Tot în `localStorage` este păstrat și modul de afișare ales (luminos sau întunecat).

Harta traseelor de pe prima pagină arată ce pagini au fost deja deschise și de unde poate continua un traseu. Pentru asta, adresele paginilor deschise sunt păstrate în `localStorage`, sub cheia `pagini-vizitate`, iar traseul ales pe hartă sub cheia `traseu-ales`. Nici acestea nu sunt trimise nicăieri și pot fi șterse din setările browserului, odată cu celelalte date ale site-ului.

Paginile cu exemple de cod Python care pot fi rulate folosesc și IndexedDB, tot în browser. După prima rulare, interpretorul Python păstrează acolo pachetele descărcate (de exemplu NumPy), ca să nu le descarce din nou la vizitele următoare. Datele pot fi șterse din setările browserului, odată cu celelalte date ale site-ului.

Demo-ul cu modelul de limbaj de pe pagina _Modele de limbaj mari (LLM)_ păstrează fișierele modelului (circa 170 MB) în Cache Storage, sub numele `transformers-cache`, doar după apăsarea butonului de încărcare și doar dacă browserul are spațiu suficient. Butonul „Ștergerea modelului din browser” din demo le șterge.

## Videourile de pe YouTube

Pagina [Videouri](/videouri/) și unele pagini din documentație includ episoade din seria video a proiectului, publicate pe YouTube. Până la apăsarea butonului de redare, pagina nu contactează YouTube: imaginea videoului este servită de pe același domeniu. La apăsarea butonului, playerul se încarcă de pe youtube-nocookie.com, varianta playerului YouTube (Google Ireland Limited) cu confidențialitate îmbunătățită. Din acel moment, YouTube primește adresa IP și date tehnice despre browser și poate păstra în browser cookie-uri și alte date, pentru redare, statistici și securitate, conform [politicii de confidențialitate Google](https://policies.google.com/privacy). Linkurile „Pe YouTube” deschid videoul direct pe youtube.com.

## Găzduire și alte servicii

Site-ul este găzduit pe GitHub Pages (GitHub, Inc.), care poate păstra jurnale tehnice ale accesărilor, de exemplu adresa IP, pentru securitate și funcționare. Fonturile sunt servite de pe același domeniu, iar căutarea rulează integral în browser, pe baza unui index static. Nici fonturile, nici căutarea nu trimit date către alți terți.

## Exemple de cod Python

Unele pagini conțin exemple de cod Python care pot fi modificate și rulate în browser, cu [PyScript](https://pyscript.net). PyScript este servit de pe același domeniu. Interpretorul Python ([Pyodide](https://pyodide.org)) și pachetele folosite de exemple sunt descărcate de pe cdn.jsdelivr.net, rețeaua de distribuție a conținutului jsDelivr, doar la apăsarea butonului „Rulare”. Ca la orice descărcare, serviciul primește adresa IP și date tehnice despre browser. jsDelivr nu plasează cookie-uri. Codul rulează integral în browser și nu este trimis nicăieri.

## Demo-ul cu modelul de limbaj

Modelul SmolLM2 135M și biblioteca care îl rulează (Transformers.js, cu ONNX Runtime) sunt servite de pe același domeniu, deci demo-ul nu contactează alte servicii. Mesajele scrise în demo și răspunsurile modelului rămân în browser și nu sunt trimise nicăieri.

## Contact

Întrebările despre datele personale pot fi trimise la [contact@inteligentartificiala.ro](mailto:contact@inteligentartificiala.ro).
