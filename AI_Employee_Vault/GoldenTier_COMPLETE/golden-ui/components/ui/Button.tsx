'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      icon,
      iconPosition = 'left',
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'rounded-lg',
    ];

    const variantClasses = {
      primary: [
        'bg-primary-500 text-black hover:bg-primary-600',
        'focus:ring-primary-500 shadow-md hover:shadow-lg',
        'active:scale-[0.98]',
      ],
      secondary: [
        'bg-secondary-100 text-secondary-900 hover:bg-secondary-200',
        'dark:bg-secondary-800 dark:text-secondary-100 dark:hover:bg-secondary-700',
        'focus:ring-secondary-500',
      ],
      outline: [
        'border-2 border-primary-500 text-primary-600 hover:bg-primary-50',
        'dark:border-primary-400 dark:text-primary-400 dark:hover:bg-primary-950',
        'focus:ring-primary-500',
      ],
      ghost: [
        'text-secondary-600 hover:bg-secondary-100 hover:text-secondary-900',
        'dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-100',
        'focus:ring-secondary-500',
      ],
      danger: [
        'bg-danger-500 text-white hover:bg-danger-600',
        'focus:ring-danger-500 shadow-md hover:shadow-lg',
        'active:scale-[0.98]',
      ],
      success: [
        'bg-success-500 text-white hover:bg-success-600',
        'focus:ring-success-500 shadow-md hover:shadow-lg',
        'active:scale-[0.98]',
      ],
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-sm gap-2',
      lg: 'px-6 py-3 text-base gap-2',
      xl: 'px-8 py-4 text-lg gap-3',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          loading && 'cursor-wait',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : (
          icon && iconPosition === 'left' && icon
        )}
        {children}
        {!loading && icon && iconPosition === 'right' && icon}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, type ButtonProps };