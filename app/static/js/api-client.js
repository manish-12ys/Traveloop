/**
 * API Client for Traveloop Dashboard
 * Handles all API calls to the backend
 */

const apiClient = {
    baseURL: '/api/dashboard',
    
    /**
     * Make a fetch request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `API Error: ${response.status}`);
        }
        
        return response.json();
    },
    
    /**
     * Get user profile
     */
    async getProfile() {
        return this.request('/profile');
    },
    
    /**
     * Get user's trips with pagination
     */
    async getTrips(limit = 10, offset = 0) {
        return this.request(`/trips?limit=${limit}&offset=${offset}`);
    },
    
    /**
     * Get active/upcoming trips
     */
    async getActiveTrips() {
        return this.request('/active-trips');
    },
    
    /**
     * Get past trips
     */
    async getPastTrips(limit = 5) {
        return this.request(`/past-trips?limit=${limit}`);
    },
    
    /**
     * Get dashboard statistics
     */
    async getDashboardStats() {
        return this.request('/stats');
    },
    
    /**
     * Create a new trip
     */
    async createTrip(tripData) {
        return this.request('/trips', {
            method: 'POST',
            body: JSON.stringify(tripData),
        });
    },
    
    /**
     * Update an existing trip
     */
    async updateTrip(tripId, tripData) {
        return this.request(`/trips/${tripId}`, {
            method: 'PUT',
            body: JSON.stringify(tripData),
        });
    },
    
    /**
     * Delete a trip
     */
    async deleteTrip(tripId) {
        return this.request(`/trips/${tripId}`, {
            method: 'DELETE',
        });
    },
};
