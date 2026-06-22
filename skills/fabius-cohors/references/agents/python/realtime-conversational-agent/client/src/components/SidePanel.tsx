import React from 'react';
import { Bot, User, Code, Terminal } from 'lucide-react';

type EventPart = {
  type: 'text' | 'audio/pcm' | 'function_call' | 'function_response';
  data: any;
};

type TranscriptionData = {
  text: string;
  is_final: boolean;
};

export type StructuredAgentEvent = {
  id: string;
  author: string;
  is_partial: boolean;
  turn_complete: boolean;
  parts: EventPart[];
  input_transcription?: TranscriptionData | null;
  output_transcription?: TranscriptionData | null;
  interrupted?: boolean | null;
};

type SidePanelProps = {
  events: StructuredAgentEvent[];
};

const EventPartCard: React.FC<{ part: EventPart; author: string }> = ({ part, author }) => {
  const isAgent = author !== 'user';

  switch (part.type) {
    case 'text':
      return (
        <div className={`text-sm ${isAgent ? 'text-gray-200' : 'text-white font-medium'}`}>
          {part.data}
        </div>
      );
    case 'function_call':
      return (
        <details className="mt-2 bg-gray-900 rounded p-2 text-xs cursor-pointer">
          <summary className="font-medium text-yellow-400 flex items-center gap-2">
            <Code className="w-4 h-4" />
            Function Call: <span className="text-yellow-200">{part.data.name}</span>
          </summary>
          <pre className="mt-2 p-2 bg-black rounded overflow-x-auto text-gray-300">
            {JSON.stringify(part.data.args, null, 2)}
          </pre>
        </details>
      );
    case 'function_response':
      return (
        <details className="mt-2 bg-gray-900 rounded p-2 text-xs cursor-pointer">
          <summary className="font-medium text-purple-400 flex items-center gap-2">
            <Terminal className="w-4 h-4" />
            Function Response: <span className="text-purple-200">{part.data.name}</span>
          </summary>
          <pre className="mt-2 p-2 bg-black rounded overflow-x-auto text-gray-300">
            {JSON.stringify(part.data.response, null, 2)}
          </pre>
        </details>
      );
    default:
      return null;
  }
};

export const SidePanel: React.FC<SidePanelProps> = ({ events }) => {
  return (
    <div className="space-y-4">
      {events.map((event) => (
        <div key={event.id} className="flex gap-3">
          
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            event.author === 'user' ? 'bg-blue-600' : 'bg-gray-700'
          }`}>
            {event.author === 'user' ? (
              <User className="w-5 h-5" />
            ) : (
              <Bot className="w-5 h-5" />
            )}
          </div>

          <div className="flex-1 bg-gray-800 rounded-lg p-3 space-y-2">
            <span className="text-sm font-semibold capitalize text-white">
              {event.author}
            </span>
            {event.parts.map((part, pIndex) => (
              <EventPartCard key={pIndex} part={part} author={event.author} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};