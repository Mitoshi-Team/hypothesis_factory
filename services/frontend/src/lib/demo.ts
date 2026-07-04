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
