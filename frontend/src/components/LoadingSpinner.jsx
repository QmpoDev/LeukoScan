import { useEffect, useState } from 'react';

export default function LoadingSpinner() {
    const [seconds, setSeconds] = useState(0);

    useEffect(() => {
        const id = setInterval(() => setSeconds((s) => s + 1), 1000);
        return () => clearInterval(id);
    }, []);

    // After 8 seconds, show a cold-start warning
    const isSlow = seconds >= 8;

    return (
        <div className="flex flex-col items-center gap-3 py-4" role="status" aria-label="Analyzing image">
            <div className="relative w-10 h-10">
                <div className="absolute inset-0 rounded-full border-4 border-gray-100" />
                <div className="absolute inset-0 rounded-full border-4 border-[#1CBDC9] border-t-transparent animate-spin" />
            </div>
            {!isSlow ? (
                <p className="text-xs font-medium text-gray-400 tracking-wide">Analyzing image…</p>
            ) : (
                <div className="text-center space-y-1">
                    <p className="text-xs font-medium text-gray-500">Still working…</p>
                    <p className="text-xs text-gray-400 max-w-xs">
                        The server may be waking up from sleep. This can take up to 60 seconds on first use.
                    </p>
                </div>
            )}
        </div>
    );
}
