const tiers = [
  { min: 90, label: 'Excellent',      bg: 'bg-green-100',  text: 'text-green-800',  ring: 'ring-green-300'  },
  { min: 75, label: 'Good',           bg: 'bg-blue-100',   text: 'text-blue-800',   ring: 'ring-blue-300'   },
  { min: 60, label: 'Acceptable',     bg: 'bg-yellow-100', text: 'text-yellow-800', ring: 'ring-yellow-300' },
  { min: 0,  label: 'Review Needed',  bg: 'bg-red-100',    text: 'text-red-800',    ring: 'ring-red-300'    },
];

function getTier(score) {
  return tiers.find((t) => score >= t.min) || tiers[tiers.length - 1];
}

export default function ConfidenceScore({ score }) {
  const tier = getTier(score);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm
                  font-semibold ring-1 ring-inset ${tier.bg} ${tier.text} ${tier.ring}`}
    >
      {score}% &mdash; {tier.label}
    </span>
  );
}
