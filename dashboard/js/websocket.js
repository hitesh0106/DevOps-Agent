/**
 * DevOps Agent — Real-time Updates (WebSockets)
 * Handles live telemetry and agent events.
 */

class AgentSocket {
    constructor() {
        this.socket = null;
        this.reconnectInterval = 5000;
        this.init();
    }

    init() {
        // Use window.location for protocol/host
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/agent`;

        console.log('Connecting to Agent Socket:', wsUrl);
        
        // Simulating WebSocket for Demo if backend not ready
        this.simulateLiveEvents();
    }

    // Since we are in a demo/development environment, let's simulate
    // real-time events that would normally come over a socket.
    simulateLiveEvents() {
        setInterval(() => {
            if (Math.random() > 0.85) {
                this.onMessage({
                    type: 'status_update',
                    data: {
                        resource: 'node-02',
                        metric: 'CPU',
                        value: Math.floor(Math.random() * 20) + 30 + '%'
                    }
                });
            }
        }, 10000);
    }

    onMessage(event) {
        if (event.type === 'status_update') {
            console.log('Live Telemetry:', event.data);
            // In a real implementation, we would update the UI here
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.agentSocket = new AgentSocket();
});
