import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-mantis-500 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-mantis-600 text-white shadow-sm shadow-mantis-200 hover:bg-mantis-700",
        secondary: "border-transparent bg-gray-100 text-gray-900 hover:bg-gray-200",
        destructive: "border-transparent bg-red-500 text-white shadow-sm shadow-red-200 hover:bg-red-600",
        outline: "text-gray-950 hover:bg-gray-50",
        success: "border-transparent bg-emerald-500 text-white shadow-sm shadow-emerald-200 hover:bg-emerald-600",
        warning: "border-transparent bg-amber-500 text-white shadow-sm shadow-amber-200 hover:bg-amber-600",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
