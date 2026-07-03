import type { BusinessReport, HistoryEntry } from '@/types'

export const MOCK_REPORT: BusinessReport = {
  id: 'rep-2026-0703-01',
  createdAt: '2026-07-03T12:40:00.000Z',
  problem: 'Повысить жаропрочность никелевого сплава ХН62 на 15% без роста себестоимости шихты',
  constraints: [
    'Доступное сырьё: Ni, Cr, Co, Nb, отходы производства',
    'Бюджет на легирующие добавки — не более +8% к текущей себестоимости',
    'Оборудование: вакуумно-индукционная плавка, печи отжига до 1200 °C',
    'Нормативы: ГОСТ 5632-2014 по коррозионной стойкости',
  ],
  summary:
    'Сформировано 3 приоритетные гипотезы. Наиболее перспективная — микролегирование ниобием ' +
    'с двухступенчатым отжигом: прогноз +14–17% жаропрочности при росте себестоимости ~5%. ' +
    'Все гипотезы проверяемы в лабораторных условиях в течение 4–8 недель.',
  hypotheses: [
    {
      id: 'hyp-1',
      title: 'Микролегирование 0.3% Nb с двухступенчатым отжигом (1080 °C → 850 °C)',
      rationale:
        'Введение 0.3% ниобия при контролируемом режиме отжига стимулирует формирование ' +
        'дисперсных карбидов NbC на границах зёрен, что тормозит зернограничное проскальзывание ' +
        'при высоких температурах. Аналогичный эффект подтверждён для сплавов серии Inconel.',
      mechanism:
        'Дисперсные карбиды NbC закрепляют границы зёрен (эффект Зинера), повышая сопротивление ' +
        'ползучести на 12–18% при 900 °C.',
      sources: [
        { id: 's1', title: 'Carbide precipitation in Nb-modified Ni superalloys', kind: 'article', year: 2021, url: 'https://example.org/nbc-superalloys' },
        { id: 's2', title: 'US10858721B2 — Heat-resistant nickel alloy', kind: 'patent', year: 2020, url: 'https://patents.example.org/US10858721B2' },
        { id: 's3', title: 'Внутренний отчёт ЛИ-2024-117: отжиг ХН62', kind: 'report', year: 2024 },
      ],
      novelty: 72,
      feasibility: 84,
      risks: [
        { category: 'technical', description: 'Риск охрупчивания при превышении 0.4% Nb', level: 'medium' },
        { category: 'economic', description: 'Ниобий повышает себестоимость шихты на ~5%', level: 'low' },
      ],
      expectedValue: 'Рост жаропрочности +14–17%, ресурс детали +20% при 900 °C',
      kpiImpact: '+15% жаропрочность',
    },
    {
      id: 'hyp-2',
      title: 'Замена части Co на Ru (0.5%) для стабилизации γ′-фазы',
      rationale:
        'Частичная замена кобальта рутением повышает температуру сольвус γ′-фазы, расширяя ' +
        'рабочий температурный диапазон. Подтверждено данными Materials Project по стабильности фаз.',
      mechanism:
        'Ru замедляет коагуляцию γ′-выделений, сохраняя мелкодисперсную структуру при длительной ' +
        'выдержке под нагрузкой.',
      sources: [
        { id: 's4', title: 'Ru effect on γ′ solvus temperature', kind: 'article', year: 2019, url: 'https://example.org/ru-gamma-prime' },
        { id: 's5', title: 'Materials Project mp-1234: Ni-Co-Ru', kind: 'dataset', year: 2023, url: 'https://materialsproject.org/mp-1234' },
      ],
      novelty: 81,
      feasibility: 58,
      risks: [
        { category: 'economic', description: 'Рутений дорог — рост себестоимости до +7%', level: 'high' },
        { category: 'technical', description: 'Требует точного контроля состава при плавке', level: 'medium' },
      ],
      expectedValue: 'Рост жаропрочности +10–13%, стабильность при 950 °C',
      kpiImpact: '+12% жаропрочность',
    },
    {
      id: 'hyp-3',
      title: 'Оптимизация режима ГИП (горячее изостатическое прессование) для снижения пористости',
      rationale:
        'Снижение остаточной пористости за счёт ГИП при 1160 °C / 150 МПа повышает усталостную ' +
        'долговечность без изменения химического состава — минимальные затраты на сырьё.',
      mechanism:
        'Закрытие микропор устраняет концентраторы напряжений, повышая сопротивление ползучести ' +
        'и усталости.',
      sources: [
        { id: 's6', title: 'HIP processing of cast Ni superalloys', kind: 'article', year: 2022, url: 'https://example.org/hip-processing' },
        { id: 's7', title: 'Внутренний отчёт ЛИ-2023-089: ГИП образцов', kind: 'report', year: 2023 },
      ],
      novelty: 45,
      feasibility: 91,
      risks: [
        { category: 'technical', description: 'Требуется доступ к установке ГИП', level: 'medium' },
        { category: 'economic', description: 'Затраты только на энергопотребление процесса', level: 'low' },
      ],
      expectedValue: 'Рост жаропрочности +6–9%, усталостный ресурс +25%',
      kpiImpact: '+8% жаропрочность',
    },
  ],
}

export const MOCK_HISTORY: HistoryEntry[] = [
  {
    id: 'h1',
    createdAt: '2026-07-03T12:40:00.000Z',
    problem: 'Повысить жаропрочность никелевого сплава ХН62 на 15%',
    reportId: 'rep-2026-0703-01',
    hypothesisCount: 3,
  },
  {
    id: 'h2',
    createdAt: '2026-06-28T09:15:00.000Z',
    problem: 'Снизить себестоимость шихты без потери прочности на растяжение',
    reportId: 'rep-2026-0628-04',
    hypothesisCount: 4,
  },
  {
    id: 'h3',
    createdAt: '2026-06-21T16:02:00.000Z',
    problem: 'Улучшить коррозионную стойкость алюминиевого сплава Д16',
    reportId: 'rep-2026-0621-02',
    hypothesisCount: 5,
  },
  {
    id: 'h4',
    createdAt: '2026-06-14T11:30:00.000Z',
    problem: 'Повысить износостойкость покрытия режущего инструмента',
    reportId: 'rep-2026-0614-07',
    hypothesisCount: 3,
  },
]
