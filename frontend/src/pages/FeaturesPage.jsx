import { Brain, ScanSearch, Zap, BarChart2, ImageIcon, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';

const KEY_FEATURES = [
    {
        icon: <Brain size={22} className="text-[#1CBDC9]" />,
        bg: 'bg-[#1CBDC9]/10',
        title: 'Deep Learning Precision',
        desc: 'CNN trained on 12,000+ white blood cell images for robust recognition of the supported classes.',
    },
    {
        icon: <ScanSearch size={22} className="text-[#2DC6B2]" />,
        bg: 'bg-[#2DC6B2]/10',
        title: 'Four-Class Differentiation',
        desc: 'Detects Eosinophils, Lymphocytes, Monocytes, and Neutrophils.',
    },
    {
        icon: <Zap size={22} className="text-[#172F7C]" />,
        bg: 'bg-[#172F7C]/8',
        title: 'Low-Latency Inference',
        desc: 'FastAPI backend provides near real-time predictions.',
    },
    {
        icon: <BarChart2 size={22} className="text-[#F0756C]" />,
        bg: 'bg-[#F0756C]/10',
        title: 'Confidence Metrics',
        desc: 'Each prediction includes a probability score for transparency.',
    },
];

const CELL_TYPES = [
    {
        name: 'Eosinophil',
        accent: 'border-[#1CBDC9]',
        badge: 'bg-[#1CBDC9]/10 text-[#0e9ab0]',
        description: 'Bi-lobed nucleus; large cytoplasmic granules; associated with parasitic infections and allergies.',
    },
    {
        name: 'Lymphocyte',
        accent: 'border-[#2DC6B2]',
        badge: 'bg-[#2DC6B2]/10 text-[#1a9e8e]',
        description: 'Large, round nucleus; central to adaptive immunity (B and T cells).',
    },
    {
        name: 'Monocyte',
        accent: 'border-[#172F7C]',
        badge: 'bg-[#172F7C]/10 text-[#172F7C]',
        description: 'Largest WBC; differentiates into macrophages and dendritic cells.',
    },
    {
        name: 'Neutrophil',
        accent: 'border-[#F0756C]',
        badge: 'bg-[#F0756C]/10 text-[#c94f47]',
        description: 'Most abundant WBC; first responder to bacterial infection.',
    },
];

const MODEL_SPECS = [
    { icon: <ImageIcon size={18} className="text-[#2DC6B2]" />, label: 'Input', value: 'JPEG or PNG image' },
    { icon: <Cpu size={18} className="text-[#2DC6B2]" />, label: 'Preprocessing', value: 'Resized to 150×150 px · Pixel values normalized to [0, 1]' },
    { icon: <CheckCircle2 size={18} className="text-[#2DC6B2]" />, label: 'Output', value: 'Class label + confidence score (0–100%)' },
];

export default function FeaturesPage() {
    return (
        <div className="min-h-screen bg-gray-50">

            {/* ── Page hero ──────────────────────────────────────────────── */}
            <section className="bg-[#172F7C] text-white py-14 sm:py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto text-center">
                    <p className="text-sm font-semibold text-[#2DC6B2] uppercase tracking-widest mb-3">Features</p>
                    <h1 className="text-3xl sm:text-4xl font-extrabold leading-tight mb-4">
                        Smarter Analysis. Faster Results.
                    </h1>
                    <p className="text-blue-200 text-base sm:text-lg leading-relaxed">
                        LeukoScan combines deep learning with a clinician-friendly interface to deliver
                        fast, transparent white blood cell classification.
                    </p>
                </div>
            </section>

            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-14">

                {/* ── Key Capabilities ───────────────────────────────────────── */}
                <div>
                    <h2 className="text-lg font-bold text-[#172F7C] mb-6">Key Capabilities</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                        {KEY_FEATURES.map(({ icon, bg, title, desc }) => (
                            <div
                                key={title}
                                className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:border-[#2DC6B2]/40 hover:shadow-md transition-all flex gap-4 items-start"
                            >
                                <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center shrink-0`}>
                                    {icon}
                                </div>
                                <div>
                                    <h3 className="font-bold text-[#172F7C] text-sm mb-1">{title}</h3>
                                    <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ── Supported Cell Types ───────────────────────────────────── */}
                <div>
                    <h2 className="text-lg font-bold text-[#172F7C] mb-6">Supported Cell Types</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                        {CELL_TYPES.map(({ name, accent, badge, description }) => (
                            <div
                                key={name}
                                className={`bg-white rounded-2xl p-6 shadow-sm border-l-4 ${accent} border border-gray-100 flex flex-col gap-2`}
                            >
                                <span className={`self-start text-xs font-bold px-3 py-1 rounded-full ${badge}`}>
                                    {name}
                                </span>
                                <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ── Model Specifications ───────────────────────────────────── */}
                <div>
                    <h2 className="text-lg font-bold text-[#172F7C] mb-6">Model Specifications</h2>
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <ul className="divide-y divide-gray-100">
                            {MODEL_SPECS.map(({ icon, label, value }) => (
                                <li key={label} className="flex items-center gap-4 px-6 py-4">
                                    <div className="w-8 h-8 rounded-lg bg-[#2DC6B2]/10 flex items-center justify-center shrink-0">
                                        {icon}
                                    </div>
                                    <span className="text-sm font-semibold text-gray-700 w-28 shrink-0">{label}</span>
                                    <span className="text-sm text-gray-500">{value}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* ── Scope Note ─────────────────────────────────────────────── */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex gap-4 items-start">
                    <div className="w-9 h-9 rounded-xl bg-[#F0756C]/10 flex items-center justify-center shrink-0 mt-0.5">
                        <AlertCircle size={18} className="text-[#F0756C]" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-[#172F7C] mb-1">Scope &amp; Limitations</h3>
                        <p className="text-sm text-gray-500 leading-relaxed">
                            LeukoScan currently supports four major leukocyte classes and does not classify
                            basophils, red blood cells, platelets, or other non-WBC elements. Results are
                            intended as a supplementary reference and should not replace professional
                            laboratory diagnosis.
                        </p>
                    </div>
                </div>

            </div>
        </div>
    );
}
