import { Microscope, Loader2 } from 'lucide-react';

export default function PredictButton({ onClick, disabled, isLoading }) {
    return (
        <button
            type="button"
            onClick={onClick}
            disabled={disabled}
            className="
        inline-flex items-center gap-2
        bg-[#172F7C] hover:bg-[#1CBDC9]
        disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed
        text-white font-semibold
        px-8 py-3 rounded-lg text-sm
        transition-colors shadow-sm
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1CBDC9] focus-visible:ring-offset-2
      "
        >
            {isLoading
                ? <Loader2 size={16} className="animate-spin" />
                : <Microscope size={16} />
            }
            {isLoading ? 'Analyzing…' : 'Run Classification'}
        </button>
    );
}
