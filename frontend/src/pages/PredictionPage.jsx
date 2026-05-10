import usePrediction from '../hooks/usePrediction';
import DropZone from '../components/DropZone';
import PredictButton from '../components/PredictButton';
import ResultCard from '../components/ResultCard';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { Microscope, Info, AlertCircle, Lock, X } from 'lucide-react';

const CELL_TYPES = ['Eosinophil', 'Lymphocyte', 'Monocyte', 'Neutrophil'];

export default function PredictionPage() {
    const {
        file,
        previewUrl,
        isLoading,
        result,
        error,
        handleFileAccepted,
        handleFileRejected,
        handlePredict,
        handleClear,
    } = usePrediction();

    return (
        <div className="min-h-screen bg-gray-50">

            {/* ── Page hero ──────────────────────────────────────────────── */}
            <section className="bg-[#172F7C] text-white py-10 sm:py-14 px-4 sm:px-6 lg:px-8">
                <div className="max-w-2xl mx-auto text-center">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 mb-4">
                        <Microscope size={24} className="text-[#2DC6B2]" />
                    </div>
                    <h1 className="text-2xl sm:text-3xl font-extrabold mb-2">
                        White Blood Cell Classifier
                    </h1>
                    <p className="text-blue-200 text-sm sm:text-base max-w-lg mx-auto">
                        Upload a microscopy image to identify the leukocyte type and view a confidence score.
                    </p>
                </div>
            </section>

            {/* ── Main layout ────────────────────────────────────────────── */}
            <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-4">

                {/* Upload card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

                    {/* Card header */}
                    <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                        <div>
                            <h2 className="text-sm font-bold text-[#172F7C]">Upload Image</h2>
                            <p className="text-xs text-gray-400 mt-0.5">
                                JPEG or PNG only · Recommended: single-cell crop; images will be resized to 150×150 px.
                            </p>
                        </div>
                        {file && !isLoading && (
                            <button
                                onClick={handleClear}
                                className="flex items-center gap-1 text-xs text-gray-400 hover:text-[#F0756C] transition-colors ml-4 shrink-0"
                                aria-label="Clear uploaded image"
                            >
                                <X size={14} />
                                Clear
                            </button>
                        )}
                    </div>

                    {/* Card body */}
                    <div className="p-6 flex flex-col gap-5">

                        {/* Drop zone */}
                        <DropZone
                            onFileAccepted={handleFileAccepted}
                            onFileRejected={handleFileRejected}
                            previewUrl={previewUrl}
                        />

                        {/* Input guidance */}
                        {!file && (
                            <div className="bg-gray-50 rounded-xl border border-gray-100 px-4 py-3 space-y-1.5">
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                    Input Guidance
                                </p>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    <span className="font-medium text-gray-600">Recommended:</span>{' '}
                                    A clear, single-cell crop showing one white blood cell centered in the frame.
                                </p>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    <span className="font-medium text-gray-600">File limits:</span>{' '}
                                    JPEG or PNG; max 5 MB; images are automatically resized to 150×150 px.
                                </p>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    <span className="font-medium text-gray-600">If no cell is detected:</span>{' '}
                                    Try cropping closer to a single cell or upload a higher-quality image.
                                </p>
                            </div>
                        )}

                        {/* File validation error */}
                        {error && !result && !isLoading && <ErrorMessage message={error} />}

                        {/* Action row */}
                        <div className="flex items-center justify-center gap-3">
                            <PredictButton
                                onClick={handlePredict}
                                disabled={!file || isLoading}
                                isLoading={isLoading}
                            />
                            {file && !isLoading && (
                                <button
                                    onClick={handleClear}
                                    className="
                    inline-flex items-center gap-1.5
                    border border-gray-200 text-gray-500
                    hover:border-[#F0756C]/50 hover:text-[#F0756C]
                    text-sm font-medium px-5 py-3 rounded-lg
                    transition-colors
                  "
                                >
                                    <X size={14} />
                                    Clear
                                </button>
                            )}
                        </div>

                        {/* Loading */}
                        {isLoading && <LoadingSpinner />}

                        {/* Result */}
                        {result && !isLoading && (
                            <ResultCard
                                predictedClass={result.predictedClass}
                                confidence={result.confidence}
                            />
                        )}

                        {/* Confidence guidance — shown when result is low confidence */}
                        {result && !isLoading && result.confidence < 0.6 && (
                            <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                                <Info size={15} className="text-amber-500 mt-0.5 shrink-0" />
                                <p className="text-xs text-amber-700 leading-relaxed">
                                    Confidence below 60% — this result should be reviewed manually by a qualified professional.
                                </p>
                            </div>
                        )}

                        {/* API / network error after predict attempt */}
                        {error && result === null && !isLoading && file !== null && (
                            <ErrorMessage message={error} />
                        )}

                    </div>
                </div>

                {/* Output explanation */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-5">
                    <div className="flex items-center gap-2 mb-3">
                        <Info size={15} className="text-[#1CBDC9]" />
                        <h3 className="text-xs font-bold text-[#172F7C] uppercase tracking-wide">
                            Output Explanation
                        </h3>
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-500 leading-relaxed">
                        <li>
                            <span className="font-medium text-gray-600">Result:</span>{' '}
                            Predicted class label + confidence score (0–100%).
                        </li>
                        <li>
                            <span className="font-medium text-gray-600">Confidence guidance:</span>{' '}
                            Scores below 60% should be reviewed manually.
                        </li>
                    </ul>
                </div>

                {/* Detectable cell types */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-5">
                    <p className="text-xs font-bold text-[#172F7C] uppercase tracking-wide mb-3">
                        Detectable Cell Types
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {CELL_TYPES.map((c) => (
                            <span
                                key={c}
                                className="bg-[#172F7C]/5 text-[#172F7C] text-xs font-medium px-3 py-1 rounded-full border border-[#172F7C]/10"
                            >
                                {c}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Notes & Limitations */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-5">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertCircle size={15} className="text-[#F0756C]" />
                        <h3 className="text-xs font-bold text-[#172F7C] uppercase tracking-wide">
                            Notes &amp; Limitations
                        </h3>
                    </div>
                    <ul className="space-y-2 text-xs text-gray-500 leading-relaxed list-disc list-inside">
                        <li>
                            LeukoScan supports four major WBC classes only; it does not classify basophils,
                            red blood cells, platelets, parasites, or smear artifacts.
                        </li>
                        <li>
                            This tool is assistive and not a substitute for clinical diagnosis. Confirm
                            findings with standard laboratory procedures.
                        </li>
                    </ul>
                </div>

                {/* Privacy note */}
                <div className="flex items-start gap-3 bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-4">
                    <Lock size={14} className="text-gray-300 mt-0.5 shrink-0" />
                    <p className="text-xs text-gray-400 leading-relaxed">
                        <span className="font-medium text-gray-500">Privacy:</span>{' '}
                        Uploaded images are processed transiently and are not stored long-term.
                    </p>
                </div>

            </div>
        </div>
    );
}
