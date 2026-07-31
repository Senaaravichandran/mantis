"use client";

interface Props {
  score: number;
  label?: string;
  size?: number;
}

export function RiskScoreGauge({ score, label = "Risk Score", size = 120 }: Props) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clampedScore / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 70) return "#dc2626";
    if (s >= 40) return "#f59e0b";
    return "#16a34a";
  };

  const color = getColor(clampedScore);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#f3f4f6"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-2xl font-bold" style={{ color }}>{clampedScore}</span>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
    </div>
  );
}
