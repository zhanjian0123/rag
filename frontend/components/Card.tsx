import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = "", hover = true }: CardProps) {
  return (
    <div
      className={`
        bg-white rounded-lg border border-slate-200 overflow-hidden
        ${hover ? "hover:border-slate-300 hover:shadow-md transition-all duration-200" : ""}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "" }: CardHeaderProps) {
  return (
    <div className={`px-4 py-3 border-b border-slate-100 bg-slate-50/50 ${className}`}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = "" }: CardTitleProps) {
  return <h3 className={`text-sm font-medium text-slate-900 ${className}`}>{children}</h3>;
}

export function CardDescription({ children, className = "" }: CardDescriptionProps) {
  return <p className={`text-xs text-slate-500 mt-1 ${className}`}>{children}</p>;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={`px-4 py-3 ${className}`}>{children}</div>;
}
