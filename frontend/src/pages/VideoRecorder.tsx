import React, { useState, useRef } from 'react';
import { Video, StopCircle, Save, Loader2 } from 'lucide-react';

const VideoRecorder: React.FC = () => {
    const [isRecording, setIsRecording] = useState<boolean>(false);
    const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);
    const [savePath, setSavePath] = useState<string>('');
    const [isSaving, setIsSaving] = useState<boolean>(false);
    const [message, setMessage] = useState<string>('');

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }

            mediaRecorderRef.current = new MediaRecorder(stream);
            mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
                if (event.data.size > 0) {
                    setRecordedChunks((prev) => [...prev, event.data]);
                }
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
            setMessage('');
        } catch (error) {
            console.error("Error accessing media devices:", error);
            setMessage('Error accessing camera/microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
        setIsRecording(false);
        if (videoRef.current && videoRef.current.srcObject) {
            const stream = videoRef.current.srcObject as MediaStream;
            stream.getTracks().forEach(track => track.stop());
        }
    };

    const saveVideo = async () => {
        if (recordedChunks.length === 0) return;
        if (!savePath) {
            setMessage('Please enter a save path');
            return;
        }

        setIsSaving(true);
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('file', blob, `journal_${Date.now()}.webm`);
        formData.append('save_path', savePath);

        try {
            const response = await fetch('http://localhost:8000/api/save-video', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setMessage(`Video saved to: ${data.path}`);
                setRecordedChunks([]);
            } else {
                const error = await response.json();
                setMessage(`Error saving video: ${error.detail}`);
            }
        } catch (error) {
            console.error("Error saving video:", error);
            setMessage('Network error saving video');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 flex flex-col gap-4">
            <h2 className="text-xl font-semibold text-stone-800 flex items-center gap-2">
                <Video className="w-5 h-5" /> Video Journal
            </h2>

            <div className="relative aspect-video bg-stone-900 rounded-lg overflow-hidden flex items-center justify-center">
                <video ref={videoRef} autoPlay muted className="w-full h-full object-cover" />
                {!isRecording && recordedChunks.length === 0 && (
                    <div className="absolute text-stone-500">Camera Off</div>
                )}
            </div>

            <div className="flex flex-col gap-3">
                <input
                    type="text"
                    placeholder="Enter folder path to save video (e.g., ~/Movies/Journal)"
                    value={savePath}
                    onChange={(e) => setSavePath(e.target.value)}
                    className="w-full p-2 border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-stone-400 text-sm"
                />

                <div className="flex gap-2">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            className="flex-1 bg-stone-800 text-white py-2 px-4 rounded-lg hover:bg-stone-700 transition-colors flex items-center justify-center gap-2"
                        >
                            <Video className="w-4 h-4" /> Start Recording
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="flex-1 bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
                        >
                            <StopCircle className="w-4 h-4" /> Stop Recording
                        </button>
                    )}

                    {recordedChunks.length > 0 && !isRecording && (
                        <button
                            onClick={saveVideo}
                            disabled={isSaving}
                            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            Save Video
                        </button>
                    )}
                </div>

                {message && <div className="text-sm text-stone-600 text-center">{message}</div>}
            </div>
        </div>
    );
};

export default VideoRecorder;
