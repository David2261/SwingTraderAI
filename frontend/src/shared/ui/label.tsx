import { forwardRef, type LabelHTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

const labelVariants = cva(
  'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70'
)

interface LabelProps
  extends LabelHTMLAttributes<HTMLLabelElement>,
    VariantProps<typeof labelVariants> {}

export const Label = forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={labelVariants({ className })}
        {...props}
      />
    )
  }
)

Label.displayName = 'Label'
