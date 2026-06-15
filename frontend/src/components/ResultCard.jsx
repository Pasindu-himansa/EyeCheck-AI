import { Eye, AlertTriangle, CheckCircle, HelpCircle } from "lucide-react";

const conditionStyles = {
  Normal: {
    color: "text-green-300",
    bg: "bg-green-400/10",
    border: "border-green-400/30",
    icon: CheckCircle,
  },
  Keratoconus: {
    color: "text-red-300",
    bg: "bg-red-400/10",
    border: "border-red-400/30",
    icon: AlertTriangle,
  },
  Astigmatism: {
    color: "text-yellow-300",
    bg: "bg-yellow-400/10",
    border: "border-yellow-400/30",
    icon: Eye,
  },
  Suspect: {
    color: "text-orange-300",
    bg: "bg-orange-400/10",
    border: "border-orange-400/30",
    icon: AlertTriangle,
  },
  Inconclusive: {
    color: "text-gray-300",
    bg: "bg-gray-400/10",
    border: "border-gray-400/30",
    icon: HelpCircle,
  },
};

function getConfidenceStyle(percentage) {
  if (percentage <= 25) return { text: "text-green-300", bar: "bg-green-400" };
  if (percentage <= 50) return { text: "text-amber-300", bar: "bg-amber-400" };
  if (percentage <= 75)
    return { text: "text-orange-300", bar: "bg-orange-400" };
  return { text: "text-red-300", bar: "bg-red-400" };
}

const modelLabels = {
  groq: "Groq Vision AI",
  local: "Local CNN Model",
};

function ResultCard({ result }) {
  const style =
    conditionStyles[result.condition] || conditionStyles.Inconclusive;
  const Icon = style.icon;
  const confidence = result.confidence_percentage ?? 0;
  const confStyle = getConfidenceStyle(confidence);

  return (
    <div className="w-full space-y-4">
      {/* Model used badge */}
      {result.model_used && (
        <p className="text-xs text-white/40 uppercase tracking-wide text-right">
          Analyzed with: {modelLabels[result.model_used] || result.model_used}
        </p>
      )}

      {/* Disease box */}
      <div
        className={`flex items-center gap-3 rounded-xl border ${style.border} ${style.bg} p-4`}
      >
        <Icon className={style.color} size={32} />
        <div>
          <p className="text-xs text-white/50 uppercase tracking-wide">
            Detected Condition
          </p>
          <p className={`text-xl font-bold ${style.color}`}>
            {result.condition}
          </p>
        </div>
      </div>

      {/* Confidence box */}
      <div className="rounded-xl border border-white/20 bg-white/5 p-4">
        <div className="flex justify-between text-sm text-white/70 mb-2">
          <span>Confidence Level</span>
          <span className={`font-semibold ${confStyle.text}`}>
            {confidence}%
          </span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-2">
          <div
            className={`${confStyle.bar} h-2 rounded-full transition-all`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Explanation box */}
      <div className="rounded-xl border border-white/20 bg-white/5 p-4">
        <p className="text-xs text-white/50 uppercase tracking-wide mb-1">
          Analysis
        </p>
        <p className="text-sm text-white/80">{result.explanation}</p>
      </div>

      {/* Disclaimer */}
      <p className="text-xs italic text-white/40 border-t border-white/10 pt-3">
        {result.disclaimer}
      </p>
    </div>
  );
}

export default ResultCard;
