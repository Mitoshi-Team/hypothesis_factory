// Built-in demo account. Signing in with DEMO_USERNAME / DEMO_PASSWORD flips the
// API client into an offline "demo mode": every session/message/result call is
// served from the canned data below instead of hitting the backend. Handy for
// showing the UI (history, threads, hypothesis cards) without a running gateway.
//
// api.ts owns the localStorage sentinel and routes each call here when it's set;
// this module only builds the mock domain objects.

import type { HypothesisResult, KnowledgeGraph, Session, Weights } from '@/types'

export const DEMO_USERNAME = 'demo'
export const DEMO_PASSWORD = 'demo'

/** Stored in place of a refresh token to mark the session as demo. */
export const DEMO_SENTINEL = 'hf-demo-mode'

// Fixed timestamps so the two seeded chats look like real history.
const DAY = 24 * 60 * 60 * 1000

function isoDaysAgo(days: number): string {
  return new Date(Date.now() - days * DAY).toISOString()
}

const DEMO_WEIGHTS: Weights = { novelty: 1.5, feasibility: 1.0, effect: 2.0, risk: 0.5 }

// ---------------------------------------------------------------------------
// Seed chats — fully hydrated sessions with hypothesis results.

function buildSeedSessions(): Session[] {
  return [
    {
      id: 'sess_demo_alloy',
      title: 'Повысить жаропрочность никелевого сплава ХН62 на 15%',
      createdAt: isoDaysAgo(1),
      constraints:
        'Себестоимость шихты — не выше текущей. Технология вакуумно-индукционной плавки без изменений. Допустимо микролегирование до 0,5% масс.',
      weights: DEMO_WEIGHTS,
      loaded: true,
      messages: [
        {
          id: 'msg_demo_alloy_u0',
          role: 'user',
          content:
            'Нужно повысить жаропрочность никелевого сплава ХН62 примерно на 15% при рабочей температуре 950 °C. Важно не увеличивать себестоимость шихты и сохранить действующую технологию литья.',
          files: [],
        },
        {
          id: 'msg_demo_alloy_a0',
          role: 'assistant',
          status: 'done',
          iteration: 0,
          result: {
            title: 'Микролегирование рением с рафинированием по сере и фосфору',
            hypothesis:
              'Ввести 0,3–0,4% масс. рения в сочетании с глубоким рафинированием расплава по сере (<10 ppm) и фосфору. Рений замедляет диффузию в γ-матрице и стабилизирует γ′-фазу, а снижение примесей по границам зёрен подавляет зернограничное проскальзывание при 950 °C.',
            expectedEffect:
              'Ожидаемый рост предела длительной прочности σ₁₀₀ при 950 °C на 12–16% без изменения плотности отливки и параметров литья.',
            scores: { novelty: 7, feasibility: 6, effect: 8, risk: 4 },
            verdict: 'accept',
            risks: [
              'Рений — дорогой и дефицитный компонент: даже 0,3% заметно влияют на стоимость шихты.',
              'Риск ликвации рения при недостаточной гомогенизации расплава.',
              'Требуется контроль содержания серы на уровне <10 ppm, что усложняет входной контроль шихты.',
            ],
            suggestions: [
              'Проверить частичную замену рения на рутений для снижения стоимости.',
              'Заложить режим гомогенизирующего отжига 1260 °C / 4 ч.',
            ],
            evidenceSources: [
              'ГОСТ 5632-2014 «Стали и сплавы коррозионностойкие, жаростойкие и жаропрочные»',
              'Патент RU 2 585 591 C1 — жаропрочный никелевый сплав',
              'Reed R.C. «The Superalloys: Fundamentals and Applications», Cambridge, 2006',
            ],
          },
        },
      ],
    },
    {
      id: 'sess_demo_corrosion',
      title: 'Коррозионная стойкость Д16 в морской среде',
      createdAt: isoDaysAgo(4),
      constraints:
        'Предел прочности не ниже 440 МПа. Анодирование допустимо. Изменение химсостава основы — минимальное.',
      weights: { novelty: 1.0, feasibility: 1.5, effect: 1.5, risk: 1.0 },
      loaded: true,
      messages: [
        {
          id: 'msg_demo_corr_u0',
          role: 'user',
          content:
            'Повысить коррозионную стойкость алюминиевого сплава Д16 в морской среде без существенной потери прочности на растяжение.',
          files: [],
        },
        {
          id: 'msg_demo_corr_a0',
          role: 'assistant',
          status: 'done',
          iteration: 0,
          result: {
            title: 'Плакирование чистым алюминием (технология альклэд)',
            hypothesis:
              'Нанести на лист Д16 двусторонний плакирующий слой технически чистого алюминия А5 толщиной 4–5% от толщины листа. Чистый алюминий работает как протекторный анод и физический барьер против питтинга в хлоридной среде.',
            expectedEffect:
              'Существенное снижение скорости питтинговой коррозии в 3% NaCl; ресурс в морской атмосфере вырастает в 2–3 раза.',
            scores: { novelty: 3, feasibility: 8, effect: 7, risk: 6 },
            verdict: 'reject',
            risks: [
              'Плакирующий слой снижает эффективное сечение и предел прочности листа на 6–10% — риск выхода за 440 МПа.',
              'Технология неприменима к готовым профилям и сварным узлам.',
            ],
            suggestions: [
              'Рассмотреть комбинацию с анодированием вместо плакирования.',
              'Оценить локальное плакирование только зон повышенного риска.',
            ],
            evidenceSources: [
              'ГОСТ 4784-2019 «Алюминий и сплавы алюминиевые деформируемые»',
              'Синявский В.С. «Коррозия и защита алюминиевых сплавов», 2004',
            ],
          },
        },
        {
          id: 'msg_demo_corr_u1',
          role: 'user',
          content:
            'Плакирование не подходит — теряем прочность. Можно ли обойтись без снижения несущего сечения?',
          files: [],
        },
        {
          id: 'msg_demo_corr_a1',
          role: 'assistant',
          status: 'done',
          iteration: 1,
          result: {
            title: 'Твёрдое анодирование с наполнением ингибитором в порах',
            hypothesis:
              'Сформировать слой твёрдого сернокислотного анодирования 25–40 мкм с последующим наполнением пор раствором ингибитора (молибдат или соли церия) вместо горячей воды. Барьерный оксид и самозалечивающий ингибитор блокируют инициацию питтинга, не затрагивая несущее сечение основного металла.',
            expectedEffect:
              'Скорость коррозии в 3% NaCl снижается на 60–75%; предел прочности сохраняется на уровне ≥445 МПа (потеря <1%).',
            scores: { novelty: 6, feasibility: 7, effect: 7, risk: 3 },
            verdict: 'accept',
            risks: [
              'Анодный слой снижает усталостную прочность на 8–12% — критично для циклически нагруженных деталей.',
              'Наполнение соединениями церия удорожает и усложняет линию.',
            ],
            suggestions: [
              'Ввести контроль усталости для ответственных деталей.',
              'Проверить ресурс наполнения молибдатом как более дешёвой альтернативой церию.',
            ],
            evidenceSources: [
              'ГОСТ 9.305-84 «ЕСЗКС. Покрытия металлические и неметаллические»',
              'ISO 10074:2021 Hard anodizing of aluminium',
              'Патент RU 2 543 659 C2 — способ защиты алюминиевых сплавов',
            ],
          },
        },
      ],
    },
  ]
}

// A single mutable copy so demo-created sessions persist for the tab's lifetime.
let seedSessions: Session[] | null = null

function sessions(): Session[] {
  if (!seedSessions) seedSessions = buildSeedSessions()
  return seedSessions
}

let demoSeq = 0
const demoId = (p: string) => `${p}_${demoSeq++}`

// ---------------------------------------------------------------------------
// Public API used by api.ts under demo mode.

/** History list — summaries only, matching `fetchSessions`. */
export function demoSessionList(): Session[] {
  return sessions().map((s) => ({
    ...s,
    messages: [],
    loaded: false,
  }))
}

/** Full session (messages + results), matching `fetchSessionDetail`. */
export function demoSessionDetail(id: string): Session | null {
  return sessions().find((s) => s.id === id) ?? null
}

export function demoCreateSession(input: {
  title: string
  constraints: string
  weights: Weights
}): Session {
  const session: Session = {
    id: demoId('sess_demo_new'),
    title: input.title,
    createdAt: new Date().toISOString(),
    constraints: input.constraints,
    weights: input.weights,
    messages: [],
    loaded: true,
  }
  sessions().unshift(session)
  return session
}

export function demoMessageId(): string {
  return demoId('msg_demo_new')
}

// ---------------------------------------------------------------------------
// Demo knowledge graph — compact but realistic (superalloy domain), themed to
// match the seed sessions. A small connected core (shown by default) plus
// isolated NER entities that only appear under "Show all entities".

function chunk(documentTitle: string, sectionPath: string, text: string) {
  return [{ chunkId: `chunk_${demoSeq++}`, text, documentTitle, sectionPath }]
}

let demoGraphCache: KnowledgeGraph | null = null

export function demoGraph(): KnowledgeGraph {
  if (demoGraphCache) return demoGraphCache

  // Connected core -----------------------------------------------------------
  const core = [
    {
      id: 'ent_alloy',
      label: 'Material',
      name: 'Сплав ХН62',
      score: 0.94,
      sourceChunks: chunk(
        'ГОСТ 5632-2014',
        'Жаропрочные никелевые сплавы',
        'Сплав ХН62 — деформируемый жаропрочный никелевый сплав, упрочняемый выделениями γ′-фазы; применяется для деталей, работающих при 900–1000 °C.',
      ),
    },
    {
      id: 'ent_re',
      label: 'Material',
      name: 'Рений (Re)',
      score: 0.88,
      sourceChunks: chunk(
        'Reed R.C. The Superalloys',
        'Refractory elements',
        'Рений замедляет диффузию в γ-матрице и повышает сопротивление ползучести, стабилизируя структуру при высоких температурах.',
      ),
    },
    {
      id: 'ent_gammap',
      label: 'Material',
      name: 'γ′-фаза (Ni₃Al)',
      score: 0.9,
      sourceChunks: chunk(
        'Reed R.C. The Superalloys',
        'Strengthening mechanisms',
        'Дисперсные когерентные выделения γ′-фазы Ni₃(Al,Ti) — основной упрочняющий механизм жаропрочных никелевых сплавов.',
      ),
    },
    {
      id: 'ent_creep',
      label: 'Property',
      name: 'Предел длительной прочности σ₁₀₀',
      score: 0.82,
      sourceChunks: chunk(
        'Внутренний отчёт ЛИ-2024-117',
        'Испытания на ползучесть',
        'σ₁₀₀ при 950 °C — целевой показатель; рост на 12–16% ожидается при микролегировании рением.',
      ),
    },
    {
      id: 'ent_anneal',
      label: 'Process',
      name: 'Гомогенизирующий отжиг',
      score: 0.85,
      sourceChunks: chunk(
        'Reed R.C. The Superalloys',
        'Heat treatment',
        'Гомогенизирующий отжиг устраняет ликвацию легирующих элементов перед старением, обеспечивая равномерное распределение рения.',
      ),
    },
    {
      id: 'ent_temp',
      label: 'Parameter',
      name: 'Температура 1260 °C',
      score: 0.8,
      sourceChunks: chunk(
        'Внутренний отчёт ЛИ-2024-117',
        'Режимы термообработки',
        'Режим гомогенизации 1260 °C / 4 ч подобран для растворения первичных выделений без оплавления границ зёрен.',
      ),
    },
    {
      id: 'ent_sulfur',
      label: 'Parameter',
      name: 'Содержание серы <10 ppm',
      score: 0.77,
      sourceChunks: chunk(
        'ГОСТ 5632-2014',
        'Требования к чистоте',
        'Снижение серы по границам зёрен ниже 10 ppm подавляет зернограничное проскальзывание при рабочих температурах.',
      ),
    },
  ]

  const edges = [
    { source: 'ent_alloy', target: 'ent_re', relation: 'contains', confidence: 0.95, evidence: 'Ввод 0,3–0,4% масс. рения в состав сплава ХН62.' },
    { source: 'ent_alloy', target: 'ent_gammap', relation: 'contains', confidence: 0.92, evidence: 'γ′-фаза выделяется в матрице сплава ХН62.' },
    { source: 'ent_re', target: 'ent_gammap', relation: 'influences', confidence: 0.9, evidence: 'Рений стабилизирует γ′-фазу и замедляет её коагуляцию.' },
    { source: 'ent_re', target: 'ent_creep', relation: 'influences', confidence: 0.88, evidence: 'Рений повышает предел длительной прочности за счёт торможения диффузии.' },
    { source: 'ent_re', target: 'ent_anneal', relation: 'requires', confidence: 0.84, evidence: 'Равномерное распределение рения требует гомогенизирующего отжига.' },
    { source: 'ent_anneal', target: 'ent_temp', relation: 'requires', confidence: 0.86, evidence: 'Отжиг проводится при 1260 °C.' },
    { source: 'ent_anneal', target: 'ent_gammap', relation: 'produces', confidence: 0.8, evidence: 'Последующее старение формирует дисперсную γ′-фазу.' },
    { source: 'ent_sulfur', target: 'ent_creep', relation: 'influences', confidence: 0.82, evidence: 'Рафинирование по сере повышает сопротивление ползучести.' },
  ]

  const chains = [
    { chainId: 'ch_demo_1', nodeIds: ['ent_alloy', 'ent_re', 'ent_gammap'], edgeLabels: ['contains', 'influences'], summary: 'contains → influences' },
    { chainId: 'ch_demo_2', nodeIds: ['ent_re', 'ent_anneal', 'ent_temp'], edgeLabels: ['requires', 'requires'], summary: 'requires → requires' },
    { chainId: 'ch_demo_3', nodeIds: ['ent_re', 'ent_creep'], edgeLabels: ['influences'], summary: 'influences' },
    { chainId: 'ch_demo_4', nodeIds: ['ent_sulfur', 'ent_creep'], edgeLabels: ['influences'], summary: 'influences' },
  ]

  // Isolated entities (only visible under "Show all entities") ----------------
  const isolatedSpec: Array<[string, KnowledgeGraph['nodes'][number]['label'], number]> = [
    ['Никель', 'Material', 0.72],
    ['Хром', 'Material', 0.7],
    ['Кобальт', 'Material', 0.68],
    ['Рутений', 'Material', 0.66],
    ['Карбиды NbC', 'Material', 0.63],
    ['Молибден', 'Material', 0.61],
    ['Вольфрам', 'Material', 0.6],
    ['Вакуумно-индукционная плавка', 'Process', 0.74],
    ['Рафинирование расплава', 'Process', 0.69],
    ['Литьё по выплавляемым моделям', 'Process', 0.64],
    ['Ковка', 'Process', 0.58],
    ['Старение', 'Process', 0.71],
    ['Пластичность', 'Property', 0.62],
    ['Плотность отливки', 'Property', 0.57],
    ['Стойкость к окислению', 'Property', 0.6],
    ['0,3% масс.', 'Parameter', 0.55],
    ['Рабочая температура 950 °C', 'Parameter', 0.73],
    ['Скорость охлаждения', 'Parameter', 0.54],
  ]
  const isolated = isolatedSpec.map(([name, label], i) => ({
    id: `ent_iso_${i}`,
    label,
    name,
    score: isolatedSpec[i][2],
    sourceChunks: chunk('База знаний', 'Извлечённые сущности', `Сущность «${name}» распознана в загруженных материалах.`),
  }))

  demoGraphCache = { nodes: [...core, ...isolated], edges, chains }
  return demoGraphCache
}

/** Canned result returned for anything sent live in demo mode. */
export function demoResult(): HypothesisResult {
  return {
    title: 'Комплексное микролегирование под заданные ограничения',
    hypothesis:
      'Демонстрационная гипотеза: в рабочем режиме система подобрала бы состав легирующего комплекса и режим термообработки под ваши ограничения и веса критериев на основе базы знаний. Здесь ответ сформирован из образца.',
    expectedEffect:
      'Эффект оценивается по заданным весам критериев; приведены ориентировочные демонстрационные значения.',
    scores: { novelty: 6, feasibility: 6, effect: 7, risk: 4 },
    verdict: 'accept',
    risks: ['Демо-режим: результат не основан на реальной базе знаний.'],
    suggestions: [
      'Войдите под реальной учётной записью, чтобы получить обоснованную гипотезу.',
    ],
    evidenceSources: ['Демонстрационный источник'],
  }
}
