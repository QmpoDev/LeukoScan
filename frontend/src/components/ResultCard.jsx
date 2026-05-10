import { CheckCircle2 } from 'lucide-react';

const CLASS_META = {
    Eosinophil: { desc: 'Involved in allergic responses and parasite defense.', color: 'text-[#0e9ab0]', bar: 'bg-[#1CBDC9]' },
    Lymphocyte: { desc: 'Key immune cell for adaptive immunity and antibody production.', color: 'text-[#1a9e8e]', bar: 'bg-[#2DC6B2]' },
    Monocyte: { desc: 'Large WBC that differentiates into macrophages and dendritic cells.', color: 'text-[#172F7C]', bar: 'bg-[#172F7C]' },
    Neutrophil: { desc: 'Most abundant WBC; first responder to bacterial infections.', color: 'text-[#c94f47]', bar: 'bg-[#F0756C]' },
};

export default function ResultCard({ predictedClass, confidence }) {
    const pct = (confidence * 100).toFixed(2);
    const meta = CLASS_META[predictedClass] ?? { desc: '', color: 'text-[#172F7C]', bar: 'bg-[#1CBDC9]' };

    return (
        <div className="rounded-xl border border-[#A2F9AB] bg-gradient-to-br from-[#A2F9AB]/30 to-white p-6 shadow-sm">

            {/* Header */}
            <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 rounded-lg bg-[#A2F9AB] flex items-center justify-center">
                    <CheckCircle2 size={16} className="text-[#172F7C]" />
                </div>
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Classification Result
                </span>
            </div>

            {/* Cell type */}
            <p className={`text-3xl sm:text-4xl font-extrabold tracking-tight mb-1 ${meta.color}`}>
                {predictedClass}
            </p>
            {meta.desc && (
                <p className="text-xs text-gray-500 mb-5">{meta.desc}</p>
            )}

            {/* Confidence bar */}
            <div>
                <div className="flex justify-between items-center text-xs font-semibold text-gray-600 mb-2">
                    <span>Confidence Score</span>
                    <span className="text-base font-extrabold text-[#172F7C]">{pct}%</span>
                </div>
                <div className="bg-gray-200 rounded-full h-3 w-full overflow-hidden">
                    <div
                        className={`${meta.bar} h-3 rounded-full transition-all duration-700 ease-out`}
                        style={{ width: `${confidence * 100}%` }}
                        role="progressbar"
                        aria-valuenow={confidence * 100}
                        aria-valuemin={0}
                        aria-valuemax={100}
                    />
                </div>
                <div className="flex justify-between text-xs text-gray-300 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                </div>
            </div>
        </div>
    );
}
