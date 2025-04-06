// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// API service for making HTTP requests
const api = {
    // Generic fetch method with error handling
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // File upload method
    async uploadFile(endpoint, formData, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                body: formData,
                ...options
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `API error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    },
    
    // File download method
    async downloadFile(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return response.blob();
        } catch (error) {
            console.error('File download failed:', error);
            throw error;
        }
    },
    
    // Search API
    async searchItem(itemId, itemName, userId) {
        const params = new URLSearchParams();
        if (itemId) params.append('itemId', itemId);
        if (itemName) params.append('itemName', itemName);
        if (userId) params.append('userId', userId);
        
        return this.fetch(`/search?${params.toString()}`, { method: 'GET' });
    },
    
    async retrieveItem(itemId, userId) {
        return this.fetch('/retrieve', {
            method: 'POST',
            body: JSON.stringify({
                itemId,
                userId,
                timestamp: new Date().toISOString()
            })
        });
    },
    
    async placeItem(itemId, userId, containerId, position) {
        return this.fetch('/place', {
            method: 'POST',
            body: JSON.stringify({
                itemId,
                userId,
                timestamp: new Date().toISOString(),
                containerId,
                position
            })
        });
    },
    
    // Waste Management API
    async identifyWaste() {
        return this.fetch('/waste/identify', { method: 'GET' });
    },
    
    async generateReturnPlan(undockingContainerId, undockingDate, maxWeight) {
        return this.fetch('/waste/return-plan', {
            method: 'POST',
            body: JSON.stringify({
                undockingContainerId,
                undockingDate,
                maxWeight: Number(maxWeight)
            })
        });
    },
    
    async completeUndocking(undockingContainerId) {
        return this.fetch('/waste/complete-undocking', {
            method: 'POST',
            body: JSON.stringify({
                undockingContainerId,
                timestamp: new Date().toISOString()
            })
        });
    },
    
    // Time Simulation API
    async simulateDay(numOfDays, toTimestamp, itemsToBeUsedPerDay) {
        return this.fetch('/simulate/day', {
            method: 'POST',
            body: JSON.stringify({
                numOfDays,
                toTimestamp,
                itemsToBeUsedPerDay
            })
        });
    },
    
    // Placement API
    async getPlacementRecommendation(itemId, containerId) {
        const params = new URLSearchParams();
        if (itemId) params.append('itemId', itemId);
        if (containerId) params.append('containerId', containerId);
        
        return this.fetch(`/placement?${params.toString()}`, { method: 'GET' });
    },
    
    // Rearrangement API
    async getRearrangementRecommendations() {
        return this.fetch('/rearrange', { method: 'GET' });
    },
    
    // Import/Export API
    async importItems(formData) {
        return this.uploadFile('/import/items', formData);
    },
    
    async importContainers(formData) {
        return this.uploadFile('/import/containers', formData);
    },
    
    async exportArrangement() {
        return this.downloadFile('/export/arrangement', { method: 'GET' });
    },
    
    // Logs API
    async getLogs(startDate, endDate, itemId, userId, actionType) {
        const params = new URLSearchParams();
        if (startDate) params.append('startDate', startDate);
        if (endDate) params.append('endDate', endDate);
        if (itemId) params.append('itemId', itemId);
        if (userId) params.append('userId', userId);
        if (actionType) params.append('actionType', actionType);
        
        return this.fetch(`/logs?${params.toString()}`, { method: 'GET' });
    }
};

