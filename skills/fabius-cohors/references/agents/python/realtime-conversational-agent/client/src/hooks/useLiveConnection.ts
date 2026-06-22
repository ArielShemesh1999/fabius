import { useState, useRef, useCallback } from "react";
import { arrayBufferToBase64, base64ToArray } from "@/utils/encoding";
import { StructuredAgentEvent } from "@/components/SidePanel";

const RECORDER_WORKLET_PATH = "/audio-recorder-worklet.js";
const PLAYER_WORKLET_PATH = "/audio-player-worklet.js";

type ConnectionState = "idle" | "connecting" | "connected" | "closing" | "closed" | "error";
const FRAME_CAPTURE_INTERVAL_MS = 250; 

export function useLiveConnection() {
  const [connectionState, setConnectionState] = useState<ConnectionState>("idle");
  const [latestTextMessage, setLatestTextMessage] = useState<string | null>(null);
  const [eventLog, setEventLog] = useState<StructuredAgentEvent[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const canvasElementRef = useRef<HTMLCanvasElement | null>(null);
  const videoLoopRef = useRef<NodeJS.Timeout | null>(null);

  const audioPlayerContextRef = useRef<AudioContext | null>(null);
  const audioPlayerNodeRef = useRef<AudioWorkletNode | null>(null);
  
  const audioRecorderContextRef = useRef<AudioContext | null>(null);
  const audioRecorderNodeRef = useRef<AudioWorkletNode | null>(null);

  const sendMessage = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const startVideoFrameCapture = useCallback(() => {
    if (videoLoopRef.current) clearInterval(videoLoopRef.current);

    videoLoopRef.current = setInterval(() => {
      const video = videoElementRef.current;
      const canvas = canvasElementRef.current;
      if (!video || !canvas || video.readyState < video.HAVE_METADATA) {
        return;
      }
      const { videoWidth, videoHeight } = video;
      canvas.width = videoWidth;
      canvas.height = videoHeight;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.drawImage(video, 0, 0, videoWidth, videoHeight);
      const frameDataUrl = canvas.toDataURL("image/jpeg", 0.8);
      const base64Data = frameDataUrl.split(",")[1];
      sendMessage({
        mime_type: "image/jpeg",
        data: base64Data,
      });
    }, FRAME_CAPTURE_INTERVAL_MS);
  }, [sendMessage]);

  const stopVideoFrameCapture = useCallback(() => {
    if (videoLoopRef.current) {
      clearInterval(videoLoopRef.current);
      videoLoopRef.current = null;
    }
  }, []);

  const sendTextMessage = useCallback((text: string) => {
    if (!text || text.trim() === "") return;
    
    sendMessage({
      "mime_type": "text/plain",
      "data": text
    });

    const userEvent: StructuredAgentEvent = {
      id: crypto.randomUUID(),
      author: 'user',
      is_partial: false,
      turn_complete: true,
      parts: [{ type: 'text', data: text }]
    };
    setEventLog((prevLog) => [...prevLog, userEvent]);

  }, [sendMessage]);

  const setupAudioRecording = useCallback(
    async (stream: MediaStream) => {
      const recorderContextOptions = {
        sampleRate: 16000
      };

      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0) {
        console.warn("No audio tracks found in the stream. Skipping audio recording setup.");
        return;
      }

      if (!audioRecorderContextRef.current) {
        audioRecorderContextRef.current = new AudioContext(recorderContextOptions);
      }
      const audioCtx = audioRecorderContextRef.current;
      
      if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
      }

      try {
        await audioCtx.audioWorklet.addModule(RECORDER_WORKLET_PATH);
      } catch (e) {
        console.error("Error adding audio recorder worklet module", e);
        return;
      }
      
      const micSourceNode = audioCtx.createMediaStreamSource(stream);
      const workletNode = new AudioWorkletNode(audioCtx, "audio-recorder-processor");

      workletNode.port.onmessage = (event) => {
        if (event.data.type === 'audio_data') {
          const pcmDataBuffer = event.data.buffer;
          const base64Data = arrayBufferToBase64(pcmDataBuffer);
          sendMessage({
            mime_type: "audio/pcm",
            data: base64Data,
          });
        } else if (event.data.type === 'speech_start') {
          audioPlayerNodeRef.current?.port.postMessage({ type: 'flush' });
        }
      };

      micSourceNode.connect(workletNode);
      audioRecorderNodeRef.current = workletNode;
      console.log("Audio recorder worklet setup complete.");
    },
    [sendMessage]
  );

  const setupAudioPlayback = useCallback(async () => {
    const playerContextOptions = {
      sampleRate: 24000
    };

    if (!audioPlayerContextRef.current) {
      audioPlayerContextRef.current = new AudioContext(playerContextOptions);
    }
    const audioCtx = audioPlayerContextRef.current;

    if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
    }

    try {
      await audioCtx.audioWorklet.addModule(PLAYER_WORKLET_PATH);
      const playerNode = new AudioWorkletNode(audioCtx, "audio-player-processor");
      playerNode.connect(audioCtx.destination);
      audioPlayerNodeRef.current = playerNode;
      console.log("Audio player worklet setup complete.");
    } catch (error) {
      console.error("Error setting up audio player worklet:", error);
    }
  }, []);

  const connect = useCallback(
    async (
      videoEl: HTMLVideoElement,
      canvasEl: HTMLCanvasElement,
      userId: string,
      source: 'camera' | 'screen'
    ) => {
      setConnectionState("connecting");
      setLatestTextMessage(null);
      setEventLog([]);
      videoElementRef.current = videoEl;
      canvasElementRef.current = canvasEl;

      try {
        let stream: MediaStream;

        if (source === 'screen') {
          const screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: { width: 1280, height: 720 },
            audio: false,
          });

          let micStream: MediaStream | null = null;
          try {
            micStream = await navigator.mediaDevices.getUserMedia({
              audio: true,
              video: false,
            });
          } catch (micErr) {
            console.error("Could not get microphone audio:", micErr);
          }

          if (micStream && micStream.getAudioTracks().length > 0) {
            stream = new MediaStream([
              ...screenStream.getVideoTracks(),
              ...micStream.getAudioTracks(),
            ]);
          } else {
            stream = screenStream;
          }

        } else {
          stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: { width: 1280, height: 720 },
          });
        }

        mediaStreamRef.current = stream;
        videoEl.srcObject = stream;
        videoEl.play();

        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${userId}?is_audio=true`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("WebSocket connection opened.");
          setConnectionState("connected");
          setupAudioRecording(stream);
          setupAudioPlayback();
          startVideoFrameCapture();
        };

        ws.onmessage = (event) => {
          const agentEvent = JSON.parse(event.data) as StructuredAgentEvent;
          
          for (const part of agentEvent.parts) {
            if (part.type === "audio/pcm") {
              const audioDataBytes = base64ToArray(part.data);
              audioPlayerNodeRef.current?.port.postMessage(
                { type: 'audio_data', buffer: audioDataBytes.buffer }, 
                [audioDataBytes.buffer]
              );
            }
          }

          if (agentEvent.output_transcription) {
            setLatestTextMessage(agentEvent.output_transcription.text);
          }

          if (agentEvent.input_transcription && agentEvent.input_transcription.is_final) {
            const finalUserEvent: StructuredAgentEvent = {
              id: crypto.randomUUID(),
              author: 'user',
              is_partial: false,
              turn_complete: true,
              parts: [{ 
                type: 'text', 
                data: agentEvent.input_transcription.text 
              }],
            };
            setEventLog((prevLog) => [...prevLog, finalUserEvent]);
          }

          const finalParts = agentEvent.parts.filter(
            p => p.type === 'text' || p.type === 'function_call' || p.type === 'function_response'
          );

          if (finalParts.length > 0 && !agentEvent.is_partial) {
            const finalAgentEvent: StructuredAgentEvent = {
              id: crypto.randomUUID(),
              author: 'agent',
              is_partial: false, 
              turn_complete: agentEvent.turn_complete, 
              parts: finalParts,
            };
            setEventLog((prevLog) => [...prevLog, finalAgentEvent]);
          }

          if (agentEvent.turn_complete) {
            setLatestTextMessage(null);
          }
        };

        ws.onclose = () => {
          console.log("WebSocket connection closed.");
          disconnect();
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          setConnectionState("error");
          disconnect();
        };
      } catch (error) {
        console.error("Failed to get user media:", error);
        setConnectionState("error");
      }
    },
    [connectionState, setupAudioRecording, startVideoFrameCapture, setupAudioPlayback]
  );

  const disconnect = useCallback(() => {
    setConnectionState("closing");
    
    wsRef.current?.close();
    wsRef.current = null;

    stopVideoFrameCapture();

    audioRecorderContextRef.current?.close();
    audioRecorderNodeRef.current?.port.close();
    audioRecorderContextRef.current = null;
    audioRecorderNodeRef.current = null;
    
    audioPlayerContextRef.current?.close();
    audioPlayerNodeRef.current?.port.close();
    audioPlayerContextRef.current = null;
    audioPlayerNodeRef.current = null;

    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    mediaStreamRef.current = null;

    if (videoElementRef.current) {
      videoElementRef.current.srcObject = null;
    }
    
    setConnectionState("closed");
    console.log("Disconnected and cleaned up all resources.");
  }, [stopVideoFrameCapture]);

  return {
    connectionState,
    latestTextMessage,
    eventLog,
    connect,
    disconnect,
    sendTextMessage
  };
}