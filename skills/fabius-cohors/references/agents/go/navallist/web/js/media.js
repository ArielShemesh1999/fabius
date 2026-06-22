// media.js - Camera & Audio Handling

export const media = {
    
    // --- Camera ---
    
    // Trigger the hidden file input
    capturePhoto(callback) {
        const input = document.getElementById('camera-input');
        
        // Remove old listener to avoid dupes
        input.onchange = null; 
        
        input.onchange = (e) => {
            if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                // Optional: Resize image here before sending to save bandwidth
                callback(file);
            }
        };
        
        input.click();
    },


    // --- Audio ---
    
    mediaRecorder: null,
    audioChunks: [],

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.start();
            return true;
        } catch (e) {
            console.error("Mic access denied", e);
            alert("Microphone access required for voice commands.");
            return false;
        }
    },

    stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder) return resolve(null);

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' }); // Chrome/Android standard
                resolve(audioBlob);
                
                // Cleanup
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                this.mediaRecorder = null;
            };

            this.mediaRecorder.stop();
        });
    }
};
