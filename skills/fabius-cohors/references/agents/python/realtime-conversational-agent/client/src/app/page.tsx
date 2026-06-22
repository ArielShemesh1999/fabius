"use client";

import { useRef, useState, useEffect } from "react";
import { useLiveConnection } from "@/hooks/useLiveConnection";
import {
  Video,
  Mic,
  Loader2,
  X,
  Monitor,
  Camera,
} from "lucide-react";
import { SidePanel } from "@/components/SidePanel";

const SourceModal = ({
  onSelect,
  onClose,
}: {
  onSelect: (source: "camera" | "screen") => void;
  onClose: () => void;
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-gray-800 rounded-lg shadow-2xl p-8 max-w-sm w-full relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
        >
          <X className="w-6 h-6" />
        </button>
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Choose your video source
        </h2>
        <div className="flex flex-col gap-4">
          <button
            onClick={() => onSelect("camera")}
            className="flex items-center justify-center gap-3 px-6 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-semibold transition-all duration-200"
          >
            <Camera className="w-6 h-6" />
            Use Camera
          </button>
          <button
            onClick={() => onSelect("screen")}
            className="flex items-center justify-center gap-3 px-6 py-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-lg font-semibold transition-all duration-200"
          >
            <Monitor className="w-6 h-6" />
            Share Screen
          </button>
        </div>
      </div>
    </div>
  );
};


export default function Home() {
  const {
    connectionState,
    latestTextMessage,
    eventLog,
    connect,
    disconnect,
  } = useLiveConnection();

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [userId] = useState(() => `client_${crypto.randomUUID()}`);
  const [showSourceModal, setShowSourceModal] = useState(false);
  
  const [activeSource, setActiveSource] = useState<'camera' | 'screen' | null>(null);

  const isStreaming = connectionState === "connected";
  const isConnecting = connectionState === "connecting";

  const handleStartStream = (source: "camera" | "screen") => {
    setShowSourceModal(false);
    if (videoRef.current && canvasRef.current) {
      setActiveSource(source);
      connect(videoRef.current, canvasRef.current, userId, source);
    } else {
      console.error("Video or Canvas refs are not set.");
    }
  };

  const handleStopStream = () => {
    disconnect();
    setActiveSource(null);
  };

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [eventLog]); 

  return (
    <main className="flex flex-col h-screen w-full">
      <canvas ref={canvasRef} className="hidden"></canvas>
      
      {showSourceModal && (
        <SourceModal
          onSelect={handleStartStream}
          onClose={() => setShowSourceModal(false)}
        />
      )}

      <div className="flex-1 overflow-hidden">
        <div className="h-full grid grid-cols-1 md:grid-cols-2 gap-6 p-6 [grid-template-rows:minmax(0,1fr)]">
          
          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg flex flex-col p-6 gap-4 overflow-hidden">
            <h2 className="text-xl font-semibold">Video Feed</h2>
            <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden border border-gray-700">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className={`
                  w-full h-full object-cover
                  ${activeSource === 'camera' ? 'transform -scale-x-100' : ''}
                `}
              />
               {!isStreaming && !isConnecting && (
                <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center z-10">
                  <Video className="w-16 h-16 text-gray-400" />
                  <p className="mt-2 text-gray-300">Video feed is offline</p>
                </div>
              )}
              {isConnecting && (
                <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex flex-col items-center justify-center z-10">
                  <Loader2 className="w-16 h-16 text-blue-400 animate-spin" />
                  <p className="mt-4 text-lg">Connecting...</p>
                </div>
              )}
              {isStreaming && (
                <div className="absolute top-4 left-4 z-20">
                  <div className="flex items-center gap-2 bg-red-600 px-3 py-1 rounded-full text-sm font-medium animate-pulse">
                    <Mic className="w-4 h-4" />
                    <span>LIVE</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg flex flex-col p-6 gap-4">          
            <h2 className="text-xl font-semibold">Transcript</h2>
            
            <div ref={scrollContainerRef} className="flex-1 overflow-y-auto pr-2">
              {eventLog.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>Start a conversation to see the transcript.</p>
                </div>
              ) : (
                <SidePanel events={eventLog} />
              )}
            </div>
          </div>

        </div>
      </div>

      <footer className="w-full p-4 flex justify-center items-center gap-4 bg-gray-900 border-t border-gray-700">
        {!isStreaming && !isConnecting ? (
          <>
            <button
              onClick={() => setShowSourceModal(true)}
              className="p-4 bg-gray-700 hover:bg-gray-600 rounded-full text-white transition-all"
              aria-label="Start recording"
            >
              <Mic className="w-6 h-6" />
            </button>
            <span className="text-gray-400">
              Click the icon to start recording
            </span>
          </>
        ) : (
          <>
            <button
              onClick={handleStopStream}
              className="p-4 bg-red-600 hover:bg-red-700 rounded-full text-white transition-all"
              aria-label="Stop recording"
            >
              <X className="w-6 h-6" />
            </button>
            <span className="text-gray-400">
              {isConnecting ? "Connecting..." : "Recording in progress..."}
            </span>
          </>
        )}
      </footer>
    </main>
  );
}