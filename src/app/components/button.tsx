import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../utils/cn';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-[#3EB6B1] text-white hover:bg-[#36a49f] shadow-md hover:shadow-lg',
      secondary: 'bg-[#9C8CFF] text-white hover:bg-[#8b7ae6] shadow-md hover:shadow-lg',
      accent: 'bg-[#FFB6A3] text-[#2B2B2B] hover:bg-[#ffa18b] shadow-md hover:shadow-lg',
      outline: 'border-2 border-[#3EB6B1] text-[#3EB6B1] hover:bg-[#3EB6B1] hover:text-white',
      ghost: 'text-[#2B2B2B] hover:bg-gray-100',
    };
    
    const sizes = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-3',
      lg: 'px-8 py-4 text-lg',
    };
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
