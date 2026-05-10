import { BookOpen, User, Database, FlaskConical, AlertCircle } from 'lucide-react';

const CLASSES = ['Eosinophil', 'Lymphocyte', 'Monocyte', 'Neutrophil'];
const STACK = ['FastAPI', 'React', 'TensorFlow', 'Tailwind CSS'];

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-gray-50">

            {/* ── Page hero ──────────────────────────────────────────────── */}
            <section className="bg-[#172F7C] text-white py-14 sm:py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto text-center">
                    <p className="text-sm font-semibold text-[#2DC6B2] uppercase tracking-widest mb-3">About</p>
                    <h1 className="text-3xl sm:text-4xl font-extrabold leading-tight mb-5">
                        Redefining WBC Differential Counts
                    </h1>
                    <p className="text-blue-200 text-base sm:text-lg leading-relaxed">
                        LeukoScan provides a digital second opinion for hematology labs, powered by a custom CNN that scans blood smear images, identifies morphological patterns, and classifies four major WBC types with confidence scores.
                    </p>
                </div>
            </section>

            {/* ── Content ────────────────────────────────────────────────── */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-6">

                {/* Developer card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
                    <div className="flex items-center gap-2 mb-6">
                        <div className="w-8 h-8 rounded-lg bg-[#1CBDC9]/10 flex items-center justify-center">
                            <User size={18} className="text-[#1CBDC9]" />
                        </div>
                        <h2 className="text-base font-bold text-[#172F7C]">Developer</h2>
                    </div>
                    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                        {/* Photo slot */}
                        <div className="shrink-0">
                            <img
                                src="/developer-photo.jpg"
                                alt="Developer"
                                className="w-24 h-24 sm:w-28 sm:h-28 rounded-full object-cover border-4 border-[#2DC6B2] shadow-md"
                                onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                    e.currentTarget.nextSibling.style.display = 'flex';
                                }}
                            />
                            <div
                                className="w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-[#172F7C]/8 border-4 border-[#2DC6B2] shadow-md hidden items-center justify-center"
                                aria-hidden="true"
                            >
                                <User size={44} className="text-[#172F7C]/30" />
                            </div>
                        </div>
                        <div className="text-center sm:text-left">
                            <p className="text-lg font-bold text-[#172F7C] leading-tight">
                                Paul Emmanuelle Quimpo
                            </p>
                            <p className="text-xs font-medium text-[#2DC6B2] mb-3">
                                Bachelor of Science in Computer Science
                            </p>
                            <p className="text-sm text-gray-600 leading-relaxed mb-3">
                                Developed as the Final Laboratory requirement for the Event-Driven
                                Programming course. Integrates a pre-trained Keras CNN with a FastAPI
                                backend and React frontend — demonstrating end-to-end event-driven
                                architecture from model inference to browser UI.
                            </p>

                        </div>
                    </div>
                </div>

                {/* Two-column grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Academic Context */}
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        <div className="flex items-center gap-2 mb-5">
                            <div className="w-8 h-8 rounded-lg bg-[#2DC6B2]/10 flex items-center justify-center">
                                <BookOpen size={18} className="text-[#2DC6B2]" />
                            </div>
                            <h2 className="text-base font-bold text-[#172F7C]">Academic Context</h2>
                        </div>
                        <dl className="space-y-3 text-sm">
                            <div>
                                <dt className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Course</dt>
                                <dd className="text-gray-700">Event-Driven Programming</dd>
                            </div>
                            <div>
                                <dt className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Task</dt>
                                <dd className="text-gray-700">
                                    Build a full-stack ML web application
                                    <span className="ml-1.5 inline-block bg-[#172F7C]/10 text-[#172F7C] text-xs font-semibold px-2 py-0.5 rounded">
                                        Final Project
                                    </span>
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Stack</dt>
                                <dd className="flex flex-wrap gap-1.5">
                                    {STACK.map((s) => (
                                        <span
                                            key={s}
                                            className="bg-[#172F7C]/8 text-[#172F7C] text-xs font-semibold px-2.5 py-1 rounded-md border border-[#172F7C]/10"
                                        >
                                            {s}
                                        </span>
                                    ))}
                                </dd>
                            </div>
                        </dl>
                    </div>

                    {/* Dataset */}
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        <div className="flex items-center gap-2 mb-5">
                            <div className="w-8 h-8 rounded-lg bg-[#A2F9AB]/40 flex items-center justify-center">
                                <Database size={18} className="text-[#2DC6B2]" />
                            </div>
                            <h2 className="text-base font-bold text-[#172F7C]">Dataset</h2>
                        </div>
                        <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                            Trained on a curated dataset of white blood cell microscopy images split across
                            training, validation, and test sets — four classes:
                        </p>
                        <div className="flex flex-wrap gap-2 mb-4">
                            {CLASSES.map((c) => (
                                <span
                                    key={c}
                                    className="bg-[#A2F9AB] text-[#172F7C] text-xs font-semibold px-3 py-1 rounded-full"
                                >
                                    {c}
                                </span>
                            ))}
                        </div>
                        <p className="text-xs text-gray-400 border-t border-gray-100 pt-3">
                            Images resized to 150×150 px · Pixel values normalized to [0, 1]
                        </p>
                    </div>
                </div>

                {/* About the Project — full width */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
                    <div className="flex items-center gap-2 mb-5">
                        <div className="w-8 h-8 rounded-lg bg-[#172F7C]/8 flex items-center justify-center">
                            <FlaskConical size={18} className="text-[#172F7C]" />
                        </div>
                        <h2 className="text-base font-bold text-[#172F7C]">About the Project</h2>
                    </div>
                    <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
                        <p>
                            LeukoScan classifies white blood cell microscopy images using a CNN trained with
                            TensorFlow/Keras. The architecture stacks convolutional blocks — Conv2D,
                            ReLU activation, and MaxPooling — followed by dense layers and a 4-class
                            Softmax output.
                        </p>
                        <p>
                            The FastAPI backend loads the trained{' '}
                            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-[#172F7C] text-xs">.keras</code>{' '}
                            model at startup and exposes a{' '}
                            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-[#172F7C] text-xs">POST /predict</code>{' '}
                            endpoint. The React frontend provides a drag-and-drop interface and displays
                            the predicted cell type with a confidence score bar.
                        </p>
                    </div>
                </div>

                {/* Clinical Disclaimer */}
                <div className="bg-[#F0756C]/5 border border-[#F0756C]/20 rounded-2xl p-6 flex gap-4 items-start">
                    <div className="w-9 h-9 rounded-xl bg-[#F0756C]/10 flex items-center justify-center shrink-0 mt-0.5">
                        <AlertCircle size={18} className="text-[#F0756C]" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-[#172F7C] mb-1">Clinical Disclaimer</h3>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            LeukoScan is an assistive research tool, not a substitute for professional
                            clinical diagnosis. All results should be confirmed by a qualified medical
                            professional using standard laboratory procedures. This tool supports four
                            major leukocyte classes only and does not classify basophils, red blood cells,
                            platelets, parasites, or smear artifacts.
                        </p>
                    </div>
                </div>

            </div>
        </div>
    );
}
