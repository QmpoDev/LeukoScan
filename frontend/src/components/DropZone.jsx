import { useRef, useState } from 'react';
import { UploadCloud, ImageIcon, RefreshCw } from 'lucide-react';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png'];

/** Pure helper — exported for tests */
export function isValidMime(type) {
    return ACCEPTED_TYPES.includes(type);
}

export default function DropZone({ onFileAccepted, onFileRejected, previewUrl }) {
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef(null);

    function handleFile(file) {
        if (!file) return;
        if (isValidMime(file.type)) {
            onFileAccepted(file);
        } else {
            onFileRejected('Only JPEG and PNG images are supported.');
        }
    }

    function onDragOver(e) { e.preventDefault(); setIsDragging(true); }
    function onDragLeave(e) { e.preventDefault(); setIsDragging(false); }
    function onDrop(e) {
        e.preventDefault();
        setIsDragging(false);
        handleFile(e.dataTransfer.files?.[0]);
    }
    function onChange(e) {
        handleFile(e.target.files?.[0]);
        e.target.value = '';
    }

    return (
        <div
            role="button"
            aria-label="Drop zone — click or drag an image here"
            tabIndex={0}
            className={`
        relative rounded-xl border-2 border-dashed transition-all duration-200
        cursor-pointer select-none outline-none
        focus-visible:ring-2 focus-visible:ring-[#1CBDC9] focus-visible:ring-offset-2
        ${isDragging
                    ? 'border-[#1CBDC9] bg-[#1CBDC9]/5 scale-[1.01]'
                    : 'border-gray-200 bg-gray-50 hover:border-[#2DC6B2] hover:bg-[#2DC6B2]/5'
                }
      `}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        >
            <input
                ref={inputRef}
                type="file"
                accept="image/jpeg,image/png"
                className="hidden"
                onChange={onChange}
                data-testid="file-input"
            />

            {previewUrl ? (
                <div className="flex flex-col items-center gap-3 p-6">
                    <div className="relative">
                        <img
                            src={previewUrl}
                            alt="Selected blood cell"
                            className="max-h-52 sm:max-h-64 rounded-lg object-contain shadow-md"
                        />
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <RefreshCw size={12} />
                        Click or drop to replace
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center gap-3 py-10 px-6 text-center">
                    <div className={`
            w-14 h-14 rounded-2xl flex items-center justify-center transition-colors
            ${isDragging ? 'bg-[#1CBDC9]/15' : 'bg-[#2DC6B2]/10'}
          `}>
                        <UploadCloud size={28} className={isDragging ? 'text-[#1CBDC9]' : 'text-[#2DC6B2]'} />
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-700 mb-0.5">
                            {isDragging ? 'Drop to upload' : 'Drag & drop your image here'}
                        </p>
                        <p className="text-xs text-gray-400">or click to browse files</p>
                    </div>
                    <div className="flex items-center gap-1.5 bg-white border border-gray-200 rounded-full px-3 py-1 text-xs text-gray-400">
                        <ImageIcon size={11} />
                        JPEG or PNG · Max 5 MB · Single-cell crop recommended
                    </div>
                </div>
            )}
        </div>
    );
}
