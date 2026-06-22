import { api } from './api.js';
import { ui } from './ui.js';
import { media } from './media.js';
import { checkAuth } from './auth.js';
import { generateTripName } from './naming.js';
import { CHECKLIST_SCHEMA } from './checklist_data.js';
import { subscribeTrip, disconnectRealtime } from './realtime.js';

// --- State ---
const state = {
    sessionId: null, // ADK Session ID (e.g. Salty_Crab_42)
    tripId: null,    // Database PK (e.g. random_shortkey)
    userId: null,    // Identity ID (UUID or guest_name)
    displayName: null, // Human-friendly name
    pollingInterval: null,
    completionModalShown: false,
    autoReportShown: false,
    currentStatus: 'Draft'
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
    // Check Auth
    const user = await checkAuth();
    
    // 0. Set Default Session ID (Random Nautical Name or URL Param)
    const sessionIdInput = document.getElementById('session-id');
    const userIdInput = document.getElementById('user-id');
    
    // Load saved name if not logged in
    if (!user && userIdInput) {
        const savedName = localStorage.getItem('navallist_user_name');
        if (savedName) {
            userIdInput.value = savedName;
        }
    }

    const urlParams = new URLSearchParams(window.location.search);
    const sessionFromUrl = urlParams.get('session');

    if (sessionIdInput) {
        if (sessionFromUrl) {
            sessionIdInput.value = sessionFromUrl;
        } else {
            sessionIdInput.value = generateTripName();
        }
    }

    // Auto-login if we have session and user name
    if (sessionFromUrl) {
        let uid = user ? user.id : userIdInput.value.trim();
        let name = user ? user.name : userIdInput.value.trim();
        if (uid) {
            await startApp(sessionFromUrl, uid, name);
        }
    }

    // 1. Setup Login Form
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const sid = document.getElementById('session-id').value.trim();
        const uid = document.getElementById('user-id').value.trim();
        
        // Save name for next time
        if (uid) {
            localStorage.setItem('navallist_user_name', uid);
            
            // If logged in (cookie exists), update the backend user record with this name
            // We can check if 'user' object from checkAuth exists, but it might be stale scope.
            // Best to try updating if we suspect we are logged in.
            // Or verify via checkAuth again? Overkill.
            // Just try it. If 401, ignored.
            try {
                await api.updateUser(uid);
            } catch (err) {
                // Ignore if not logged in
            }
        }

        if (sid && uid) {
            await startApp(sid, uid, uid); // Default type handled in startApp
        }
    });

    // 2. Setup Globals for UI Calls - REMOVED

    // 3. Setup Voice FAB
    setupVoiceFab();

    // 4. Setup Header Controls
    setupControls();
    
    // 5. Connection Status Listener
    document.addEventListener('connection-status', (e) => {
        ui.updateConnectionStatus(e.detail.status);
    });

    // 6. Photo Viewer
    let currentPhotoIndex = 0;
    let currentPhotoList = [];

    const viewPhoto = (artifactPathOrList) => {
        const dialog = document.getElementById('photo-dialog');
        const img = document.getElementById('photo-viewer');
        const loading = document.getElementById('photo-loading');
        const nextBtn = document.getElementById('photo-next');
        const prevBtn = document.getElementById('photo-prev');
        const counter = document.getElementById('photo-counter');
        
        // Determine if it's a single path or a list
        if (Array.isArray(artifactPathOrList)) {
            currentPhotoList = artifactPathOrList;
            currentPhotoIndex = 0;
        } else {
            currentPhotoList = [artifactPathOrList];
            currentPhotoIndex = 0;
        }

        const loadPhoto = (index) => {
            if (index < 0 || index >= currentPhotoList.length) return;
            currentPhotoIndex = index;
            
            const path = currentPhotoList[currentPhotoIndex];
            const params = new URLSearchParams({
                app: 'navallist_agent',
                user: state.userId,
                session: state.sessionId,
                path: path
            });
            const url = `/api/artifacts?${params.toString()}`;

            img.style.display = 'none';
            loading.style.display = 'block';
            img.src = url;
            
            img.onload = () => {
                loading.style.display = 'none';
                img.style.display = 'block';
            };

            // Update UI
            if (currentPhotoList.length > 1) {
                nextBtn.classList.remove('hidden');
                prevBtn.classList.remove('hidden');
                counter.classList.remove('hidden');
                counter.innerText = `${currentPhotoIndex + 1} / ${currentPhotoList.length}`;
            } else {
                nextBtn.classList.add('hidden');
                prevBtn.classList.add('hidden');
                counter.classList.add('hidden');
            }
        };

        // Setup Buttons
        nextBtn.onclick = (e) => {
            e.stopPropagation();
            if (currentPhotoIndex < currentPhotoList.length - 1) {
                loadPhoto(currentPhotoIndex + 1);
            } else {
                loadPhoto(0); // Wrap around
            }
        };

        prevBtn.onclick = (e) => {
             e.stopPropagation();
             if (currentPhotoIndex > 0) {
                 loadPhoto(currentPhotoIndex - 1);
             } else {
                 loadPhoto(currentPhotoList.length - 1); // Wrap around
             }
        };

        loadPhoto(0);
        dialog.showModal();
    };

    document.getElementById('close-photo').addEventListener('click', () => {
        document.getElementById('photo-dialog').close();
    });

    // 2. Setup Event Delegation (Moved here to use viewPhoto)
    setupEventDelegation(viewPhoto);


    // 6. Global Delete Trip Listener
    document.addEventListener('delete-trip', async (e) => {
        const tripId = e.detail.tripId;
        try {
            await api.deleteTrip(tripId);
            // Refresh list
            checkAuth(); // This triggers list reload inside auth logic usually, or we call list directly
            // Actually checkAuth calls fetchUserTrips if logged in.
        } catch (err) {
            console.error(err);
            alert("Failed to delete trip.");
        }
    });
});

// --- Core Workflow ---

// Scoped poll timeout for debounce
let pollTimeout;

function schedulePollState(delay = 300) {
    if (pollTimeout) clearTimeout(pollTimeout);
    pollTimeout = setTimeout(() => {
        pollState();
    }, delay);
}

async function startApp(sessionId, userId, displayName = null, tripType = 'Departing') {
    // Determine Identity vs Display Name
    // userId passed from form is the human name typed by user
    // checkAuth() at startup populated 'user' if logged in
    const authUser = await checkAuth(); 
    
    state.sessionId = sessionId;
    state.displayName = displayName || userId; 
    state.userId = authUser ? authUser.id : "guest_" + userId;
    
    state.tripType = tripType; // Store in state
    state.completionModalShown = false;
    state.autoReportShown = false;
    state.currentStatus = 'Draft';

    // UI Transition
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('dashboard-screen').classList.remove('hidden');
    document.getElementById('voice-bar-root').classList.remove('hidden');
    document.getElementById('trip-title').innerText = sessionId; // Initial value
    
    // Init Checklist UI
    ui.init('checklist-container', 'category-tabs');
    // Enable Swipe Navigation
    ui.setupSwipeHandlers('checklist-container');

    // Tell UI about the trip type for help text
    ui.setTripType(tripType);

    // Register Session
    // 1. Backend DB (for persistence & listing)
    try {
        const trip = await api.createTrip(sessionId, displayName || userId, tripType);
        state.tripId = trip.id; // Store DB ID for polling
        
        // If joining an existing trip, update our local type to match DB
        if (trip.trip_type && trip.trip_type !== tripType) {
            state.tripType = trip.trip_type;
            ui.setTripType(trip.trip_type);
        }

        ui.updateHeaderTitle(sessionId, trip.boat_name);
    } catch (e) {
        console.error("Failed to create/join trip in DB:", e);
        if (e.status === 401) {
            alert("Login required to create a new trip. You can only join existing trips anonymously.");
        } else {
            alert("Failed to join trip: " + e.message);
        }
        
        // Reset UI back to login screen
        setTimeout(() => {
            document.getElementById('dashboard-screen').classList.add('hidden');
            document.getElementById('voice-bar-root').classList.add('hidden');
            document.getElementById('login-screen').classList.remove('hidden');
            
            // Clean URL
            const url = new URL(window.location.href);
            url.searchParams.delete('session');
            window.history.pushState({}, '', url);
        }, 300);
        return;
    }

    // 2. Agent Service (for logic)
    await api.createSession(sessionId, userId, state.displayName);

    // Start Realtime Subscription (replaces polling)
    // Initial fetch
    await pollState();
    
    // Subscribe to updates
    subscribeTrip(state.tripId, (event) => {
        console.log("Received update, refreshing state...", event);
        // Debounce polling to avoid flood
        schedulePollState(300);
    }, (type, data) => {
        ui.updatePresence(type, data);
    }, state.displayName); // Pass clean human name
}

async function pollState() {
    if (!state.tripId) return;

    let combinedState = {};
    let currentTrip = null;
    let currentReportItems = null;

    try {
        // 1. Fetch Unified State (Metadata + Items + Agent State)
        const unified = await api.getTrip(state.tripId, state.userId);
        if (!unified) return;

        const trip = unified.trip;
        const items = unified.items;
        const agentState = unified.agent_state;

        // 2. Process Metadata
        if (trip) {
            currentTrip = trip;
            ui.updateHeaderTitle(state.sessionId, trip.boat_name);
            if (trip.status) {
                state.currentStatus = trip.status;
                updateStatusUI(trip.status);

                // If status is NOT Draft (e.g., Ready/Completed), close the completion modal if open
                if (trip.status !== 'Draft') {
                    const dialog = document.getElementById('completion-dialog');
                    if (dialog && dialog.open) {
                        dialog.close();
                        state.completionModalShown = false;
                    }
                }
            }
            if (trip.trip_type && trip.trip_type !== state.tripType) {
                state.tripType = trip.trip_type;
                ui.setTripType(state.tripType);
                updateTypeUI(state.tripType);
            }
            
            // Inject boat_name into state for the form input
            if (trip.boat_name) combinedState['boat_name'] = trip.boat_name;
        }

        // 3. Process Agent State (Agent's view of the world)
        if (agentState) {
            combinedState = { ...combinedState, ...agentState };
        }

        // 4. Process Checklist Items (The Truth)
        if (items && Array.isArray(items)) {
            currentReportItems = items;
            // Update Report UI if open
            const reportDialog = document.getElementById('report-dialog');
            if (reportDialog && reportDialog.open) {
                ui.renderReportContent(items, trip);
            }

            // Convert DB Rows to State Map: { "Slip": "Value", "Oil": true }
            items.forEach(item => {
                // Map Name -> Value
                combinedState[item.name] = item.is_checked;

                // If it has a value/location, that takes precedence as the "val" for inputs
                const hasValue = item.location_text !== null && item.location_text !== undefined && item.location_text !== "";
                if (hasValue) {
                    combinedState[item.name] = item.location_text;
                    combinedState[`${item.name}_location`] = item.location_text;
                }

                if (item.photos && item.photos.length > 0) {
                     combinedState[`${item.name}_photos`] = item.photos;
                }
                
                // Assignment
                if (item.assigned_to_name) {
                    combinedState[`${item.name}_assigned_to_name`] = item.assigned_to_name;
                }
                if (item.assigned_to_user_id) {
                     combinedState[`${item.name}_assigned_to_user_id`] = item.assigned_to_user_id;
                }
            });
        }

        // 5. Update UI with merged state
        ui.updateState(combinedState, state.userId, state.displayName);

        // 6. Check for Completion
        checkTripCompletion(combinedState, currentTrip, currentReportItems, state);

    } catch (e) {
        console.warn("Poll Unified State failed:", e);
    }
}

export function checkTripCompletion(combinedState, trip, reportItems, appState) {
    let totalItems = 0;
    let completedItems = 0;

    Object.values(CHECKLIST_SCHEMA).forEach(categoryItems => {
        categoryItems.forEach(item => {
            totalItems++;
            const val = combinedState[item.id] || combinedState[item.label];
            if (val !== undefined) {
                if (typeof val === 'boolean') {
                    if (val === true) completedItems++;
                } else if (val && String(val).trim() !== "") {
                    completedItems++;
                }
            }
        });
    });

    if (totalItems > 0 && completedItems === totalItems) {
        let shownAnything = false;

        // Auto-Open Report if "Hide Checked" is ON and we haven't shown it yet
        if (ui.hideChecked && !appState.autoReportShown && trip && reportItems) {
            appState.autoReportShown = true;
            ui.renderReport(reportItems, trip);
            shownAnything = true;
        }

        if (appState.currentStatus === 'Draft' && !appState.completionModalShown) {
            appState.completionModalShown = true;
            document.getElementById('completion-dialog').showModal();
            shownAnything = true;
        }

        if (shownAnything) {
            document.getElementById('voice-bar-root').classList.add('hidden');
        }
    } else {
        console.log(`Completion Check: ${completedItems}/${totalItems} (Not done)`);
        // Reset if they uncheck something? 
        // User might want it to pop up again if they finish it again.
        appState.completionModalShown = false;
        // Don't reset autoReportShown here, otherwise it might annoyingly pop up again if they toggle one item.
        // Or maybe we should? "If all items are checked off...". 
        // If they uncheck and recheck, maybe they want to see it again? 
        // Let's reset it so the feature feels consistent.
        appState.autoReportShown = false;
    }
}

function updateStatusUI(status) {
    const select = document.getElementById('status-select');
    if (select) {
        select.value = status;
        
        // Update color class
        select.classList.remove('ready', 'departed', 'draft');
        select.classList.add(status.toLowerCase());
    }
}

function updateTypeUI(type) {
    const select = document.getElementById('type-select');
    if (select) {
        select.value = type;
    }
}

// --- Interaction Handlers ---

function setupEventDelegation(viewPhotoCallback) {
    const container = document.getElementById('checklist-container');
    const tripsList = document.getElementById('trips-list');
    
    // 1. Checklist Item Interactions
    container.addEventListener('click', (e) => {
        // Find closest button or actionable element
        const target = e.target.closest('button') || e.target.closest('.photo-icon-wrapper');
        if (!target) return;

        const action = target.dataset.action;
        if (!action) return;

        e.stopPropagation();

        if (action === 'camera') {
            handleCameraClick(target.dataset.itemId, target.dataset.label);
        } else if (action === 'assign') {
            const row = target.closest('.item-row');
            if (row) {
                // We need to pass the schema item to showAssignMenu, 
                // but ui.js doesn't export showAssignMenu directly for external use easily without context.
                // However, ui.showAssignMenu expects an item object {label: "..."}.
                // We can reconstruct enough context or expose a method in UI that takes ID/Label.
                ui.showAssignMenu({ id: target.dataset.assignId, label: target.dataset.label });
            }
        } else if (action === 'info') {
            // Similarly for help
             const itemSchema = Object.values(CHECKLIST_SCHEMA).flat().find(i => i.id === target.dataset.itemId);
             if (itemSchema) ui.showHelp(itemSchema);
        } else if (action === 'view-photos') {
            const filenames = JSON.parse(target.dataset.filenames || "[]");
            if (viewPhotoCallback) viewPhotoCallback(filenames);
        }
    });

    // 2. Checklist Input Changes
    container.addEventListener('change', (e) => {
        if (e.target.dataset.action === 'update-item') {
            const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
            handleItemUpdate(e.target.dataset.label, value);
        }
    });
    
    // 3. Trip List Interactions (Delegation)
    tripsList.addEventListener('click', (e) => {
        const delBtn = e.target.closest('.btn-delete-trip');
        if (delBtn) {
            e.stopPropagation();
            if (confirm(`Are you sure you want to delete "${delBtn.dataset.sessionId}"?`)) {
                const event = new CustomEvent('delete-trip', { detail: { tripId: delBtn.dataset.tripId } });
                document.dispatchEvent(event);
            }
            return;
        }
        
        const item = e.target.closest('.trip-list-item');
        if (item && item.dataset.action === 'select-trip') {
            const input = document.getElementById('session-id');
            if (input) {
                input.value = item.dataset.sessionId;
                document.getElementById('login-form').dispatchEvent(new Event('submit'));
            }
        }
    });

    // 4. Assignment Interaction (from Dialog)
    document.addEventListener('assignment-change', (e) => {
        handleAssignmentChange(e.detail.itemId, e.detail.userId, e.detail.userName);
    });
}

function setupControls() {
    // Status Change
    const statusSelect = document.getElementById('status-select');
    statusSelect.addEventListener('change', async (e) => {
        const newStatus = e.target.value;
        try {
            await api.updateTripStatus(state.tripId, newStatus);
            // Optimistic update
            updateStatusUI(newStatus);
        } catch (error) {
            console.error(error);
            alert("Failed to update status");
        }
    });

    // Type Change
    const typeSelect = document.getElementById('type-select');
    typeSelect.addEventListener('change', async (e) => {
        const newType = e.target.value;
        try {
            await api.updateTripType(state.tripId, newType);
            // Update local state immediately
            state.tripType = newType;
            ui.setTripType(newType);
            updateTypeUI(newType);
        } catch (error) {
            console.error(error);
            alert("Failed to update trip type");
            // Revert UI on error?
            updateTypeUI(state.tripType);
        }
    });

    // Report
    document.getElementById('btn-report').addEventListener('click', async () => {
        if (!state.tripId) {
            alert("Trip not fully initialized yet.");
            return;
        }
        try {
            const [report, trip] = await Promise.all([
                api.getTripReport(state.tripId),
                api.getTrip(state.tripId)
            ]);
            ui.renderReport(report, trip);
            document.getElementById('voice-bar-root').classList.add('hidden');
        } catch (error) {
            console.error(error);
            alert("Failed to load report");
        }
    });

    document.getElementById('close-report').addEventListener('click', () => {
        document.getElementById('report-dialog').close();
        // Only show voice bar if completion dialog is not open
        const compDialog = document.getElementById('completion-dialog');
        if (!compDialog || !compDialog.open) {
            document.getElementById('voice-bar-root').classList.remove('hidden');
        }
    });

    document.getElementById('report-dialog').addEventListener('cancel', () => {
        // Only show voice bar if completion dialog is not open
        const compDialog = document.getElementById('completion-dialog');
        if (!compDialog || !compDialog.open) {
            document.getElementById('voice-bar-root').classList.remove('hidden');
        }
    });

    // Share
    document.getElementById('btn-share').addEventListener('click', () => {
        const url = new URL(window.location.href);
        url.searchParams.set('session', state.sessionId);
        const shareUrl = url.toString();

        // 1. Setup UI
        const dialog = document.getElementById('share-dialog');
        const linkText = document.getElementById('share-link-text');
        const qrContainer = document.getElementById('qrcode');
        
        linkText.innerText = shareUrl;
        qrContainer.innerHTML = ''; // Clear previous

        // 2. Generate QR
        new QRCode(qrContainer, {
            text: shareUrl,
            width: 200,
            height: 200,
            colorDark : "#002b36",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H
        });

        dialog.showModal();
    });

    document.getElementById('close-share').addEventListener('click', () => {
        document.getElementById('share-dialog').close();
    });

    document.getElementById('copy-link-btn').addEventListener('click', () => {
        const link = document.getElementById('share-link-text').innerText;
        navigator.clipboard.writeText(link).then(() => {
            alert("Link copied!");
        });
    });

    // Settings
    document.getElementById('btn-settings').addEventListener('click', () => {
        document.getElementById('settings-dialog').showModal();
    });

    document.getElementById('close-settings').addEventListener('click', () => {
        document.getElementById('settings-dialog').close();
    });

    document.getElementById('close-help').addEventListener('click', () => {
        document.getElementById('help-dialog').close();
    });

    const hideCheckedToggle = document.getElementById('setting-hide-checked');
    hideCheckedToggle.checked = ui.hideChecked;
    hideCheckedToggle.addEventListener('change', (e) => {
        ui.toggleHideChecked(e.target.checked);
    });

    // Completion Dialog
    document.getElementById('btn-completion-cancel').addEventListener('click', () => {
        document.getElementById('completion-dialog').close();
        // Only show voice bar if report is not open
        const reportDialog = document.getElementById('report-dialog');
        if (!reportDialog || !reportDialog.open) {
            document.getElementById('voice-bar-root').classList.remove('hidden');
        }
    });

    document.getElementById('btn-completion-confirm').addEventListener('click', async () => {
        try {
            await api.updateTripStatus(state.tripId, 'Ready');
            updateStatusUI('Ready');
            document.getElementById('completion-dialog').close();
            // Only show voice bar if report is not open
            const reportDialog = document.getElementById('report-dialog');
            if (!reportDialog || !reportDialog.open) {
                document.getElementById('voice-bar-root').classList.remove('hidden');
            }
        } catch (error) {
            console.error(error);
            alert("Failed to update status");
        }
    });

    // Back / Exit
    document.getElementById('btn-back').addEventListener('click', () => {
        // 1. Stop Realtime
        disconnectRealtime();
        if (state.pollingInterval) {
            clearInterval(state.pollingInterval);
            state.pollingInterval = null;
        }

        // 2. Clear State (Keep userId)
        state.sessionId = null;
        state.tripId = null;

        // 3. Update UI
        document.getElementById('dashboard-screen').classList.add('hidden');
        document.getElementById('voice-bar-root').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');

        // 4. Clean URL (remove ?session=... if present so refresh doesn't auto-rejoin)
        const url = new URL(window.location.href);
        url.searchParams.delete('session');
        window.history.pushState({}, '', url);

        // 5. Refresh Trip List (if logged in)
        // We could call a function to refresh the list here if we moved logic out of auth.js/startup
    });
}

// 1. Checkbox / Input Change
async function handleItemUpdate(itemId, value) {
    console.log(`Update ${itemId}: ${value}`);
    
    let isCompleted = false;
    let isChecked = false;

    if (typeof value === 'boolean' || value === "true" || value === "false") {
        isChecked = (value === true || value === "true");
        isCompleted = isChecked;
    } else {
        // Text/Number input
        isCompleted = (value && String(value).trim() !== "");
        isChecked = isCompleted; // Mark as checked in DB if it has a value
    }

    // Optimistic UI Update for Visibility
    // We do this immediately so the user sees the "Hide" effect
    if (ui.hideChecked) {
        // Find all rows for this item (could be in category and My Items)
        const itemSchema = Object.values(CHECKLIST_SCHEMA).flat().find(i => i.label === itemId || i.id === itemId);
        const rows = document.querySelectorAll(`.item-row[data-id="${itemSchema ? itemSchema.id : itemId}"]`);
        
        rows.forEach(row => {
            if (isCompleted) {
                row.classList.add('checked');
                // Only fade if it was not already hidden and NOT allowing multi photo
                if (!itemSchema || !itemSchema.allow_multi_photo) {
                    if (!row.classList.contains('hidden') && !row.classList.contains('fading-out')) {
                        // Delay hiding: wait 1s, then fade for 1s
                        setTimeout(() => {
                            row.classList.add('fading-out');
                            setTimeout(() => {
                                row.classList.add('hidden');
                                row.classList.remove('fading-out');
                                ui.updateTabVisibility();
                            }, 1000); // Wait for transition duration
                        }, 1000); // Hold for 1s
                    }
                }
            } else {
                row.classList.remove('checked');
                row.classList.remove('hidden');
                row.classList.remove('fading-out');
                ui.updateTabVisibility();
            }
        });
    }

    // 1. Direct DB Update (Reliable CRUD)
    if (state.tripId) {
        try {
            // If it's not a boolean, assume it's a value/text update
            const textVal = (typeof value !== 'boolean') ? value : "";
            
            await api.updateChecklistItem(state.tripId, itemId, isChecked, textVal, state.displayName);
            
            // Trigger state poll manually to be robust against lost realtime messages
            schedulePollState(500); 

        } catch (e) {
            console.error("Direct update failed:", e);
            // Don't alert yet, maybe Agent path works?
        }
    }

    // 2. Notify Agent (for context/reasoning/logs)
    const text = `I have updated item "${itemId}" to: ${value}`;
    
    // Fire & Forget (mostly) - The Realtime subscription will handle UI synchronization if needed
    try {
        await api.sendInteraction(state.sessionId, state.displayName, text);
    } catch (e) {
        console.warn("Failed to sync update to agent. Check connection.");
    }
}

// 2. Camera Click
function handleCameraClick(itemId, itemName) {
    media.capturePhoto(async (fileBlob) => {
        // Show loading/uploading state?
        console.log(`Uploading photo for ${itemName}`);
        ui.showToast("Uploading photo...", "info");
        
        try {
            await api.uploadItemPhoto(state.tripId, itemName, fileBlob);
            ui.showToast("Photo uploaded!", "success");

            // Auto-increment count if applicable
            const itemSchema = Object.values(CHECKLIST_SCHEMA).flat().find(i => i.id === itemId);
            if (itemSchema && itemSchema.type === 'count') {
                const input = document.querySelector(`input[data-input-id="${itemId}"]`);
                let val = 0;
                if (input) {
                     val = parseInt(input.value) || 0;
                }
                const newVal = val + 1;
                
                // Optimistic UI Update
                if (input) input.value = newVal;

                // Trigger Update to Backend
                await handleItemUpdate(itemName, newVal);
                ui.showToast(`Count incremented to ${newVal}`, "success");
            }
        } catch (e) {
            console.error(e);
            ui.showToast("Upload failed.", "error");
        }
    });
}

// 3. Assignment Change
async function handleAssignmentChange(itemId, userId, userName) {
    console.log(`Assign ${itemId} to ${userName} (${userId})`);
    if (state.tripId) {
        try {
             // Get current check state from UI to preserve it
            const itemSchema = Object.values(CHECKLIST_SCHEMA).flat().find(i => i.label === itemId || i.id === itemId);
            const row = document.querySelector(`.item-row[data-id="${itemSchema ? itemSchema.id : itemId}"]`);
            let isChecked = false;
            let currentValue = undefined;
            if (row) {
                const input = row.querySelector('input');
                if (input) {
                    if (input.type === 'checkbox') {
                        isChecked = input.checked;
                    } else {
                        currentValue = input.value;
                        // Use row class as definitive "checked" state
                        isChecked = row.classList.contains('checked');
                    }
                }
            }

            await api.updateChecklistItem(state.tripId, itemId, isChecked, currentValue, undefined, userId, userName);
            // Trigger manual poll for robustness
            schedulePollState(500);
        } catch (e) {
            console.error("Assignment update failed:", e);
        }
    }
}

// 3. Voice FAB (Hold to Speak)
function setupVoiceFab() {
    const fabs = document.querySelectorAll('.mic-bar');
    const indicator = document.getElementById('listening-indicator');
    
    // Helper to update all FABs UI
    const updateFabs = (isListening) => {
        fabs.forEach(f => {
            if (isListening) {
                f.style.transform = "scale(0.98)";
                f.classList.add('listening');
                f.innerText = "Listening...";
            } else {
                f.style.transform = "scale(1)";
                f.classList.remove('listening');
                f.innerText = "Hold to Speak";
            }
        });
    };

    // Touch/Mouse Down -> Start
    const startListener = async (e) => {
        e.preventDefault(); // Prevent text selection
        updateFabs(true);
        if (await media.startRecording()) {
            indicator.classList.remove('hidden');
        }
    };

    // Touch/Mouse Up -> Stop & Send
    const stopListener = async (e) => {
        // Don't revert immediately in updateFabs(false)
        // updateFabs(false); 
        // We handle UI manually here for transition
        
        indicator.classList.add('hidden');
        
        // Show Processing State
        fabs.forEach(f => {
            f.classList.remove('listening');
            f.classList.add('processing');
            f.innerText = "Processing...";
        });
        
        const audioBlob = await media.stopRecording();
        if (audioBlob) {
            console.log("Sending Audio...");
            try {
                // Use a simple prompt to anchor the audio turn
                const prompt = `Voice command from ${state.displayName}`;
                const events = await api.sendInteraction(
                    state.sessionId, 
                    state.userId, 
                    prompt, 
                    null, 
                    audioBlob
                );
                
                console.log("Agent Replied:", events);

                // Check for tool results with warnings or partial success
                if (Array.isArray(events)) {
                    events.forEach(ev => {
                        if (ev.content && ev.content.parts) {
                            ev.content.parts.forEach(p => {
                                if (p.function_response && p.function_response.response) {
                                    const resp = p.function_response.response;
                                    if (resp.status === "warning" || resp.status === "partial_success") {
                                        ui.showToast(resp.message, "warning");
                                    }
                                }
                            });
                        }
                    });
                }

                ui.showToast("Got it!", "success");
            } catch (e) {
                console.error(e);
                
                // If it's a history/turn error, we might need a fresh session
                if (e.message.includes("turn") || e.message.includes("INVALID_ARGUMENT")) {
                    console.warn("History corruption detected, restarting session...");
                    state.sessionId = 's' + Math.random().toString(36).substring(2, 11);
                    localStorage.setItem('navallist_session_id', state.sessionId);
                    ui.showToast("Session refreshed due to error. Please try again.", "info");
                    // Re-sync session with backend
                    api.createSession(state.sessionId, state.userId, state.displayName);
                }

                // Check for structured error from api.js
                if (e.data && e.data.code === "overloaded") {
                    ui.showToast("The AI is a bit busy right now. Please wait a few seconds and try again.", "warning");
                } else if (e.message.includes("overloaded")) {
                    ui.showToast("The AI is a bit busy right now. Please wait a few seconds and try again.", "warning");
                } else {
                    ui.showToast("Agent failed: " + e.message, "error");
                }
            } finally {
                // Reset UI
                fabs.forEach(f => {
                    f.classList.remove('processing');
                    f.style.transform = "scale(1)";
                    f.innerText = "Hold to Speak";
                });
            }
        } else {
             // Reset if no recording
             fabs.forEach(f => {
                f.classList.remove('listening');
                f.style.transform = "scale(1)";
                f.innerText = "Hold to Speak";
            });
        }
    };

    fabs.forEach(fab => {
        fab.addEventListener('mousedown', startListener);
        fab.addEventListener('touchstart', startListener);
        
        fab.addEventListener('mouseup', stopListener);
        fab.addEventListener('touchend', stopListener);
    });
}