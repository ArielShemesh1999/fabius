// auth.js - Authentication Logic
import { api } from './api.js';
import { ui } from './ui.js';

export async function checkAuth() {
    try {
        const response = await fetch('/auth/me');
        if (response.ok) {
            const user = await response.json();
            handleLoggedIn(user);
            return user;
        } else {
            handleLoggedOut();
            return null;
        }
    } catch (error) {
        // Only log if it's NOT a 401 (Unauthorized), as 401 is expected for guests
        if (error.status !== 401) {
            console.warn('Auth check (non-401 or network error):', error);
        }
        handleLoggedOut();
        return null;
    }
}

async function handleLoggedIn(user) {
    // Update button text
    const submitBtn = document.querySelector('#login-form button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerText = 'Start / Join Trip';
    }

    // Hide Google Login Button
    const googleBtnContainer = document.getElementById('google-login-container');
    if (googleBtnContainer) {
        googleBtnContainer.style.display = 'none';
    }

    // Show Logout Button
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.classList.remove('hidden');
    }

    // Fill Captain Name
    const nameInput = document.getElementById('user-id');
    if (nameInput) {
        nameInput.value = user.name || '';
        // Optional: Disable it if we don't want them to change it
        // nameInput.disabled = true; 
    }

    // Load Trips
    const tripsContainer = document.getElementById('user-trips-container');
    if (tripsContainer) {
        tripsContainer.classList.remove('hidden');
    }

    try {
        const trips = await api.getUserTrips();
        ui.renderTripList(trips);
    } catch (e) {
        console.warn("Failed to load trips", e);
    }
}

function handleLoggedOut() {
    // Update button text
    const submitBtn = document.querySelector('#login-form button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerText = 'Join Trip';
    }

    // Show Google Login Button
    const googleBtnContainer = document.getElementById('google-login-container');
    if (googleBtnContainer) {
        googleBtnContainer.style.display = 'block';
    }

    const tripsContainer = document.getElementById('user-trips-container');
    if (tripsContainer) {
        tripsContainer.classList.add('hidden');
    }

    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.classList.add('hidden');
    }

    const nameInput = document.getElementById('user-id');
    if (nameInput) {
        nameInput.value = '';
    }
}

// Wire up logout button
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            if (confirm("Are you sure you want to logout?")) {
                window.location.href = '/auth/logout';
            }
        });
    }
});
