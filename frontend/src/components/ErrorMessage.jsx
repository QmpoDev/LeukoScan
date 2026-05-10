import { AlertCircle } from 'lucide-react';

export default function ErrorMessage({ message }) {
    if (!message) return null;
    return (
        <div
            role="alert"
            className="flex items-start gap-3 bg-[#F0756C]/10 border border-[#F0756C]/30 rounded-xl px-4 py-3"
        >
            <AlertCircle size={15} className="text-[#F0756C] mt-0.5 shrink-0" />
            <span className="text-sm text-[#c94f47] leading-snug">{message}</span>
        </div>
    );
}
