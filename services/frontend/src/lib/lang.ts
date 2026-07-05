// Lightweight i18n core (framework-agnostic) shared by React components and the
// plain-function formatters in format.ts / api.ts. React state lives in i18n.tsx;
// this module owns the current language, persistence, and the dictionaries.

export type Lang = 'ru' | 'en' | 'zh'

export const LANGS: Lang[] = ['ru', 'en', 'zh']

/** Display metadata for the language switcher (native names). */
export const LANG_META: Record<Lang, { native: string; label: string }> = {
  ru: { native: 'Русский', label: 'Russian' },
  en: { native: 'English', label: 'English' },
  zh: { native: '中文', label: 'Chinese' },
}

const STORAGE_KEY = 'hf-lang'

function detect(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'ru' || saved === 'en' || saved === 'zh') return saved
  } catch {
    /* localStorage unavailable */
  }
  return 'ru'
}

let current: Lang = detect()

type Listener = (lang: Lang) => void
const listeners = new Set<Listener>()

export function getLang(): Lang {
  return current
}

export function setLang(lang: Lang): void {
  if (lang === current) return
  current = lang
  try {
    localStorage.setItem(STORAGE_KEY, lang)
    document.documentElement.lang = lang
  } catch {
    /* ignore */
  }
  listeners.forEach((l) => l(lang))
}

export function subscribeLang(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

// ---------------------------------------------------------------------------
// Dictionaries

type Dict = Record<string, string>

const ru: Dict = {
  // sidebar
  'sidebar.newChat': 'Новый чат',
  'sidebar.prevChats': 'Предыдущие чаты',
  'sidebar.historyUnavailable': 'История недоступна',
  'sidebar.historyUnavailableDesc':
    'Для того чтобы иметь доступ к истории, необходимо войти или зарегистрироваться.',
  'sidebar.loadingHistory': 'Загружаем историю…',
  'sidebar.empty': 'Пока пусто — начните первый чат, и он появится здесь.',
  'sidebar.retry': 'Повторить',
  'sidebar.auth': 'Авторизация',
  'sidebar.deleteChat': 'Удалить чат',
  'sidebar.hideMenu': 'Скрыть меню',
  'sidebar.showMenu': 'Показать меню',

  // profile menu
  'profile.open': 'Открыть меню профиля',
  'profile.demo': 'Демо-режим',
  'profile.account': 'Аккаунт',
  'profile.language': 'Язык',
  'profile.logout': 'Выйти',
  'profile.logoutTitle': 'Выйти из аккаунта?',
  'profile.logoutDesc': 'Историю можно будет открыть снова после входа.',
  'profile.cancel': 'Отмена',

  // auth
  'auth.regionLogin': 'Авторизация',
  'auth.regionRegister': 'Регистрация',
  'auth.perk1': 'История сессий всегда под рукой',
  'auth.perk2': 'Итеративная работа над гипотезой',
  'auth.perk3': 'Оценка по критериям и рискам',
  'auth.brandTitle': 'Гипотезы, подкреплённые данными',
  'auth.brandDesc':
    'Опишите технологическую задачу — получите гипотезу с обоснованием, ожидаемым эффектом и оценкой рисков.',
  'auth.backToChat': 'К чату',
  'auth.createAccount': 'Создать аккаунт',
  'auth.welcomeBack': 'С возвращением',
  'auth.registerHint': 'Придумайте логин и пароль, чтобы начать работу.',
  'auth.loginHint': 'Войдите, чтобы работать с чатом и историей сессий.',
  'auth.loginField': 'Логин',
  'auth.passwordField': 'Пароль',
  'auth.repeatPassword': 'Повторите пароль',
  'auth.showPassword': 'Показать пароль',
  'auth.hidePassword': 'Скрыть пароль',
  'auth.registering': 'Регистрируем…',
  'auth.loggingIn': 'Входим…',
  'auth.signUp': 'Зарегистрироваться',
  'auth.signIn': 'Войти',
  'auth.haveAccount': 'Уже есть аккаунт? ',
  'auth.noAccount': 'Нет аккаунта? ',
  'auth.demoButton': 'Посмотреть демо без регистрации',
  'auth.forgot': 'Забыли логин или пароль? Обратитесь к администратору.',
  'auth.errEnterCreds': 'Введите логин и пароль.',
  'auth.errPwMismatch': 'Пароли не совпадают.',
  'auth.errBadCreds': 'Неверный логин или пароль.',
  'auth.errTaken': 'Такой логин уже занят.',

  // composer
  'composer.placeholder': 'Опишите технологическую проблему…',
  'composer.problemAria': 'Технологическая проблема',
  'composer.contextAria': 'Контекст: ограничения, веса и файлы',
  'composer.context': 'Контекст',
  'composer.send': 'Отправить',

  // context tray
  'context.constraints': 'Ограничения',
  'context.constraintsPlaceholder': 'Бюджет, оборудование, нормативы, доступное сырьё…',
  'context.weights': 'Веса критериев',
  'context.materials': 'Материалы и данные',
  'context.weightAria': 'Вес: {name}',
  'dropzone.hint': 'Excel, CSV, JSON, PDF, Word · до 20 МБ',
  'dropzone.prompt': 'Перетащите файлы или нажмите для выбора',
  'dropzone.remove': 'Удалить {name}',

  // criteria + verdict
  'criteria.novelty': 'Новизна',
  'criteria.feasibility': 'Реализуемость',
  'criteria.effect': 'Эффект',
  'criteria.risk': 'Риск',
  'verdict.accept': 'Принята',
  'verdict.reject': 'Отклонена',

  // empty state
  'empty.title': 'С какой задачей поработаем?',
  'empty.desc':
    'Опишите технологическую проблему. Я разберу базу знаний и предложу гипотезу с обоснованием, ожидаемым эффектом, оценкой по критериям и рисками.',
  'empty.loginTitle': 'Войдите, чтобы пользоваться чатом',
  'empty.loginDesc':
    'Сообщение можно набрать уже сейчас — вместе с ограничениями, весами и файлами. После входа мы автоматически отправим его и откроем чат.',
  'empty.loginAction': 'Войти или зарегистрироваться',

  // hypothesis result
  'result.expectedEffect': 'Ожидаемый эффект',
  'result.risks': 'Риски',
  'result.nextChecks': 'Что проверить дальше',
  'result.sources': 'Источники',
  'result.hypothesisLabel': 'Гипотеза',
  'doc.appTitle': 'Фабрика гипотез',
  'doc.reportSubtitle': 'Отчёт по гипотезе',

  // thinking trace
  'thinking.0': 'Извлекаю сущности и связи',
  'thinking.1': 'Ищу пробелы в знаниях',
  'thinking.2': 'Формирую гипотезу по аналогиям',
  'thinking.3': 'Оцениваю новизну и риски',

  // message actions
  'actions.copied': 'Скопировано',
  'actions.copy': 'Копировать',
  'actions.download': 'Скачать',
  'actions.viewGraph': 'Посмотреть граф',

  // knowledge graph
  'graph.title': 'Граф знаний',
  'graph.subtitle': 'Сущности и связи из базы знаний',
  'graph.tab.graph': 'Граф',
  'graph.tab.chains': 'Цепочки',
  'graph.loading': 'Загружаем граф…',
  'graph.error': 'Не удалось загрузить граф.',
  'graph.retry': 'Повторить',
  'graph.empty': 'Для этого результата граф пуст.',
  'graph.close': 'Закрыть',
  'graph.showAll': 'Показать все сущности',
  'graph.showAllHint': 'Ядро · {core} из {total}',
  'graph.search': 'Поиск сущности…',
  'graph.types': 'Типы',
  'graph.stats': '{nodes} сущностей · {edges} связей',
  'graph.score': 'Уверенность',
  'graph.sources': 'Источники',
  'graph.noSources': 'Нет привязанных источников.',
  'graph.selectHint': 'Выберите узел, чтобы увидеть детали и источники.',
  'graph.chainsTitle': 'Цепочки рассуждений',
  'graph.chainsEmpty': 'Цепочки не построены.',
  'graph.chainNodes': '{n} узлов',
  'graph.showOnGraph': 'Показать на графе',
  'graph.confidence': 'Достоверность',
  'graph.evidence': 'Обоснование',

  // node types
  'graph.node.Material': 'Материал',
  'graph.node.Process': 'Процесс',
  'graph.node.Property': 'Свойство',
  'graph.node.Parameter': 'Параметр',

  // edge relations
  'graph.rel.contains': 'содержит',
  'graph.rel.influences': 'влияет на',
  'graph.rel.produces': 'производит',
  'graph.rel.requires': 'требует',
  'graph.rel.cites': 'ссылается на',
  'graph.rel.part_of': 'часть',
  'graph.rel.similar_to': 'похоже на',

  // save modal
  'save.title': 'Скачать гипотезу',
  'save.chooseFormat': 'Выберите формат',
  'save.close': 'Закрыть',
  'save.pdfHint': 'Свёрстанный документ для печати',
  'save.docxHint': 'Редактируемый документ Word',

  // assistant message
  'assistant.failedTitle': 'Не удалось получить ответ',
  'assistant.failedDesc': 'Попробуйте отправить сообщение ещё раз.',

  // chat thread
  'thread.loading': 'Загружаем историю чата…',

  // common / app
  'common.signIn': 'Войти',
  'common.loading': 'Загрузка',
  'app.hideError': 'Скрыть ошибку',

  // relative dates
  'date.today': 'сегодня',
  'date.yesterday': 'вчера',
  'date.daysAgo': '{n} дн назад',

  // api errors
  'err.VALIDATION_ERROR': 'Проверьте правильность заполненных данных.',
  'err.UNAUTHORIZED': 'Сессия истекла. Войдите заново.',
  'err.FORBIDDEN': 'Недостаточно прав для этого действия.',
  'err.NOT_FOUND': 'Запрошенные данные не найдены.',
  'err.INTERNAL_SERVER_ERROR': 'На сервере произошла ошибка. Попробуйте ещё раз.',
  'err.NETWORK_ERROR': 'Не удалось связаться с сервером. Проверьте подключение.',
  'err.TIMEOUT': 'Сервер отвечает слишком долго. Попробуйте позже.',
  'err.PIPELINE_FAILED': 'Обработка запроса завершилась с ошибкой. Попробуйте переформулировать.',
  'err.UNKNOWN': 'Что-то пошло не так. Попробуйте ещё раз.',
}

const en: Dict = {
  'sidebar.newChat': 'New chat',
  'sidebar.prevChats': 'Previous chats',
  'sidebar.historyUnavailable': 'History unavailable',
  'sidebar.historyUnavailableDesc': 'Sign in or create an account to access your history.',
  'sidebar.loadingHistory': 'Loading history…',
  'sidebar.empty': "It's empty for now — start your first chat and it will appear here.",
  'sidebar.retry': 'Retry',
  'sidebar.auth': 'Sign in',
  'sidebar.deleteChat': 'Delete chat',
  'sidebar.hideMenu': 'Hide menu',
  'sidebar.showMenu': 'Show menu',

  'profile.open': 'Open profile menu',
  'profile.demo': 'Demo mode',
  'profile.account': 'Account',
  'profile.language': 'Language',
  'profile.logout': 'Log out',
  'profile.logoutTitle': 'Log out of your account?',
  'profile.logoutDesc': 'You can reopen your history after signing back in.',
  'profile.cancel': 'Cancel',

  'auth.regionLogin': 'Sign in',
  'auth.regionRegister': 'Sign up',
  'auth.perk1': 'Session history always at hand',
  'auth.perk2': 'Iterate on your hypothesis',
  'auth.perk3': 'Scoring by criteria and risks',
  'auth.brandTitle': 'Hypotheses backed by data',
  'auth.brandDesc':
    'Describe a technical problem — get a hypothesis with rationale, expected effect and a risk assessment.',
  'auth.backToChat': 'To chat',
  'auth.createAccount': 'Create account',
  'auth.welcomeBack': 'Welcome back',
  'auth.registerHint': 'Pick a username and password to get started.',
  'auth.loginHint': 'Sign in to work with the chat and your session history.',
  'auth.loginField': 'Username',
  'auth.passwordField': 'Password',
  'auth.repeatPassword': 'Repeat password',
  'auth.showPassword': 'Show password',
  'auth.hidePassword': 'Hide password',
  'auth.registering': 'Signing up…',
  'auth.loggingIn': 'Signing in…',
  'auth.signUp': 'Sign up',
  'auth.signIn': 'Sign in',
  'auth.haveAccount': 'Already have an account? ',
  'auth.noAccount': "Don't have an account? ",
  'auth.demoButton': 'Explore the demo without signing up',
  'auth.forgot': 'Forgot your username or password? Contact your administrator.',
  'auth.errEnterCreds': 'Enter a username and password.',
  'auth.errPwMismatch': 'Passwords do not match.',
  'auth.errBadCreds': 'Wrong username or password.',
  'auth.errTaken': 'That username is already taken.',

  'composer.placeholder': 'Describe a technical problem…',
  'composer.problemAria': 'Technical problem',
  'composer.contextAria': 'Context: constraints, weights and files',
  'composer.context': 'Context',
  'composer.send': 'Send',

  'context.constraints': 'Constraints',
  'context.constraintsPlaceholder': 'Budget, equipment, standards, available materials…',
  'context.weights': 'Criteria weights',
  'context.materials': 'Materials and data',
  'context.weightAria': 'Weight: {name}',
  'dropzone.hint': 'Excel, CSV, JSON, PDF, Word · up to 20 MB',
  'dropzone.prompt': 'Drag files here or click to choose',
  'dropzone.remove': 'Remove {name}',

  'criteria.novelty': 'Novelty',
  'criteria.feasibility': 'Feasibility',
  'criteria.effect': 'Effect',
  'criteria.risk': 'Risk',
  'verdict.accept': 'Accepted',
  'verdict.reject': 'Rejected',

  'empty.title': 'What shall we work on?',
  'empty.desc':
    'Describe a technical problem. I will study the knowledge base and propose a hypothesis with rationale, expected effect, criteria scoring and risks.',
  'empty.loginTitle': 'Sign in to use the chat',
  'empty.loginDesc':
    'You can type your message right now — together with constraints, weights and files. After signing in we will send it automatically and open the chat.',
  'empty.loginAction': 'Sign in or create an account',

  'result.expectedEffect': 'Expected effect',
  'result.risks': 'Risks',
  'result.nextChecks': 'What to check next',
  'result.sources': 'Sources',
  'result.hypothesisLabel': 'Hypothesis',
  'doc.appTitle': 'Hypothesis Factory',
  'doc.reportSubtitle': 'Hypothesis report',

  'thinking.0': 'Extracting entities and relations',
  'thinking.1': 'Looking for knowledge gaps',
  'thinking.2': 'Forming a hypothesis by analogy',
  'thinking.3': 'Assessing novelty and risks',

  'actions.copied': 'Copied',
  'actions.copy': 'Copy',
  'actions.download': 'Download',
  'actions.viewGraph': 'View graph',

  'graph.title': 'Knowledge graph',
  'graph.subtitle': 'Entities and relations from the knowledge base',
  'graph.tab.graph': 'Graph',
  'graph.tab.chains': 'Chains',
  'graph.loading': 'Loading graph…',
  'graph.error': 'Could not load the graph.',
  'graph.retry': 'Retry',
  'graph.empty': 'The graph is empty for this result.',
  'graph.close': 'Close',
  'graph.showAll': 'Show all entities',
  'graph.showAllHint': 'Core · {core} of {total}',
  'graph.search': 'Search entity…',
  'graph.types': 'Types',
  'graph.stats': '{nodes} entities · {edges} relations',
  'graph.score': 'Confidence',
  'graph.sources': 'Sources',
  'graph.noSources': 'No linked sources.',
  'graph.selectHint': 'Select a node to see details and sources.',
  'graph.chainsTitle': 'Reasoning chains',
  'graph.chainsEmpty': 'No chains were built.',
  'graph.chainNodes': '{n} nodes',
  'graph.showOnGraph': 'Show on graph',
  'graph.confidence': 'Confidence',
  'graph.evidence': 'Evidence',

  'graph.node.Material': 'Material',
  'graph.node.Process': 'Process',
  'graph.node.Property': 'Property',
  'graph.node.Parameter': 'Parameter',

  'graph.rel.contains': 'contains',
  'graph.rel.influences': 'influences',
  'graph.rel.produces': 'produces',
  'graph.rel.requires': 'requires',
  'graph.rel.cites': 'cites',
  'graph.rel.part_of': 'part of',
  'graph.rel.similar_to': 'similar to',

  'save.title': 'Download hypothesis',
  'save.chooseFormat': 'Choose a format',
  'save.close': 'Close',
  'save.pdfHint': 'Laid-out document for printing',
  'save.docxHint': 'Editable Word document',

  'assistant.failedTitle': 'Could not get a response',
  'assistant.failedDesc': 'Try sending the message again.',

  'thread.loading': 'Loading chat history…',

  'common.signIn': 'Sign in',
  'common.loading': 'Loading',
  'app.hideError': 'Dismiss error',

  'date.today': 'today',
  'date.yesterday': 'yesterday',
  'date.daysAgo': '{n} days ago',

  'err.VALIDATION_ERROR': 'Please check the entered data.',
  'err.UNAUTHORIZED': 'Session expired. Please sign in again.',
  'err.FORBIDDEN': 'You do not have permission for this action.',
  'err.NOT_FOUND': 'The requested data was not found.',
  'err.INTERNAL_SERVER_ERROR': 'A server error occurred. Please try again.',
  'err.NETWORK_ERROR': 'Could not reach the server. Check your connection.',
  'err.TIMEOUT': 'The server is taking too long. Please try later.',
  'err.PIPELINE_FAILED': 'Processing failed. Try rephrasing your request.',
  'err.UNKNOWN': 'Something went wrong. Please try again.',
}

const zh: Dict = {
  'sidebar.newChat': '新对话',
  'sidebar.prevChats': '历史对话',
  'sidebar.historyUnavailable': '无法查看历史',
  'sidebar.historyUnavailableDesc': '登录或注册后即可访问历史记录。',
  'sidebar.loadingHistory': '正在加载历史…',
  'sidebar.empty': '暂时为空——开始第一个对话，它会显示在这里。',
  'sidebar.retry': '重试',
  'sidebar.auth': '登录',
  'sidebar.deleteChat': '删除对话',
  'sidebar.hideMenu': '隐藏菜单',
  'sidebar.showMenu': '显示菜单',

  'profile.open': '打开个人菜单',
  'profile.demo': '演示模式',
  'profile.account': '账户',
  'profile.language': '语言',
  'profile.logout': '退出登录',
  'profile.logoutTitle': '退出账户？',
  'profile.logoutDesc': '重新登录后仍可查看历史记录。',
  'profile.cancel': '取消',

  'auth.regionLogin': '登录',
  'auth.regionRegister': '注册',
  'auth.perk1': '会话历史随时可查',
  'auth.perk2': '对假设进行迭代',
  'auth.perk3': '按标准与风险评分',
  'auth.brandTitle': '以数据为支撑的假设',
  'auth.brandDesc': '描述一个技术问题——获得带有论证、预期效果和风险评估的假设。',
  'auth.backToChat': '返回对话',
  'auth.createAccount': '创建账户',
  'auth.welcomeBack': '欢迎回来',
  'auth.registerHint': '设置用户名和密码即可开始使用。',
  'auth.loginHint': '登录以使用对话和会话历史。',
  'auth.loginField': '用户名',
  'auth.passwordField': '密码',
  'auth.repeatPassword': '再次输入密码',
  'auth.showPassword': '显示密码',
  'auth.hidePassword': '隐藏密码',
  'auth.registering': '正在注册…',
  'auth.loggingIn': '正在登录…',
  'auth.signUp': '注册',
  'auth.signIn': '登录',
  'auth.haveAccount': '已有账户？ ',
  'auth.noAccount': '还没有账户？ ',
  'auth.demoButton': '无需注册，查看演示',
  'auth.forgot': '忘记用户名或密码？请联系管理员。',
  'auth.errEnterCreds': '请输入用户名和密码。',
  'auth.errPwMismatch': '两次密码不一致。',
  'auth.errBadCreds': '用户名或密码错误。',
  'auth.errTaken': '该用户名已被占用。',

  'composer.placeholder': '描述一个技术问题…',
  'composer.problemAria': '技术问题',
  'composer.contextAria': '上下文：约束、权重和文件',
  'composer.context': '上下文',
  'composer.send': '发送',

  'context.constraints': '约束条件',
  'context.constraintsPlaceholder': '预算、设备、规范、可用原料…',
  'context.weights': '标准权重',
  'context.materials': '材料与数据',
  'context.weightAria': '权重：{name}',
  'dropzone.hint': 'Excel、CSV、JSON、PDF、Word · 最大 20 MB',
  'dropzone.prompt': '拖入文件或点击选择',
  'dropzone.remove': '删除 {name}',

  'criteria.novelty': '新颖性',
  'criteria.feasibility': '可行性',
  'criteria.effect': '效果',
  'criteria.risk': '风险',
  'verdict.accept': '已采纳',
  'verdict.reject': '已否决',

  'empty.title': '我们来解决什么问题？',
  'empty.desc': '描述一个技术问题。我会分析知识库，并提出带有论证、预期效果、标准评分和风险的假设。',
  'empty.loginTitle': '登录后即可使用对话',
  'empty.loginDesc':
    '现在就可以输入消息——连同约束、权重和文件。登录后我们会自动发送并打开对话。',
  'empty.loginAction': '登录或注册',

  'result.expectedEffect': '预期效果',
  'result.risks': '风险',
  'result.nextChecks': '下一步验证',
  'result.sources': '来源',
  'result.hypothesisLabel': '假设',
  'doc.appTitle': '假设工厂',
  'doc.reportSubtitle': '假设报告',

  'thinking.0': '提取实体与关系',
  'thinking.1': '寻找知识空白',
  'thinking.2': '通过类比形成假设',
  'thinking.3': '评估新颖性与风险',

  'actions.copied': '已复制',
  'actions.copy': '复制',
  'actions.download': '下载',
  'actions.viewGraph': '查看图谱',

  'graph.title': '知识图谱',
  'graph.subtitle': '来自知识库的实体与关系',
  'graph.tab.graph': '图谱',
  'graph.tab.chains': '推理链',
  'graph.loading': '正在加载图谱…',
  'graph.error': '无法加载图谱。',
  'graph.retry': '重试',
  'graph.empty': '该结果的图谱为空。',
  'graph.close': '关闭',
  'graph.showAll': '显示全部实体',
  'graph.showAllHint': '核心 · {total} 中的 {core}',
  'graph.search': '搜索实体…',
  'graph.types': '类型',
  'graph.stats': '{nodes} 个实体 · {edges} 条关系',
  'graph.score': '置信度',
  'graph.sources': '来源',
  'graph.noSources': '没有关联来源。',
  'graph.selectHint': '选择一个节点以查看详情与来源。',
  'graph.chainsTitle': '推理链',
  'graph.chainsEmpty': '未构建推理链。',
  'graph.chainNodes': '{n} 个节点',
  'graph.showOnGraph': '在图谱中显示',
  'graph.confidence': '置信度',
  'graph.evidence': '依据',

  'graph.node.Material': '材料',
  'graph.node.Process': '工艺',
  'graph.node.Property': '性能',
  'graph.node.Parameter': '参数',

  'graph.rel.contains': '包含',
  'graph.rel.influences': '影响',
  'graph.rel.produces': '产生',
  'graph.rel.requires': '需要',
  'graph.rel.cites': '引用',
  'graph.rel.part_of': '属于',
  'graph.rel.similar_to': '相似于',

  'save.title': '下载假设',
  'save.chooseFormat': '选择格式',
  'save.close': '关闭',
  'save.pdfHint': '排版好的打印文档',
  'save.docxHint': '可编辑的 Word 文档',

  'assistant.failedTitle': '未能获取回复',
  'assistant.failedDesc': '请重新发送消息。',

  'thread.loading': '正在加载对话历史…',

  'common.signIn': '登录',
  'common.loading': '加载中',
  'app.hideError': '关闭错误',

  'date.today': '今天',
  'date.yesterday': '昨天',
  'date.daysAgo': '{n} 天前',

  'err.VALIDATION_ERROR': '请检查填写的数据。',
  'err.UNAUTHORIZED': '会话已过期，请重新登录。',
  'err.FORBIDDEN': '您没有执行此操作的权限。',
  'err.NOT_FOUND': '未找到请求的数据。',
  'err.INTERNAL_SERVER_ERROR': '服务器发生错误，请重试。',
  'err.NETWORK_ERROR': '无法连接服务器，请检查网络。',
  'err.TIMEOUT': '服务器响应过慢，请稍后再试。',
  'err.PIPELINE_FAILED': '处理失败，请尝试重新表述。',
  'err.UNKNOWN': '出了点问题，请重试。',
}

const DICTS: Record<Lang, Dict> = { ru, en, zh }

/** Example prompts shown on the empty state, per language. */
export const EXAMPLES: Record<Lang, string[]> = {
  ru: [
    'Повысить жаропрочность никелевого сплава ХН62 на 15% без роста себестоимости шихты',
    'Снизить себестоимость шихты без потери прочности на растяжение',
    'Улучшить коррозионную стойкость алюминиевого сплава Д16 в морской среде',
    'Повысить износостойкость покрытия режущего инструмента при 800 °C',
  ],
  en: [
    'Raise the heat resistance of nickel alloy KhN62 by 15% without increasing charge cost',
    'Reduce charge cost without losing tensile strength',
    'Improve the corrosion resistance of aluminium alloy D16 in a marine environment',
    'Increase the wear resistance of a cutting-tool coating at 800 °C',
  ],
  zh: [
    '在不增加炉料成本的前提下，将镍合金 ХН62 的耐热性提高 15%',
    '在不损失抗拉强度的前提下降低炉料成本',
    '提高铝合金 Д16 在海洋环境中的耐腐蚀性',
    '提高切削刀具涂层在 800 °C 下的耐磨性',
  ],
}

/** Locale tag for Date / number formatting. */
export const LOCALE_TAG: Record<Lang, string> = {
  ru: 'ru-RU',
  en: 'en-US',
  zh: 'zh-CN',
}

/** Translate a key for a specific language, interpolating {name}-style params. */
export function translate(lang: Lang, key: string, params?: Record<string, string | number>): string {
  const raw = DICTS[lang][key] ?? DICTS.ru[key] ?? key
  if (!params) return raw
  return raw.replace(/\{(\w+)\}/g, (_, p) => String(params[p] ?? `{${p}}`))
}

/** Translate using the current language. */
export function t(key: string, params?: Record<string, string | number>): string {
  return translate(current, key, params)
}
