import { cn } from '../../lib/utils';

export function Input({ className, type = 'text', ...props }) {
  return (
    <input
      type={type}
      className={cn(
        'w-full px-4 py-3 rounded-lg',
        'bg-dark-800 border border-dark-600',
        'text-white placeholder:text-dark-400',
        'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      {...props}
    />
  );
}

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={cn(
        'w-full px-4 py-3 rounded-lg resize-none',
        'bg-dark-800 border border-dark-600',
        'text-white placeholder:text-dark-400',
        'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'scrollbar-thin',
        className
      )}
      {...props}
    />
  );
}

export default Input;
