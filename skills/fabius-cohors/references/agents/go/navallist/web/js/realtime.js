import { Centrifuge } from 'centrifuge';

let centrifuge = null;
let currentSubscription = null;

export function initRealtime(displayName) {
    if (centrifuge) return centrifuge;

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host; // e.g. localhost:8080
    let url = `${protocol}://${host}/connection/websocket`;
    
    if (displayName) {
        url += `?name=${encodeURIComponent(displayName)}`;
    }

    centrifuge = new Centrifuge(url);

    centrifuge.on('connected', (ctx) => {
        console.log("Realtime connected", ctx);
        document.dispatchEvent(new CustomEvent('connection-status', { detail: { status: 'connected' } }));
    });

    centrifuge.on('disconnected', (ctx) => {
        console.warn("Realtime disconnected", ctx);
        document.dispatchEvent(new CustomEvent('connection-status', { detail: { status: 'disconnected' } }));
    });

    centrifuge.connect();
    return centrifuge;
}

export function subscribeTrip(tripId, onUpdate, onPresenceUpdate, displayName) {
    const client = initRealtime(displayName);

    if (currentSubscription) {
        // If already subscribed to this trip, do nothing or re-sub?
        // If different trip, unsubscribe.
        // For simplicity, always unsub previous if any.
        currentSubscription.removeAllListeners();
        currentSubscription.unsubscribe();
    }

    const channel = `trip:${tripId}`;
    console.log(`Subscribing to ${channel}`);
    
    const sub = client.newSubscription(channel);

    sub.on('publication', function(ctx) {
        // ctx.data is the payload sent from Go.
        // Go sends the DBEvent JSON.
        // Structure: { table, action, data, trip_id }
        console.log("Realtime update:", ctx.data);
        onUpdate(ctx.data);
    });

    if (onPresenceUpdate) {
        sub.on('join', function(ctx) {
            console.log("User joined:", ctx.info);
            onPresenceUpdate('join', ctx.info); 
        });

        sub.on('leave', function(ctx) {
            console.log("User left:", ctx.info);
            onPresenceUpdate('leave', ctx.info);
        });

        sub.on('subscribed', function (ctx) {
            console.log('subscribed', ctx);
            // 1. Use Data from Server (Initial State)
            if (ctx.data) {
                console.log("Initial Presence Data:", ctx.data);
                onPresenceUpdate('state', ctx.data);
            }
            
            // 2. Try Standard Presence (Might fail with 108 if not enabled)
            sub.presence().then(function(pCtx) {
                console.log("Presence:", pCtx.clients);
                onPresenceUpdate('state', pCtx.clients);
            }, function(err) {
                console.warn("Presence failed (using initial data if avail)", err);
            });
        });
    } else {
        sub.on('subscribed', function (ctx) {
            console.log('subscribed', ctx);
        });
    }

    sub.on('subscribing', function (ctx) {
        console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
    });

    sub.on('unsubscribed', function (ctx) {
        console.log('unsubscribed', ctx);
    });

    sub.subscribe();
    currentSubscription = sub;
}

export function disconnectRealtime() {
    if (centrifuge) {
        centrifuge.disconnect();
        centrifuge = null;
        currentSubscription = null;
    }
}
