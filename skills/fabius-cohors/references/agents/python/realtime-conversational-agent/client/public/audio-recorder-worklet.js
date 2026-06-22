/**
 * An AudioWorkletProcessor for recording audio and sending it to the main
 * thread. It also performs simple Voice Activity Detection (VAD) to
 * signal when speech has started, enabling barge-in.
 */
class AudioRecorderProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    // VAD parameters
    this.energyThreshold = 0.00125; // Sensitivity for speech detection
    this.speechDuration = 0.2;   // Min duration (in sec) to count as speech
    this.silenceDuration = 0.5;  // Max duration (in sec) of silence to stop "speech"
    
    this.speechFrames = 0;
    this.silenceFrames = 0;
    this.isSpeaking = false;
    this.sampleRate = 16000;
  }

  /**
   * Calculates the Root Mean Square (RMS) energy of an audio buffer.
   * @param {Float32Array} pcmData - The audio buffer.
   * @returns {number} - The energy level.
   */
  calculateEnergy(pcmData) {
    let sum = 0;
    for (let i = 0; i < pcmData.length; i++) {
      sum += pcmData[i] * pcmData[i];
    }
    return Math.sqrt(sum / pcmData.length);
  }

  process(inputs, outputs, parameters) {
    const inputChannel = inputs[0][0];

    if (!inputChannel) {
      return true;
    }

    const energy = this.calculateEnergy(inputChannel);
    const frameDuration = inputChannel.length / this.sampleRate;

    if (energy > this.energyThreshold) {
      this.speechFrames += frameDuration;
      this.silenceFrames = 0;
      if (this.speechFrames > this.speechDuration && !this.isSpeaking) {
        this.isSpeaking = true;
        this.port.postMessage({ type: 'speech_start' });
      }
    } else {
      this.silenceFrames += frameDuration;
      if (this.silenceFrames > this.silenceDuration && this.isSpeaking) {
        this.isSpeaking = false;
        this.speechFrames = 0;
      }
    }

    const pcmData = new Int16Array(inputChannel.length);
    for (let i = 0; i < inputChannel.length; i++) {
      const s = Math.max(-1, Math.min(1, inputChannel[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    this.port.postMessage(
      { type: 'audio_data', buffer: pcmData.buffer }, 
      [pcmData.buffer]
    );
    
    return true;
  }
}

registerProcessor("audio-recorder-processor", AudioRecorderProcessor);

