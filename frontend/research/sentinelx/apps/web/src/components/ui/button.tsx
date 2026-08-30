import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0B827A]/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#09090B] disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-[#0B827A] text-white shadow-[0_0_20px_rgba(11,130,122,0.15)] hover:bg-[#0A6D65]",
        destructive:
          "bg-red-500/20 text-red-400 border border-red-500/20 hover:bg-red-500/30",
        outline:
          "border border-[rgba(255,255,255,0.08)] bg-transparent text-[#FAFAFA] hover:bg-[rgba(255,255,255,0.04)] hover:border-[rgba(255,255,255,0.12)]",
        secondary:
          "bg-[#1A1A1F] text-[#FAFAFA] border border-[rgba(255,255,255,0.06)] hover:bg-[#222227] hover:border-[rgba(255,255,255,0.1)]",
        ghost:
          "text-[#A0A0AB] hover:text-[#FAFAFA] hover:bg-[rgba(255,255,255,0.04)]",
        link: "text-[#0B827A] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-lg px-6 text-base",
        xl: "h-12 rounded-lg px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  },
)
Button.displayName = "Button"

export { Button, buttonVariants }