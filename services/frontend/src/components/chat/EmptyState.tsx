import { FlaskConical, LogIn } from 'lucide-react'

const EXAMPLES = [
  'Повысить жаропрочность никелевого сплава ХН62 на 15% без роста себестоимости шихты',
  'Снизить себестоимость шихты без потери прочности на растяжение',
  'Улучшить коррозионную стойкость алюминиевого сплава Д16 в морской среде',
  'Повысить износостойкость покрытия режущего инструмента при 800 °C',
]

interface Props {
  authenticated: boolean
  onSelect: (text: string) => void
  onLogin: () => void
}

export function EmptyState({ authenticated, onSelect, onLogin }: Props) {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-2xl flex-col justify-center px-4 py-12">
      <div className="animate-fade-up" key={authenticated ? 'hero-auth' : 'hero-guest'}>
        <span className="grid h-11 w-11 place-items-center rounded-xl bg-accent-50 text-accent-600">
          <FlaskConical className="h-6 w-6" strokeWidth={1.8} />
        </span>
        <h1 className="mt-5 text-2xl font-semibold tracking-tight text-ink">
          С какой задачей поработаем?
        </h1>
        <p className="mt-2 max-w-lg text-[15px] leading-relaxed text-ink-soft">
          Опишите технологическую проблему. Я разберу базу знаний и предложу гипотезу с
          обоснованием, ожидаемым эффектом, оценкой по критериям и рисками.
        </p>
      </div>

      {authenticated ? (
        <div
          key="examples"
          className="mt-7 flex flex-col gap-2 animate-fade-up"
          style={{ animationDelay: '80ms' }}
        >
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => onSelect(ex)}
              className="rounded-xl border border-line bg-card px-4 py-3 text-left text-[14px] text-ink-soft transition-colors hover:border-accent-200 hover:bg-accent-50 hover:text-ink"
            >
              {ex}
            </button>
          ))}
        </div>
      ) : (
        <div
          key="login-cta"
          className="mt-7 animate-fade-up rounded-2xl border border-line bg-card px-5 py-5"
          style={{ animationDelay: '80ms' }}
        >
          <p className="text-[15px] font-medium text-ink">
            Войдите, чтобы пользоваться чатом
          </p>
          <p className="mt-1.5 max-w-md text-[13.5px] leading-relaxed text-ink-soft">
            Сообщение можно набрать уже сейчас — вместе с ограничениями, весами и файлами. После
            входа мы автоматически отправим его и откроем чат.
          </p>
          <button
            type="button"
            onClick={onLogin}
            className="mt-3.5 inline-flex items-center gap-2 rounded-xl bg-accent-500 px-4 py-2.5 text-[13.5px] font-medium text-white shadow-soft transition-all duration-200 ease-out hover:bg-accent-600 active:scale-[0.97]"
          >
            <LogIn className="h-4 w-4" strokeWidth={2.2} />
            Войти или зарегистрироваться
          </button>
        </div>
      )}
    </div>
  )
}
