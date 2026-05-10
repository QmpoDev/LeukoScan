export default function LoadingSpinner() {
    return (
        <div className="flex flex-col items-center gap-3 py-4" role="status" aria-label="Analyzing image">
            <div className="relative w-10 h-10">
                <div className="absolute inset-0 rounded-full border-4 border-gray-100" />
                <div className="absolute inset-0 rounded-full border-4 border-[#1CBDC9] border-t-transparent animate-spin" />
            </div>
            <p className="text-xs font-medium text-gray-400 tracking-wide">Analyzing image…</p>
        </div>
    );
}
