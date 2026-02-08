import { cn } from '../../lib/utils';

const badgeVariants = {
  default: 'bg-dark-700 text-dark-200',
  primary: 'bg-primary-500/20 text-primary-400 border border-primary-500/30',
  success: 'bg-accent-500/20 text-accent-400 border border-accent-500/30',
  warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
  danger: 'bg-red-500/20 text-red-400 border border-red-500/30',
  info: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30',
};

export function Badge({ children, variant = 'default', className, ...props }) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        badgeVariants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const variants = {
    Critical: 'danger',
    High: 'warning',
    Medium: 'info',
    Low: 'default',
  };
  return <Badge variant={variants[priority] || 'default'}>{priority}</Badge>;
}

export function StatusBadge({ status }) {
  const variants = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    edited: 'info',
  };
  const labels = {
    pending: 'Pending Review',
    approved: 'Approved',
    rejected: 'Rejected',
    edited: 'Edited',
  };
  return <Badge variant={variants[status] || 'default'}>{labels[status] || status}</Badge>;
}

export default Badge;
