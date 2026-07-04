import * as SwitchPrimitive from '@radix-ui/react-switch'
import { cn } from '@/lib/cn'

interface SwitchProps {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  className?: string
  'aria-label'?: string
}

export function Switch({ checked, onCheckedChange, className, 'aria-label': ariaLabel }: SwitchProps) {
  return (
    <SwitchPrimitive.Root
      checked={checked}
      onCheckedChange={onCheckedChange}
      aria-label={ariaLabel}
      className={cn(
        'relative h-6 w-11 shrink-0 rounded-full border border-transparent bg-[#DDE1E5] shadow-inner outline-none transition-colors duration-200',
        'data-[state=checked]:bg-accent-500',
        'focus-visible:ring-2 focus-visible:ring-accent-500/45 focus-visible:ring-offset-1 focus-visible:ring-offset-bg',
        className,
      )}
    >
      <SwitchPrimitive.Thumb
        className={cn(
          'block h-5 w-5 translate-x-0.5 rounded-full bg-white shadow-soft transition-transform duration-200 will-change-transform',
          'data-[state=checked]:translate-x-[18px]',
        )}
      />
    </SwitchPrimitive.Root>
  )
}
