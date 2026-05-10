import { Link } from 'react-router-dom';
import { Microscope, Brain, Zap, BarChart2, ScanSearch, ArrowRight, CheckCircle } from 'lucide-react';

const HIGHLIGHTS = [
    {
        icon: <Brain size={26} className="text-[#1CBDC9]" />,
        title: 'Deep Learning Precision',
        desc: 'CNN trained on 12,000+ images for robust, reliable recognition.',
    },
    {
        icon: <ScanSearch size={26} className="text-[#1CBDC9]" />,
        title: 'Four-Class Detection',
        desc: 'Specialized for Eosinophils, Lymphocytes, Monocytes, and Neutrophils.',
    },
    {
        icon: <Zap size={26} className="text-[#1CBDC9]" />,
        title: 'Real-Time Inference',
        desc: 'FastAPI backend delivers results in milliseconds, not minutes.',
    },
    {
        icon: <BarChart2 size={26} className="text-[#1CBDC9]" />,
        title: 'Confidence Metrics',
        desc: 'Every result includes a probability score for full transparency.',
    },
];

const CELL_TYPES = ['Eosinophil', 'Lymphocyte', 'Monocyte', 'Neutrophil'];

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gray-50">

            {/* ── Hero ─────────────────────────────────────────────────────── */}
            <section className="relative bg-[#172F7C] text-white overflow-hidden">
                {/* Subtle background pattern */}
                <div className="absolute inset-0 opacity-5 pointer-events-none"
                    style={{ backgroundImage: 'radial-gradient(circle at 25% 50%, #2DC6B2 0%, transparent 60%), radial-gradient(circle at 75% 20%, #1CBDC9 0%, transparent 50%)' }}
                />
                <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 text-center">
                    <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-1.5 text-sm text-[#A2F9AB] font-medium mb-6">
                        <span className="w-2 h-2 rounded-full bg-[#A2F9AB] animate-pulse" />
                        Assistive Research Tool
                    </div>
                    <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight tracking-tight mb-6">
                        Precision White Blood Cell<br className="hidden sm:block" />
                        <span className="text-[#2DC6B2]"> Analysis at High Speed.</span>
                    </h1>
                    <p className="text-base sm:text-lg text-blue-200 max-w-2xl mx-auto mb-10 leading-relaxed">
                        LeukoScan uses Deep Learning to automate white blood cell classification — bridging microscopy and AI for instant, high-accuracy recognition of the four major leukocyte types: Eosinophils, Lymphocytes, Monocytes, and Neutrophils.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            to="/predict"
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-[#2DC6B2] hover:bg-[#1CBDC9] text-white font-bold px-8 py-3.5 rounded-lg text-base transition-colors shadow-lg"
                        >
                            <Microscope size={18} />
                            Try the Classifier
                            <ArrowRight size={16} />
                        </Link>
                        <Link
                            to="/features"
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 border border-white/30 text-white font-semibold px-8 py-3.5 rounded-lg text-base transition-colors"
                        >
                            Learn More
                        </Link>
                    </div>

                    {/* Cell type pills */}
                    <div className="flex flex-wrap justify-center gap-2 mt-10">
                        {CELL_TYPES.map((c) => (
                            <span key={c} className="bg-white/10 border border-white/20 text-white/80 text-xs font-medium px-3 py-1 rounded-full">
                                {c}
                            </span>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── Why LeukoScan ────────────────────────────────────────────── */}
            <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 bg-white">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <p className="text-sm font-semibold text-[#2DC6B2] uppercase tracking-widest mb-2">Capabilities</p>
                        <h2 className="text-2xl sm:text-3xl font-extrabold text-[#172F7C]">
                            Why LeukoScan?
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                        {HIGHLIGHTS.map(({ icon, title, desc }) => (
                            <div
                                key={title}
                                className="bg-gray-50 rounded-xl p-6 border border-gray-100 hover:border-[#2DC6B2]/50 hover:shadow-md transition-all flex flex-col gap-3"
                            >
                                <div className="w-10 h-10 rounded-lg bg-[#172F7C]/5 flex items-center justify-center">
                                    {icon}
                                </div>
                                <h3 className="font-bold text-[#172F7C] text-sm">{title}</h3>
                                <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── How it works ─────────────────────────────────────────────── */}
            <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-12">
                        <p className="text-sm font-semibold text-[#2DC6B2] uppercase tracking-widest mb-2">Workflow</p>
                        <h2 className="text-2xl sm:text-3xl font-extrabold text-[#172F7C]">
                            Three Steps to a Result
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        {[
                            { step: '01', title: 'Upload Image', desc: 'Drag and drop or browse for a JPEG or PNG blood cell microscopy image.' },
                            { step: '02', title: 'Run Analysis', desc: 'LeukoScan preprocesses and passes the image through the CNN model.' },
                            { step: '03', title: 'View Results', desc: 'Receive the predicted cell type and a confidence score instantly.' },
                        ].map(({ step, title, desc }) => (
                            <div key={step} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col gap-3">
                                <span className="text-3xl font-extrabold text-[#2DC6B2]/40">{step}</span>
                                <h3 className="font-bold text-[#172F7C]">{title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── Final CTA ────────────────────────────────────────────────── */}
            <section className="py-14 sm:py-16 px-4 sm:px-6 lg:px-8 bg-[#172F7C]">
                <div className="max-w-3xl mx-auto text-center">
                    <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-3">
                        Ready to analyze a white blood cell image?
                    </h2>
                    <p className="text-blue-200 mb-2 text-sm sm:text-base">
                        Upload a JPEG or PNG — no account, no setup required.
                    </p>
                    <ul className="flex flex-wrap justify-center gap-x-6 gap-y-1 text-xs text-blue-300 mb-8">
                        {['Free to use', 'Instant results', 'JPEG & PNG supported'].map((t) => (
                            <li key={t} className="flex items-center gap-1">
                                <CheckCircle size={12} className="text-[#A2F9AB]" /> {t}
                            </li>
                        ))}
                    </ul>
                    <Link
                        to="/predict"
                        className="inline-flex items-center gap-2 bg-[#2DC6B2] hover:bg-[#1CBDC9] text-white font-bold px-8 py-3.5 rounded-lg text-base transition-colors shadow-lg"
                    >
                        <Microscope size={18} />
                        Start Classifying
                        <ArrowRight size={16} />
                    </Link>
                </div>
            </section>

        </div>
    );
}
