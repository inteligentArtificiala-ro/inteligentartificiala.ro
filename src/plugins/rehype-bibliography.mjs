// @ts-check

/**
 * @typedef {import('hast').Root} Root
 * @typedef {import('hast').Element} Element
 * @typedef {import('hast').ElementContent} ElementContent
 * @typedef {import('hast').Properties} Properties
 * @typedef {Root | ElementContent} Node
 */

/**
 * Secțiunea „Bibliografie” de la sfârșitul paginilor: titlul `## Bibliografie`, urmat de o listă cu intrări de forma
 * „Autori (an). [Titlu](adresă). _Publicație_.”, în ordine alfabetică.
 *
 * - Lista primește clasa `bibliografie`, iar fiecare intrare un id stabil (`bib-vaswani-2017`), ca să poată fi legată
 *   direct. Autorii, anul și titlul sunt marcați separat, pentru stilurile din src/styles/custom.css.
 * - O legătură din text către aceeași adresă ca titlul unei intrări primește un id (`cit-vaswani-2017`), iar intrarea
 *   primește o legătură înapoi (↩) pentru fiecare loc din text în care este citată.
 * - La build, semnalează intrările care nu au anul după autori și pe cele care nu sunt în ordine alfabetică.
 */
export default function rehypeBibliography() {
  return (/** @type {Root} */ tree, /** @type {{ path?: string }} */ file) => {
    const list = findList(tree);
    if (!list) return;

    const page = (file.path ?? '').replace(/^.*\/src\/content\/docs\//, '');
    list.properties.className = ['bibliografie'];
    list.properties.role = 'list';
    list.properties.ariaLabelledBy = 'bibliografie';

    /** @type {{ item: Element, content: Element, authors: string, year: string, key: string }[]} */
    const entries = [];
    for (const item of list.children) {
      if (item.type !== 'element' || item.tagName !== 'li') continue;
      // Într-o listă „aerisită” (cu rânduri goale între intrări), textul intrării este într-un paragraf.
      const [first] = item.children.filter((child) => child.type !== 'text' || child.value.trim());
      const content = first?.type === 'element' && first.tagName === 'p' ? first : item;
      const parts = markAuthorsAndYear(content);
      if (!parts) {
        console.warn(`[bibliografie] ${page}: intrare fără „(an)” după autori: ${toText(item).slice(0, 80)}`);
        continue;
      }
      entries.push({
        item,
        content,
        ...parts,
        key: `${slug(parts.authors)}-${parts.year === 'f.a.' ? 'fa' : parts.year}`,
      });
    }

    // Lucrările aceluiași autor din același an se deosebesc printr-o literă: openai-2024a, openai-2024b
    // (google-deepmind-fa-a pentru sursele fără an).
    const keys = entries.map((entry) => entry.key);
    entries.forEach((entry, index) => {
      if (keys.filter((key) => key === keys[index]).length < 2) return;
      const letter = String.fromCharCode(97 + keys.slice(0, index).filter((key) => key === keys[index]).length);
      entry.key += entry.year === 'f.a.' ? `-${letter}` : letter;
    });

    const collator = new Intl.Collator('ro', { sensitivity: 'base', ignorePunctuation: true });
    /** @type {Map<string, { content: Element, key: string, citations: string[] }>} */
    const byHref = new Map();
    entries.forEach((entry, index) => {
      entry.item.properties.id = `bib-${entry.key}`;
      const title = entry.content.children.find((child) => child.type === 'element' && child.tagName === 'a');
      if (title?.type === 'element') {
        title.properties.className = ['bib-titlu'];
        const href = normalizeHref(title.properties.href);
        if (href && !byHref.has(href)) byHref.set(href, { content: entry.content, key: entry.key, citations: [] });
      }
      const previous = entries[index - 1];
      if (previous && compareEntries(collator, previous, entry) > 0) {
        console.warn(
          `[bibliografie] ${page}: „${entry.authors} (${entry.year})” ar trebui să fie înainte de „${previous.authors} (${previous.year})”`,
        );
      }
    });

    // Legăturile din text către lucrările din bibliografie.
    walkLinks(tree, list, (link) => {
      const cited = byHref.get(normalizeHref(link.properties.href) ?? '');
      if (!cited) return;
      if (!link.properties.id) {
        const n = cited.citations.length + 1;
        link.properties.id = n === 1 ? `cit-${cited.key}` : `cit-${cited.key}-${n}`;
      }
      cited.citations.push(String(link.properties.id));
    });

    for (const { content, citations } of byHref.values()) {
      if (!citations.length) continue;
      content.children.push(
        { type: 'text', value: ' ' },
        element(
          'span',
          { className: ['bib-citari'], dataPagefindIgnore: true },
          citations.map((id, index) =>
            element(
              'a',
              {
                className: ['bib-inapoi'],
                href: `#${id}`,
                ariaLabel:
                  citations.length === 1 ? 'Înapoi la citarea din text' : `Înapoi la citarea ${index + 1} din text`,
              },
              // U+FE0E cere forma de text a săgeții, nu emoji-ul (pe iOS).
              index === 0 ? [text('↩︎')] : [text('↩︎'), element('sup', {}, [text(String(index + 1))])],
            ),
          ),
        ),
      );
    }
  };
}

/**
 * Lista de după titlul „Bibliografie”. Titlul poate fi deja învelit de Starlight în `div.sl-heading-wrapper`, în funcție
 * de ordinea în care rulează pluginurile.
 * @param {Root} tree
 */
function findList(tree) {
  const children = tree.children;
  const start = children.findIndex(
    (node) =>
      node.type === 'element' &&
      (isHeading(node) || node.children.some((child) => child.type === 'element' && isHeading(child))),
  );
  if (start < 0) return undefined;
  const next = children.slice(start + 1).find((node) => node.type !== 'text' || node.value.trim());
  return next?.type === 'element' && next.tagName === 'ul' ? next : undefined;
}

/** @param {Element} node */
function isHeading(node) {
  return node.tagName === 'h2' && toText(node).trim() === 'Bibliografie';
}

/**
 * Învelește „Autori” și „(an)” de la începutul intrării în `span.bib-autori` și `span.bib-an`.
 * @param {Element} content
 */
function markAuthorsAndYear(content) {
  const children = content.children;
  for (let index = 0; index < children.length; index++) {
    const child = children[index];
    if (child.type === 'element' && child.tagName === 'a') return undefined;
    if (child.type !== 'text') continue;
    const match = /\s*\((\d{4}|f\.a\.)\)/.exec(child.value);
    if (!match) continue;

    const authors = [...children.slice(0, index), text(child.value.slice(0, match.index))];
    content.children = [
      element('span', { className: ['bib-autori'] }, authors),
      text(' '),
      element('span', { className: ['bib-an'] }, [text(`(${match[1]})`)]),
      text(child.value.slice(match.index + match[0].length)),
      ...children.slice(index + 1),
    ];
    return { authors: authors.map(toText).join('').trim(), year: match[1] };
  }
  return undefined;
}

/**
 * Ordinea alfabetică: după numele primului autor („Ba” înaintea lui „Bahdanau”), apoi după restul autorilor (fără
 * punctuație și diacritice), apoi după an. „f.a.” vine după orice an.
 * @param {Intl.Collator} collator
 * @param {{ authors: string, year: string }} a
 * @param {{ authors: string, year: string }} b
 */
function compareEntries(collator, a, b) {
  const surname = (/** @type {string} */ authors) => authors.split(',')[0];
  return (
    collator.compare(surname(a.authors), surname(b.authors)) ||
    collator.compare(a.authors, b.authors) ||
    collator.compare(a.year, b.year)
  );
}

/**
 * Primul nume din lista de autori, ca bucată de id: „Vaswani, A. et al.” → `vaswani`, „Google DeepMind” →
 * `google-deepmind`.
 * @param {string} authors
 */
function slug(authors) {
  return authors
    .split(/,| et al\.| și /)[0]
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .split('-')
    .slice(0, 3)
    .join('-');
}

/** @param {unknown} href */
function normalizeHref(href) {
  return typeof href === 'string' && /^https?:/.test(href)
    ? href
        .replace(/^http:/, 'https:')
        .replace(/#.*$/, '')
        .replace(/\/$/, '')
    : undefined;
}

/**
 * Toate legăturile din pagină, în afară de cele din bibliografie.
 * @param {Node} node
 * @param {Element} skip
 * @param {(link: Element) => void} visit
 */
function walkLinks(node, skip, visit) {
  if (node === skip) return;
  if (node.type === 'element' && node.tagName === 'a') visit(node);
  if ('children' in node) for (const child of node.children) walkLinks(/** @type {Node} */ (child), skip, visit);
}

/**
 * @param {Node} node
 * @returns {string}
 */
function toText(node) {
  if (node.type === 'text') return node.value;
  return 'children' in node ? node.children.map((child) => toText(/** @type {Node} */ (child))).join('') : '';
}

/**
 * @param {string} value
 * @returns {import('hast').Text}
 */
function text(value) {
  return { type: 'text', value };
}

/**
 * @param {string} tagName
 * @param {Properties} properties
 * @param {ElementContent[]} children
 * @returns {Element}
 */
function element(tagName, properties, children) {
  return { type: 'element', tagName, properties, children };
}
