import { cn } from '../../lib/utils';

export function Card({ className, children, hover = false, glow = false, ...props }) {
  return (
    <div
      className={cn(
        'rounded-xl bg-dark-800/50 border border-dark-700',
        'backdrop-blur-sm',
        hover && 'hover:border-primary-500/50 hover:bg-dark-800/80 transition-all duration-300 cursor-pointer',
        glow && 'hover:shadow-lg hover:shadow-primary-500/10',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children, ...props }) {
  return (
    <div className={cn('px-6 py-4 border-b border-dark-700', className)} {...props}>
      {children}
    </div>
  );
}

export function CardContent({ className, children, ...props }) {
  return (
    <div className={cn('px-6 py-4', className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className, children, ...props }) {
  return (
    <div className={cn('px-6 py-4 border-t border-dark-700', className)} {...props}>
      {children}
    </div>
  );
}

export default Card;
