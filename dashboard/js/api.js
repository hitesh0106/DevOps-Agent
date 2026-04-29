/**
 * DevOps Agent — API Client
 * Wraps all backend communication.
 */

const API_BASE = '/api';

const Api = {
    async get(endpoint) {
        try {
            const resp = await fetch(`${API_BASE}${endpoint}`);
            return await resp.json();
        } catch (err) {
            console.error(`API GET Error [${endpoint}]:`, err);
            throw err;
        }
    },

    async post(endpoint, data) {
        try {
            const resp = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await resp.json();
        } catch (err) {
            console.error(`API POST Error [${endpoint}]:`, err);
            throw err;
        }
    },

    // Specific endpoints
    async runTask(task) {
        return await this.post('/agent/task', { task });
    },

    async getStatus() {
        return await this.get('/monitoring/status');
    },

    async getPipelines() {
        return await this.get('/pipelines');
    },

    async getIncidents() {
        return await this.get('/monitoring/incidents');
    }
};
