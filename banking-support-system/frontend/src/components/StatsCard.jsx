export default function StatsCard({ title, value, subtitle, icon }) {
  return (
    <div className="card relative overflow-hidden">
      {/* Icon (top-right) */}
      {icon && (
        <span className="absolute top-4 right-4 text-2xl opacity-20">
          {icon}
        </span>
      )}

      <p className="text-sm font-medium text-gray-500">{title}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && (
        <p className="mt-1 text-xs text-gray-400">{subtitle}</p>
      )}
    </div>
  );
}
