import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function getRiskColor(level: string): string {
  const colors: Record<string, string> = {
    low: "text-green-600 bg-green-50 border-green-200",
    medium: "text-amber-600 bg-amber-50 border-amber-200",
    high: "text-red-600 bg-red-50 border-red-200",
    critical: "text-red-800 bg-red-100 border-red-300",
  };
  return colors[level] || colors.low;
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    info: "text-blue-600 bg-blue-50 border-blue-200",
    warning: "text-amber-600 bg-amber-50 border-amber-200",
    critical: "text-red-600 bg-red-50 border-red-200",
    emergency: "text-red-800 bg-red-100 border-red-300",
  };
  return colors[severity] || colors.info;
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: "text-gray-600 bg-gray-50",
    pending_approval: "text-amber-600 bg-amber-50",
    approved: "text-blue-600 bg-blue-50",
    in_progress: "text-purple-600 bg-purple-50",
    completed: "text-green-600 bg-green-50",
    cancelled: "text-red-600 bg-red-50",
  };
  return colors[status] || colors.draft;
}
