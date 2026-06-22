// ui.js - Rendering Logic

import { CHECKLIST_SCHEMA } from './checklist_data.js';

function updateHeaderTitle(sessionId, boatName) {
    const el = document.getElementById('trip-title');
    el.innerText = sessionId;
}

function getUserColor(name) {
    const colors = [
        'rgb(88, 61, 27)',  // Deep Brown
        'rgb(149, 104, 45)', // Bronze
        '#314c3b',           // Dark Green
        '#1565c0',           // Nautical Blue
        '#2e7d32',           // Success Green
        '#5d4037',           // Dark Wood
        '#006064',           // Deep Teal
        '#283593'            // Indigo
    ];
    
    if (!name) return colors[0];
    
    // Simple hash to select color
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % colors.length;
    return colors[index];
}

export const ui = {
    
    currentCategory: Object.keys(CHECKLIST_SCHEMA)[0], // Default to first
    hideChecked: localStorage.getItem('navallist_hide_checked') !== 'false', // Load from storage
    tripType: 'Departing',
    activeUsers: new Map(),

    getInitials(name) {
         if (!name) return "?";
         const parts = name.trim().split(/\s+/);
         if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
         return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    },

    updatePresence(type, data) {
        console.log(`updatePresence(${type}):`, JSON.stringify(data));
        if (type === 'state') {
            this.activeUsers.clear();
            if (data) {
                Object.values(data).forEach(client => {
                    if (client) {
                        const userId = client.user || client.userId || client.userID || client.UserID || client.User || "";
                        if (userId) {
                            let name = userId;
                            if (name.startsWith("guest_")) name = name.substring(6);
                            const rawInfo = client.info || client.conn_info || client.connInfo || client.ConnInfo;
                            if (rawInfo) {
                                try {
                                    let infoStr;
                                    if (typeof rawInfo === 'string') {
                                        try { infoStr = atob(rawInfo); } catch(e) { infoStr = rawInfo; }
                                    } else if (rawInfo instanceof Uint8Array) {
                                        infoStr = new TextDecoder().decode(rawInfo);
                                    } else {
                                        if (rawInfo.name) name = rawInfo.name;
                                    }
                                    if (infoStr) {
                                        const info = JSON.parse(infoStr);
                                        if (info && info.name) name = info.name;
                                    }
                                } catch (e) {
                                     console.warn("Failed to parse info for", userId, e);
                                }
                            }
                            console.log(`Adding user from state: ID=${userId} Name=${name}`);
                            this.activeUsers.set(userId, name);
                        }
                    }
                });
            }
        } else if (type === 'join') {
            if (data) {
                const userId = data.user || data.userId || data.userID || data.UserID || data.User || "";
                if (userId) {
                    let name = userId;
                    if (name.startsWith("guest_")) name = name.substring(6);
                    const info = data.info || data.connInfo || data.conn_info || data.ConnInfo;
                    if (info) {
                         if (info.name) name = info.name;
                         else if (typeof info === 'string') {
                             try {
                                 const parsed = JSON.parse(info);
                                 if (parsed.name) name = parsed.name;
                             } catch(e) {
                                 try {
                                     const decoded = JSON.parse(atob(info));
                                     if (decoded.name) name = decoded.name;
                                 } catch(e2) {}
                             }
                         }
                    }
                    console.log(`Adding user from join: ID=${userId} Name=${name}`);
                    this.activeUsers.set(userId, name);
                }
            }
        } else if (type === 'leave') {
            if (data) {
                const userId = data.user || data.userId || data.userID || data.UserID || data.User || "";
                if (userId) {
                    console.log(`Removing user: ${userId}`);
                    this.activeUsers.delete(userId);
                }
            }
        }
        this.renderPresenceBar();
    },

    renderPresenceBar() {
        const bar = document.getElementById('presence-bar');
        if (!bar) return;
        if (this.activeUsers.size === 0) {
            bar.classList.add('hidden');
            return;
        }
        bar.classList.remove('hidden');
        bar.innerHTML = '';
        
        const template = document.getElementById('template-presence-user');

        this.activeUsers.forEach((name, userId) => {
            const clone = template.content.cloneNode(true);
            const div = clone.querySelector('.user-avatar');
            div.title = name;
            div.ariaLabel = `User: ${name}`;
            div.style.backgroundColor = getUserColor(name);
            div.innerText = this.getInitials(name);
            bar.appendChild(div);
        });
    },

    updateConnectionStatus(status) {
        const el = document.getElementById('connection-status');
        if (!el) return;
        el.classList.remove('hidden');
        if (status === 'connected') {
            el.classList.add('connected');
            el.classList.remove('disconnected');
            el.title = "Connected";
        } else {
            el.classList.remove('connected');
            el.classList.add('disconnected');
            el.title = "Disconnected (Reconnecting...)";
        }
    },

    setTripType(type) {
        this.tripType = type || 'Departing';
        this.updateItemVisibilityByTripType();
    },

    getItemExplanation(item) {
        let explanation = item.explanation;
        if (this.tripType === 'Returning' && item.explanation_returning) {
            explanation = item.explanation_returning;
        } else if (item.explanation_departing) {
            explanation = item.explanation_departing;
        }
        return explanation;
    },

    updateItemVisibilityByTripType() {
        Object.values(CHECKLIST_SCHEMA).flat().forEach(item => {
            const explanation = this.getItemExplanation(item);
            const isNA = explanation === "N/A";
            
            // Update all rows for this item (cat and my)
            const rows = document.querySelectorAll(`.item-row[data-id="${item.id}"]`);
            rows.forEach(row => {
                if (isNA) row.classList.add('hidden-na');
                else row.classList.remove('hidden-na');
            });
        });
        this.updateTabVisibility();
    },

    init(containerId, tabsId) {
        const container = document.getElementById(containerId);
        const tabsContainer = document.getElementById(tabsId);
        container.innerHTML = '';
        tabsContainer.innerHTML = '';

        const myTab = document.createElement('a');
        myTab.className = 'tab hidden';
        myTab.innerText = "My Items";
        myTab.dataset.category = "My Items";
        myTab.onclick = () => this.switchTab("My Items");
        tabsContainer.appendChild(myTab);

        const myGroup = document.createElement('div');
        myGroup.className = 'category-group';
        myGroup.id = 'cat-My-Items';
        container.appendChild(myGroup);

        Object.keys(CHECKLIST_SCHEMA).forEach((category, index) => {
            const tab = document.createElement('a');
            tab.className = 'tab';
            tab.innerText = category;
            tab.dataset.category = category;
            tab.onclick = () => this.switchTab(category);
            tabsContainer.appendChild(tab);

            const group = document.createElement('div');
            group.className = 'category-group';
            group.id = `cat-${category.replace(/\s+/g, '-')}`;
            CHECKLIST_SCHEMA[category].forEach(item => {
                group.appendChild(this.createItemRow(item, 'cat'));
            });
            container.appendChild(group);
        });
        this.updateItemVisibilityByTripType();
        this.updateTabVisibility();
    },

    createIcon(name, fontSize = null) {
        const span = document.createElement('span');
        span.className = 'material-symbols-outlined';
        if (fontSize) span.style.fontSize = fontSize;
        span.innerText = name;
        return span;
    },

    createItemRow(item, context = 'cat') {
        const template = document.getElementById('template-checklist-item');
        const clone = template.content.cloneNode(true);
        const div = clone.querySelector('.item-row');
        
        div.id = `row-${context}-${item.id}`;
        div.dataset.id = item.id;
        div.dataset.context = context;
        div.dataset.label = item.label;

        // Info Button
        const infoBtn = div.querySelector('.btn-info');
        infoBtn.dataset.itemId = item.id;

        // Label
        const label = div.querySelector('.item-label');
        label.innerText = item.label;

        // Assign Button
        const assignBtn = div.querySelector('.btn-assign');
        assignBtn.dataset.assignId = item.id;
        assignBtn.dataset.label = item.label;

        // Camera Button
        const camBtn = div.querySelector('.btn-cam');
        if (item.allow_photo) {
            camBtn.classList.remove('hidden');
            camBtn.dataset.itemId = item.id;
            camBtn.dataset.label = item.label;
        } else {
            camBtn.remove();
        }

        // Input
        const actions = div.querySelector('.item-actions');
        let input;
        if (item.type === 'count' || item.type === 'input' || item.type === 'number' || item.type === 'text') {
            input = document.createElement('input');
            input.type = (item.type === 'count' || item.type === 'number') ? 'number' : 'text';
            input.placeholder = (item.type === 'count' || item.type === 'number') ? '#' : '...';
        } else {
            input = document.createElement('input');
            input.type = 'checkbox';
        }
        input.dataset.action = "update-item";
        input.dataset.inputId = item.id;
        input.dataset.label = item.label;
        actions.appendChild(input);

        return div;
    },

    switchTab(categoryName) {
        this.currentCategory = categoryName;
        document.querySelectorAll('.tab').forEach(t => {
            t.classList.toggle('active', t.innerText === categoryName);
        });
        document.querySelectorAll('.category-group').forEach(g => {
            const isActive = g.id === `cat-${categoryName.replace(/\s+/g, '-')}`;
            g.classList.toggle('active', isActive);
        });
    },

    showHelp(item) {
        const dialog = document.getElementById('help-dialog');
        document.getElementById('help-title').innerText = item.label;
        const explanation = this.getItemExplanation(item);
        document.getElementById('help-explanation').innerText = explanation || "No additional information available.";
        const picSection = document.getElementById('help-picture-section');
        if (item.allow_photo && item.picture_reason) {
            document.getElementById('help-picture-reason').innerText = item.picture_reason;
            picSection.classList.remove('hidden');
        } else {
            picSection.classList.add('hidden');
        }
        dialog.showModal();
    },

    updateTabVisibility() {
        let firstVisibleCategory = null;
        const myGroup = document.getElementById('cat-My-Items');
        const myTab = Array.from(document.querySelectorAll('.tab')).find(t => t.innerText === "My Items");
        if (myGroup && myTab) {
            const hasVisibleItems = Array.from(myGroup.querySelectorAll('.item-row')).some(
                row => !row.classList.contains('hidden') && !row.classList.contains('hidden-na')
            );
            if (hasVisibleItems) {
                myTab.classList.remove('hidden');
                if (!firstVisibleCategory) firstVisibleCategory = "My Items";
            } else {
                myTab.classList.add('hidden');
            }
        }

        Object.keys(CHECKLIST_SCHEMA).forEach((category) => {
            const groupId = `cat-${category.replace(/\s+/g, '-')}`;
            const group = document.getElementById(groupId);
            if (!group) return;
            const hasVisibleItems = Array.from(group.querySelectorAll('.item-row')).some(
                row => !row.classList.contains('hidden') && !row.classList.contains('hidden-na')
            );
            const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.innerText === category);
            if (tab) {
                if (hasVisibleItems) {
                    tab.classList.remove('hidden');
                    if (!firstVisibleCategory) firstVisibleCategory = category;
                } else {
                    tab.classList.add('hidden');
                }
            }
        });

        const currentTab = Array.from(document.querySelectorAll('.tab')).find(t => t.innerText === this.currentCategory);
        const noActiveTab = !document.querySelector('.tab.active');
        if (noActiveTab || (currentTab && currentTab.classList.contains('hidden'))) {
            if (firstVisibleCategory) {
                this.switchTab(firstVisibleCategory);
            }
        }
    },

    setupSwipeHandlers(elementId) {
        const element = document.getElementById(elementId);
        let touchStartX = 0;
        let touchStartY = 0;
        element.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
        }, {passive: true});
        element.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].screenX;
            const touchEndY = e.changedTouches[0].screenY;
            this.handleSwipe(touchStartX, touchStartY, touchEndX, touchEndY);
        }, {passive: true});
    },

    handleSwipe(startX, startY, endX, endY) {
        const diffX = endX - startX;
        const diffY = endY - startY;
        const threshold = 50;
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > threshold) {
            if (diffX > 0) this.navigateTab(-1);
            else this.navigateTab(1);
        }
    },

    navigateTab(direction) {
        const tabs = Array.from(document.querySelectorAll('.tab'));
        const visibleTabs = tabs.filter(t => !t.classList.contains('hidden'));
        const currentIndex = visibleTabs.findIndex(t => t.innerText === this.currentCategory);
        if (currentIndex !== -1) {
            const nextIndex = currentIndex + direction;
            if (nextIndex >= 0 && nextIndex < visibleTabs.length) {
                this.switchTab(visibleTabs[nextIndex].innerText);
            }
        }
    },

    showAssignMenu(item) {
        console.log("Active Users Map:", this.activeUsers);
        const dialog = document.getElementById('assign-dialog');
        document.getElementById('assign-item-name').innerText = item.label;
        const list = document.getElementById('assign-list');
        list.innerHTML = '';
        const createRow = (userId, userName) => {
            const btn = document.createElement('button');
            btn.className = 'assign-option';
            btn.style.display = 'flex';
            btn.style.alignItems = 'center';
            btn.style.gap = '1rem';
            btn.style.padding = '0.8rem';
            btn.style.border = '1px solid var(--border-color)';
            btn.style.borderRadius = '4px';
            btn.style.background = 'var(--surface-bg)';
            btn.style.cursor = 'pointer';
            const avatar = document.createElement('div');
            avatar.className = 'user-avatar';
            avatar.style.backgroundColor = getUserColor(userName || userId);
            avatar.innerText = this.getInitials(userName || userId);
            const label = document.createElement('span');
            label.innerText = (userName || userId);
            btn.appendChild(avatar);
            btn.appendChild(label);
            btn.onclick = () => {
                // window.handleAssignmentChange(item.label, userId, userName || userId);
                document.dispatchEvent(new CustomEvent('assignment-change', {
                    detail: { itemId: item.label, userId: userId, userName: userName || userId }
                }));
                dialog.close();
            };
            return btn;
        };
        if (this.activeUsers.size > 0) {
            this.activeUsers.forEach((name, userId) => {
                list.appendChild(createRow(userId, name));
            });
        } else {
             const msg = document.createElement('p');
             msg.innerText = "No other active users found.";
             msg.style.color = "var(--text-light)";
             list.appendChild(msg);
        }
        const unassignBtn = document.createElement('button');
        unassignBtn.className = 'assign-option';
        unassignBtn.style.padding = '0.8rem';
        unassignBtn.style.marginTop = '0.5rem';
        unassignBtn.innerText = "Unassign";
        unassignBtn.onclick = () => {
            // window.handleAssignmentChange(item.label, "", "");
            document.dispatchEvent(new CustomEvent('assignment-change', {
                detail: { itemId: item.label, userId: "", userName: "" }
            }));
            dialog.close();
        };
        list.appendChild(unassignBtn);
        dialog.showModal();
        document.getElementById('close-assign').onclick = () => dialog.close();
    },

    toggleHideChecked(enabled) {
        this.hideChecked = enabled;
        localStorage.setItem('navallist_hide_checked', enabled);
        document.querySelectorAll('.item-row').forEach(row => {
            const input = row.querySelector('input');
            if (input) {
                let shouldHide = (input.type === 'checkbox' && input.checked) || (input.value && input.value.trim() !== "");
                if (shouldHide && this.hideChecked) row.classList.add('hidden');
                else row.classList.remove('hidden');
            }
        });
        this.updateTabVisibility();
    },

    updateState(state, currentUserId, currentDisplayName) {
        if (!state) return;
        this.updateMyItemsTab(state, currentUserId, currentDisplayName);
        Object.values(CHECKLIST_SCHEMA).flat().forEach(item => {
            const inputs = document.querySelectorAll(`input[data-input-id="${item.id}"]`);
            inputs.forEach(input => {
                const row = input.closest('.item-row');
                if (row) this.applyItemState(row, item, state, input);
            });
        });
        if (state.boat_name) {
            const input = document.getElementById('input-boat_name');
            if (input) input.value = state.boat_name;
        }
        this.updateTabVisibility();
    },

    applyItemState(row, item, state, input) {
        let val = state[item.id] !== undefined ? state[item.id] : state[item.label];
        let isCompleted = false;
        if (val !== undefined) {
            if (input.type === 'checkbox') {
                input.checked = val === true || val === "true";
                isCompleted = input.checked;
            } else {
                // Text/Number input
                if (typeof val === 'boolean' || val === "true" || val === "false") {
                    input.value = "";
                    isCompleted = false; // Booleans don't mark text/number items as completed
                } else {
                    if (document.activeElement !== input) input.value = val;
                    isCompleted = (val !== null && val !== undefined && String(val).trim() !== "");
                }
            }
        }
        if (isCompleted) row.classList.add('checked');
        else row.classList.remove('checked');

        const shouldHide = isCompleted && this.hideChecked && !item.allow_multi_photo;

        if (shouldHide) {
            if (!row.classList.contains('hidden') && !row.classList.contains('fading-out')) {
                setTimeout(() => {
                    row.classList.add('fading-out');
                    setTimeout(() => {
                        row.classList.add('hidden');
                        row.classList.remove('fading-out');
                        this.updateTabVisibility();
                    }, 1000); 
                }, 1000); 
            }
        } else {
            row.classList.remove('hidden');
            row.classList.remove('fading-out');
        }
        
        // Render Photos
        const photos = state[`${item.label}_photos`] || state[`${item.id}_photos`];
        const photoContainer = row.querySelector('.item-photos');
        if (photoContainer) {
            photoContainer.innerHTML = '';
            if (photos && Array.isArray(photos) && photos.length > 0) {
                const template = document.getElementById('template-photo-icon');
                const clone = template.content.cloneNode(true);
                const wrapper = clone.querySelector('.photo-icon-wrapper');
                
                const countSpan = wrapper.querySelector('.photo-count');
                countSpan.innerText = photos.length;
                
                // Add data for delegation
                wrapper.dataset.filenames = JSON.stringify(photos.map(p => p.filename));
                
                photoContainer.appendChild(wrapper);
            }
        }

        let assignName = state[`${item.label}_assigned_to_name`] || state[`${item.id}_assigned_to_name`];
        const assignBtn = row.querySelector('.btn-assign');
        if (assignBtn) {
            assignBtn.innerHTML = '';
            if (assignName) {
                 const div = document.createElement('div');
                 div.className = 'user-avatar small';
                 div.style.backgroundColor = getUserColor(assignName);
                 div.innerText = this.getInitials(assignName);
                 div.title = assignName;
                 assignBtn.appendChild(div);
            } else {
                assignBtn.appendChild(this.createIcon('person_add'));
            }
        }
    },
    
    updateMyItemsTab(state, currentUserId, currentDisplayName) {
        const group = document.getElementById('cat-My-Items');
        if (!group || !currentUserId) return;
        
        const cleanUserId = currentUserId.startsWith("guest_") ? currentUserId.substring(6) : currentUserId;
        const currentUserNameFromPresence = this.activeUsers.get(currentUserId);
        
        Object.values(CHECKLIST_SCHEMA).flat().forEach(item => {
             let assignName = state[`${item.label}_assigned_to_name`] || state[`${item.id}_assigned_to_name`];
             let assignId = state[`${item.label}_assigned_to_user_id`] || state[`${item.id}_assigned_to_user_id`];
             
             // Robust match: check full ID, clean ID, or Name (from state, presence, or passed display name)
             let match = (assignId && (assignId === currentUserId || assignId === cleanUserId)) || 
                         (assignName && (
                            assignName === currentUserId || 
                            assignName === cleanUserId || 
                            (currentDisplayName && assignName === currentDisplayName) ||
                            (currentUserNameFromPresence && assignName === currentUserNameFromPresence)
                         ));
                         
             const rowId = `row-my-${item.id}`;
             const existingRow = document.getElementById(rowId);

             if (match) {
                 if (!existingRow) group.appendChild(this.createItemRow(item, 'my'));
             } else {
                 if (existingRow) existingRow.remove();
             }
        });
    },

    renderReport(items, trip) {
        this.renderReportContent(items, trip);
        document.getElementById('report-dialog').showModal();
    },

    renderReportContent(items, trip) {
        const container = document.getElementById('report-content');
        container.innerHTML = '';
        const reportTripType = (trip && trip.trip_type) ? trip.trip_type : this.tripType;
        const dbItems = {};
        if (items && Array.isArray(items)) {
            items.forEach(item => { dbItems[item.name] = item; });
        }

        Object.keys(CHECKLIST_SCHEMA).forEach(category => {
            const section = document.createElement('div');
            section.className = 'report-section';
            const title = document.createElement('h3');
            title.innerText = category;
            section.appendChild(title);
            let visibleItemsCount = 0;

            CHECKLIST_SCHEMA[category].forEach(schemaItem => {
                let explanation = this.getItemExplanation(schemaItem);
                if (explanation === "N/A") return;
                visibleItemsCount++;
                let dbItem = dbItems[schemaItem.label];
                if (!dbItem && schemaItem.id === 'boat_name' && trip && trip.boat_name) {
                    dbItem = { name: schemaItem.label, location_text: trip.boat_name, is_checked: true };
                }
                const row = document.createElement('div');
                row.className = 'report-item';
                const initialsDiv = document.createElement('div');
                initialsDiv.className = 'user-initials';
                const displayName = (dbItem && dbItem.completed_by_user_name) ? dbItem.completed_by_user_name : (dbItem ? dbItem.completed_by_name : null);
                if (displayName) {
                    initialsDiv.innerText = this.getInitials(displayName);
                    initialsDiv.title = displayName;
                    initialsDiv.style.backgroundColor = getUserColor(displayName);
                } else {
                    initialsDiv.classList.add('empty');
                }
                row.appendChild(initialsDiv);
                const name = document.createElement('span');
                name.innerText = schemaItem.label;
                const val = document.createElement('span');
                if (dbItem) {
                    const hasValue = dbItem.location_text && dbItem.location_text.trim() !== "";
                    const isChecked = dbItem.is_checked || hasValue;
                    if (dbItem.flagged_issue) {
                        row.classList.add('issue');
                        val.innerText = `${dbItem.flagged_issue} ⚠️`;
                    } else if (isChecked) {
                        val.style.display = 'flex';
                        val.style.alignItems = 'center';
                        val.style.gap = '0.5rem';
                        val.style.flexWrap = 'wrap';
                        
                        if (dbItem.photos && dbItem.photos.length > 0) {
                             const btn = document.createElement('button');
                             btn.className = 'btn-view-photo';
                             const count = dbItem.photos.length;
                             btn.appendChild(this.createIcon('photo_library', '1rem'));
                             btn.appendChild(document.createTextNode(' ' + count));
                             btn.title = `View ${count} Photos`;
                             btn.onclick = () => {
                                 const filenames = dbItem.photos.map(p => p.filename);
                                 window.viewPhoto(filenames);
                             };
                             val.appendChild(btn);
                        } else if (dbItem.photo_artifact_id) {
                            // Fallback
                            const btn = document.createElement('button');
                            btn.className = 'btn-view-photo';
                            btn.appendChild(this.createIcon('image', '1rem'));
                            btn.appendChild(document.createTextNode(' 1'));
                            btn.title = "View Photo";
                            btn.onclick = () => window.viewPhoto(dbItem.photo_artifact_id);
                            val.appendChild(btn);
                        } else if (schemaItem.allow_photo) {
                            const noPhoto = document.createElement('span');
                            noPhoto.className = 'btn-no-photo';
                            noPhoto.appendChild(this.createIcon('no_photography', '1rem'));
                            noPhoto.appendChild(document.createTextNode(' 0'));
                            val.appendChild(noPhoto);
                        }
                        const text = document.createElement('span');
                        text.innerText = hasValue ? `${dbItem.location_text} ✓` : `✓`;
                        val.appendChild(text);
                    } else { val.innerText = '-'; }
                } else { val.innerText = '-'; }
                row.appendChild(name);
                row.appendChild(val);
                section.appendChild(row);
            });
            if (visibleItemsCount > 0) container.appendChild(section);
        });
    },

    renderTripList(trips) {
        const container = document.getElementById('trips-list');
        if (!trips || trips.length === 0) {
            container.innerHTML = '';
            const p = document.createElement('p');
            p.className = 'trip-list-empty';
            p.innerText = 'No trips found.';
            container.appendChild(p);
            return;
        }
        container.innerHTML = '';
        
        const template = document.getElementById('template-trip-item');

        trips.forEach(trip => {
            const clone = template.content.cloneNode(true);
            const div = clone.querySelector('.trip-list-item');
            
            // Data for delegation
            div.dataset.action = "select-trip";
            div.dataset.sessionId = trip.adk_session_id;

            const date = new Date(trip.created_at).toLocaleDateString();
            
            clone.querySelector('.trip-session').innerText = trip.adk_session_id;
            clone.querySelector('.trip-date').innerText = date;
            
            clone.querySelector('.type-badge').innerText = trip.trip_type || 'Departing';
            
            const statusBadge = clone.querySelector('.status-state');
            statusBadge.className = `status-badge status-state ${trip.status ? trip.status.toLowerCase() : ''}`;
            statusBadge.innerText = trip.status;

            const delBtn = clone.querySelector('.btn-delete-trip');
            delBtn.dataset.action = "delete-trip";
            delBtn.dataset.tripId = trip.id;
            delBtn.dataset.sessionId = trip.adk_session_id;

            container.appendChild(div);
        });
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerText = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'toast-out 0.3s forwards';
            toast.addEventListener('animationend', () => toast.remove());
        }, 3000);
    },

    updateHeaderTitle
};
