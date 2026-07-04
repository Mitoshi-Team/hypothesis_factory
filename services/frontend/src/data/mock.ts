import type { HypothesisResult, Session } from '@/types'
import { DEFAULT_WEIGHTS } from '@/types'

export const SAMPLE_RESULT: HypothesisResult = {
  title: 'Микролегирование ниобием с двухступенчатым отжигом',
  hypothesis:
    'Введение 0,3% ниобия в сплав ХН62 с двухступенчатым отжигом (1080 °C → 850 °C) ' +
    'сформирует дисперсные карбиды NbC на границах зёрен и повысит жаропрочность за счёт ' +
    'торможения зернограничного проскальзывания при рабочих температурах.',
  expectedEffect:
    'Рост жаропрочности на 14-17% при 900 °C, ресурс детали +20%. Себестоимость шихты +5%.',
  scores: { novelty: 6.0, feasibility: 8.5, effect: 8.0, risk: 4.0 },
  verdict: 'accept',
  risks: [
    'Охрупчивание при превышении 0,4% Nb',
    'Ниобий повышает себестоимость шихты примерно на 5%',
  ],
  suggestions: [
    'Уточнить диапазон температур второй ступени отжига на пробной плавке',
    'Проверить пластичность образцов после длительной выдержки под нагрузкой',
  ],
  evidenceSources: [
    'Carbide precipitation in Nb-modified Ni superalloys (2021)',
    'US10858721B2 — Heat-resistant nickel alloy',
    'Внутренний отчёт ЛИ-2024-117: отжиг ХН62',
  ],
}

const SECOND_RESULT: HypothesisResult = {
  title: 'Стабилизация γ′-фазы частичной заменой кобальта рутением',
  hypothesis:
    'Замена 0,5% кобальта рутением повысит температуру сольвус γ′-фазы и замедлит коагуляцию ' +
    'выделений, сохраняя мелкодисперсную структуру при длительной выдержке под нагрузкой.',
  expectedEffect: 'Рост жаропрочности на 10-13%, стабильность структуры при 950 °C.',
  scores: { novelty: 8.0, feasibility: 5.5, effect: 7.5, risk: 6.0 },
  verdict: 'accept',
  risks: [
    'Рутений дорог — рост себестоимости до 7%',
    'Требуется точный контроль состава при вакуумно-индукционной плавке',
  ],
  suggestions: ['Сравнить с гипотезой по ниобию по критерию себестоимости'],
  evidenceSources: [
    'Ru effect on γ′ solvus temperature (2019)',
    'Materials Project mp-1234: Ni-Co-Ru',
  ],
}

const THIRD_RESULT: HypothesisResult = {
  title: 'Оптимизация режима ГИП для снижения остаточной пористости',
  hypothesis:
    'Горячее изостатическое прессование при 1160 °C и 150 МПа закроет микропоры без изменения ' +
    'химического состава, устранит концентраторы напряжений и повысит усталостную долговечность.',
  expectedEffect: 'Рост жаропрочности на 6-9%, усталостный ресурс +25% без затрат на сырьё.',
  scores: { novelty: 4.5, feasibility: 9.0, effect: 6.0, risk: 3.0 },
  verdict: 'accept',
  risks: ['Нужен доступ к установке ГИП'],
  suggestions: ['Заложить контрольную партию образцов без ГИП для сравнения'],
  evidenceSources: [
    'HIP processing of cast Ni superalloys (2022)',
    'Внутренний отчёт ЛИ-2023-089: ГИП образцов',
  ],
}

export const MOCK_SESSIONS: Session[] = [
  {
    id: 'sess_1',
    title: 'Жаропрочность никелевого сплава ХН62',
    createdAt: '2026-07-03T12:40:00.000Z',
    constraints:
      'Бюджет на легирующие добавки — не более +8% к себестоимости. Оборудование: вакуумно-индукционная плавка, печи отжига до 1200 °C. Норматив: ГОСТ 5632-2014.',
    weights: DEFAULT_WEIGHTS,
    messages: [
      {
        id: 'sess_1-m0',
        role: 'user',
        content:
          'Повысить жаропрочность никелевого сплава ХН62 на 15% без роста себестоимости шихты',
        files: ['ХН62_состав.xlsx', 'испытания_900C.csv'],
      },
      { id: 'sess_1-m1', role: 'assistant', status: 'done', iteration: 0, result: SAMPLE_RESULT },
    ],
  },
  {
    id: 'sess_2',
    title: 'Снижение себестоимости шихты',
    createdAt: '2026-06-28T09:15:00.000Z',
    constraints: 'Сохранить прочность на растяжение не ниже текущего уровня.',
    weights: { novelty: 1.0, feasibility: 2.0, effect: 1.5, risk: 1.0 },
    messages: [
      {
        id: 'sess_2-m0',
        role: 'user',
        content: 'Снизить себестоимость шихты без потери прочности на растяжение',
        files: [],
      },
      { id: 'sess_2-m1', role: 'assistant', status: 'done', iteration: 0, result: SECOND_RESULT },
    ],
  },
  {
    id: 'sess_3',
    title: 'Коррозионная стойкость сплава Д16',
    createdAt: '2026-06-21T16:02:00.000Z',
    constraints: 'Морская среда, эксплуатация до 5 лет.',
    weights: DEFAULT_WEIGHTS,
    messages: [
      {
        id: 'sess_3-m0',
        role: 'user',
        content: 'Улучшить коррозионную стойкость алюминиевого сплава Д16 в морской среде',
        files: [],
      },
      { id: 'sess_3-m1', role: 'assistant', status: 'done', iteration: 0, result: THIRD_RESULT },
    ],
  },
]
