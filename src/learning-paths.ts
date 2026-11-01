// Traseele din harta de pe prima pagină (src/components/LearningPaths.astro). Un traseu este lista paginilor
// necesare pentru un scop, în ordinea în care se citesc. Titlul, descrierea și nivelul fiecărei stații vin din
// frontmatter-ul paginii, deci aici se aleg doar paginile și ordinea lor.
//
// Traseele pot avea în comun doar începutul: o pagină aflată pe mai multe trasee are în toate aceleași pagini
// înaintea ei. Harta le desenează împreună până acolo unde se despart. Ordinea traseelor de mai jos este și ordinea
// coloanelor de pe hartă, așa că un traseu care se desparte de altul vine imediat după ramura acestuia.
// O pagină inexistentă sau o pagină pusă în poziții diferite pe două trasee oprește build-ul cu un mesaj de eroare.

export interface LearningPath {
  name: string;
  /** Una-două propoziții, afișate sub numele traseului ales. */
  description: string;
  /** Culoarea liniei, din paleta temei: --sl-color-<color>. */
  color: 'blue' | 'orange' | 'purple' | 'green' | 'red';
  /** ID-urile paginilor (calea din src/content/docs, fără extensie). Un laborator apare prin pagina lui de început. */
  pages: string[];
}

const BAZA = [
  'concepte-de-baza/ce-este-inteligenta-artificiala',
  'concepte-de-baza/ce-este-invatarea-automata',
  'retele-neuronale/ce-sunt-retelele-neuronale',
];

export const LEARNING_PATHS: LearningPath[] = [
  {
    name: 'Cum funcționează un asistent ca ChatGPT',
    description:
      'De la învățarea automată la ce se află în spatele unui asistent conversațional: tokenuri, modele de limbaj mari, halucinații și raționament. Traseul se încheie cu un model de limbaj rulat pe propriul calculator.',
    color: 'blue',
    pages: [
      ...BAZA,
      'modele-lingvistice/ce-sunt-modelele-lingvistice-de-scara-larga',
      'modele-lingvistice/embeddings-si-tokenizare',
      'concepte-de-baza/chatgpt-gemini-claude-grok-deepseek',
      'modele-lingvistice/halucinatii',
      'modele-lingvistice/rationament-si-gandire',
      'concepte-de-baza/utilitatea-placilor-grafice',
      'laboratoare/model-local-transformers/prezentare',
    ],
  },
  {
    name: 'Cum se construiește un agent',
    description:
      'Ce se construiește în jurul unui model de limbaj ca să poată acționa: harnașamentul, apelul de instrumente, regăsirea documentelor, memoria și împărțirea sarcinilor între mai mulți agenți.',
    color: 'orange',
    pages: [
      ...BAZA,
      'modele-lingvistice/ce-sunt-modelele-lingvistice-de-scara-larga',
      'comportament-agentic/ce-este-comportamentul-agentic',
      'comportament-agentic/harnasamentul',
      'comportament-agentic/apelul-de-instrumente',
      'modele-lingvistice/generare-augmentata-prin-regasire-rag',
      'comportament-agentic/memoria-agentilor',
      'comportament-agentic/orchestrare-si-sisteme-multi-agent',
      'comportament-agentic/provocari-si-bune-practici',
      'comportament-agentic/exemple-de-sisteme-agentice',
    ],
  },
  {
    name: 'Cum se antrenează un model de limbaj',
    description:
      'Retropropagarea, mecanismul de atenție și arhitectura Transformer, apoi un model de tip GPT scris și antrenat de la zero în laborator. Traseul se încheie cu învățarea prin consolidare aplicată LLM-urilor.',
    color: 'purple',
    pages: [
      ...BAZA,
      'retele-neuronale/retropropagare',
      'modele-lingvistice/avem-nevoie-doar-de-atentie',
      'modele-lingvistice/arhitectura-transformer',
      'laboratoare/model-lingvistic-de-la-zero/prezentare',
      'modele-lingvistice/invatare-prin-consolidare-pentru-llm',
    ],
  },
  {
    name: 'Cum învață un robot',
    description:
      'Învățarea din recompense, de la stări, acțiuni și strategii de decizie la gradientul strategiei, apoi un robot simulat în MuJoCo care învață să alerge cu PPO.',
    color: 'green',
    pages: [
      ...BAZA,
      'retele-neuronale/retropropagare',
      'invatare-prin-consolidare/ce-este-invatarea-prin-consolidare',
      'invatare-prin-consolidare/gradientul-politicii-reinforce',
      'laboratoare/control-continuu-ppo-halfcheetah/prezentare',
    ],
  },
  {
    name: 'Cum se generează imagini, voce, video și text',
    description:
      'Cum creează un model de difuzie o imagine pornind de la zgomot, ce se află în spatele generatoarelor de imagini, voce și video, cum poate difuzia să scrie text și cum recunoaștem un conținut generat sau falsificat. Traseul se încheie cu imagini și sunete generate cu modele deschise.',
    color: 'red',
    pages: [
      ...BAZA,
      'modele-de-difuzie/ce-sunt-modelele-de-difuzie',
      'modele-de-difuzie/generarea-imaginilor',
      'modele-de-difuzie/generarea-vocii',
      'modele-de-difuzie/generarea-video',
      'modele-de-difuzie/generarea-textului',
      'laboratoare/difuzie-imagini-si-sunete/prezentare',
    ],
  },
];

/**
 * Etichete scurte pentru stațiile al căror titlu nu încape pe hartă în două rânduri, după ID-ul paginii.
 * Fără o etichetă de aici, harta folosește titlul paginii, apoi `sidebar.label`.
 */
export const SHORT_LABELS: Record<string, string> = {};
