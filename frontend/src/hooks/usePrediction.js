import { useState } from 'react';

const API_URL = 'http://localhost:8000/predict';

/**
 * usePrediction — encapsulates all state and logic for the Prediction page.
 *
 * Returns:
 *   file            — the currently selected File object (or null)
 *   previewUrl      — object URL for image preview (or null)
 *   isLoading       — true while the fetch is in progress
 *   result          — { predictedClass: string, confidence: number } | null
 *   error           — error message string | null
 *   handleFileAccepted(file)  — called by DropZone on valid file selection
 *   handleFileRejected(reason) — called by DropZone on invalid file type
 *   handlePredict()           — sends the image to the API
 */
export default function usePrediction() {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    function handleFileAccepted(newFile) {
        // Revoke previous object URL to avoid memory leaks
        if (previewUrl) URL.revokeObjectURL(previewUrl);

        setFile(newFile);
        setPreviewUrl(URL.createObjectURL(newFile));
        setResult(null);
        setError(null);
    }

    function handleFileRejected(reason) {
        if (previewUrl) URL.revokeObjectURL(previewUrl);

        setFile(null);
        setPreviewUrl(null);
        setResult(null);
        setError(reason);
    }

    async function handlePredict() {
        if (!file || isLoading) return;

        // Client-side file size guard (5 MB)
        if (file.size > 5 * 1024 * 1024) {
            setError('File exceeds the 5 MB limit. Please upload a smaller image.');
            return;
        }

        setIsLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const json = await response.json();
                setResult({
                    predictedClass: json.predicted_class,
                    confidence: json.confidence,
                });
            } else {
                // Try to extract the API's error message, fall back to generic
                let message = 'Prediction failed. Please try again.';
                try {
                    const errJson = await response.json();
                    if (errJson?.error) message = errJson.error;
                } catch {
                    // ignore JSON parse failure
                }
                setError(message);
            }
        } catch {
            setError('Could not reach the server. Is the backend running?');
        } finally {
            setIsLoading(false);
        }
    }

    function handleClear() {
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        setFile(null);
        setPreviewUrl(null);
        setResult(null);
        setError(null);
    }

    return {
        file,
        previewUrl,
        isLoading,
        result,
        error,
        handleFileAccepted,
        handleFileRejected,
        handlePredict,
        handleClear,
    };
}
