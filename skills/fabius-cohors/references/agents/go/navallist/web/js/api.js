// api.js - API Wrapper for Navallist Backend

const API_BASE = '/api';
const AGENT_APP_NAME = 'navallist_agent'; // Must match Config.Name in agent.go

export const api = {
    
    // Create or Join a Session (New Trip API)
    async createTrip(sessionId, userId, tripType) {
        // userId might be redundant if cookie is set, but we pass it logic-wise
        const res = await fetch(`${API_BASE}/trips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId, 
                captain_name: userId,
                trip_type: tripType
            })
        });
        if (!res.ok) {
            const err = new Error("Failed to create/join trip");
            err.status = res.status;
            throw err;
        }
        return await res.json();
    },

    // List User Trips
    async getUserTrips() {
        const res = await fetch(`${API_BASE}/trips`);
        if (!res.ok) throw new Error("Failed to list trips");
        return await res.json();
    },

    // Update User Profile
    async updateUser(name) {
        const res = await fetch('/auth/me', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!res.ok) throw new Error("Failed to update user");
    },

    // Create or Join a Session (Legacy / Agent Sync)
    async createSession(sessionId, userId, displayName) {
        try {
            const url = `${API_BASE}/agent/sessions`;
            
            // Explicitly create session to ensure it exists
            const res = await fetch(url, {
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    session_id: sessionId, 
                    user_id: userId,
                    display_name: displayName
                }) 
            });

            if (!res.ok && res.status !== 409) { // 409 = Already exists, which is fine
                 console.warn("Session creation status:", res.status);
            }
        } catch (e) {
            console.error("Failed to create session:", e);
        }
        return { sessionId, userId };
    },

    // Get current state of the trip (Polling)
    async getSession(sessionId, userId) {
        try {
            const encSession = encodeURIComponent(sessionId);
            const encUser = encodeURIComponent(userId);
            
            const url = `${API_BASE}/agent/sessions/${encSession}?userId=${encUser}`;
            
            const res = await fetch(url);
            if (res.status === 404) return null; // Session not created yet, that's fine
            if (!res.ok) throw new Error(`API Error: ${res.status}`);
            
            return await res.json();
        } catch (e) {
            console.warn("Polling info:", e.message);
            return null; 
        }
    },

    // Send an event (Text, Checkbox Toggle, or Multimodal)
    async sendInteraction(sessionId, userId, text, imageBlob = null, audioBlob = null) {
        
        // Construct ADK Event Payload (snake_case)
        // Endpoint: POST /api/run
        
        const payload = {
            app_name: AGENT_APP_NAME,
            session_id: sessionId,
            user_id: userId,
            new_message: {
                role: "user",
                parts: []
            }
        };

        // Add Text Part
        if (text) {
            payload.new_message.parts.push({ text: text });
        }

        // Add Image Part (if exists)
        if (imageBlob) {
            const base64 = await blobToBase64(imageBlob);
            payload.new_message.parts.push({
                inline_data: {
                    mime_type: imageBlob.type,
                    data: base64
                }
            });
        }
        
        // Add Audio Part (if exists)
        if (audioBlob) {
             console.log("Attaching audio blob", audioBlob.type, "size:", audioBlob.size);
             const base64 = await blobToBase64(audioBlob);
             payload.new_message.parts.push({
                inline_data: {
                    mime_type: audioBlob.type || 'audio/webm',
                    data: base64
                }
             });
        }

        try {
            const res = await fetch(`${API_BASE}/agent/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) {
                const txt = await res.text();
                let errData;
                try {
                    errData = JSON.parse(txt);
                } catch (e) {
                    // Not JSON
                }
                
                const err = new Error(errData ? errData.error || txt : txt);
                err.status = res.status;
                err.data = errData; // Attach structured data
                throw err;
            }
            return await res.json(); // Returns events array
            
        } catch (e) {
            if (e.status) {
                console.error(`Send failed with status ${e.status}`, e);
            } else {
                console.error("Send failed", e);
            }
            throw e;
        }
    },

    // Update Trip Status
    async updateTripStatus(tripId, status) {
        // tripId is the Session ID in this app's context
        const res = await fetch(`${API_BASE}/trips/${tripId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (!res.ok) throw new Error("Failed to update status");
    },

    // Update Trip Type
    async updateTripType(tripId, tripType) {
        const res = await fetch(`${API_BASE}/trips/${tripId}/type`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trip_type: tripType })
        });
        if (!res.ok) throw new Error("Failed to update trip type");
    },

    // Get Trip Report
    async getTripReport(tripId) {
        const res = await fetch(`${API_BASE}/trips/${tripId}/report`);
        if (!res.ok) throw new Error("Failed to get report");
        return await res.json();
    },

    // Get Single Trip Details (Unified State)
    async getTrip(tripId, userId) {
        let url = `${API_BASE}/trips/${tripId}`;
        if (userId) {
            url += `?userId=${encodeURIComponent(userId)}`;
        }
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to get trip details");
        return await res.json();
    },

    // Delete a Trip
    async deleteTrip(tripId) {
        const res = await fetch(`${API_BASE}/trips/${tripId}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error("Failed to delete trip");
    },

    // Update Checklist Item (Direct)
    async updateChecklistItem(tripId, itemId, isChecked, value = null, completedByName = "", assignedToUserId = null, assignedToName = null) {
        const payload = {
            is_checked: isChecked,
            location: "",
            value: "",
            completed_by_name: completedByName,
            assigned_to_user_id: assignedToUserId,
            assigned_to_name: assignedToName
        };
        
        // Simple heuristic: if value is provided, send it. 
        // If it's a checkbox, value might be empty.
        if (value !== null && value !== undefined) {
            payload.value = String(value);
            payload.location = String(value); // Redundant but safe for backend logic
        }

        const encodedItemId = encodeURIComponent(itemId);
        const res = await fetch(`${API_BASE}/trips/${tripId}/items/${encodedItemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error("Failed to update item");
        return await res.json();
    },

    // Upload Item Photo (Direct)
    async uploadItemPhoto(tripId, itemId, fileBlob) {
        const formData = new FormData();
        formData.append('file', fileBlob);

        const encodedItemId = encodeURIComponent(itemId);
        const res = await fetch(`${API_BASE}/trips/${tripId}/items/${encodedItemId}/photo`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error("Failed to upload photo");
        return await res.json();
    }
};

// Helper: Blob to Base64 (strip data: prefix for Gemini)
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            // reader.result is "data:image/jpeg;base64,....."
            // We need just the comma-separated part
            const base64String = reader.result.split(',')[1];
            resolve(base64String);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}