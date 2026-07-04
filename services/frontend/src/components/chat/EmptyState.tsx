import { LoginPrompt } from '@/components/auth/LoginPrompt'

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
    <div className="mx-auto flex min-h-full w-full max-w-2xl flex-col justify-start px-4 pb-12 pt-[14vh]">
      <div className="animate-fade-up" key={authenticated ? 'hero-auth' : 'hero-guest'}>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
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
        <LoginPrompt
          className="mt-7"
          style={{ animationDelay: '80ms' }}
          title="Войдите, чтобы пользоваться чатом"
          description="Сообщение можно набрать уже сейчас — вместе с ограничениями, весами и файлами. После входа мы автоматически отправим его и откроем чат."
          actionLabel="Войти или зарегистрироваться"
          onLogin={onLogin}
        />
      )}
    </div>
  )
}
