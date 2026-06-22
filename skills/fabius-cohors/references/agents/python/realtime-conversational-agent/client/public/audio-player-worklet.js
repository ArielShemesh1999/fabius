/**
 * An AudioWorkletProcessor for playing back raw PCM audio chunks.
 *
 * It buffers incoming audio chunks and plays them out smoothly.
 * It includes a 'flush' command to clear the buffer, which is
 * essential for barge-in (stopping playback immediately).
 */
class AudioPlayerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.audioQueue = [];
    this.currentChunk = null;
    this.currentChunkIndex = 0;
    
    this.port.onmessage = (event) => {
      if (event.data.type === 'audio_data') {
        // Add new audio data to our buffer
        const pcmData = new Int16Array(event.data.buffer);
        this.audioQueue.push(pcmData);
      } else if (event.data.type === 'flush') {
        // --- THIS IS THE CRITICAL BARGE-IN LOGIC ---
        // Clear the buffer immediately
        this.audioQueue = [];
        this.currentChunk = null;
        this.currentChunkIndex = 0;
        console.log("Audio player flushed.");
      }
    };
  }

  process(inputs, outputs, parameters) {
    const outputChannel = outputs[0][0];

    for (let i = 0; i < outputChannel.length; i++) {
      if (!this.currentChunk || this.currentChunkIndex >= this.currentChunk.length) {
        if (this.audioQueue.length > 0) {
          this.currentChunk = this.audioQueue.shift();
          this.currentChunkIndex = 0;
        } else {
          outputChannel[i] = 0;
          continue;
        }
      }

      const sample = this.currentChunk[this.currentChunkIndex];
      outputChannel[i] = sample / 32768.0;
      this.currentChunkIndex++;
    }

    return true;
  }
}

registerProcessor("audio-player-processor", AudioPlayerProcessor);

