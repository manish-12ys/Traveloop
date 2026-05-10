/**
 * Location & Map Management for Phase 4
 */

class LocationManager {
    constructor(tripId) {
        this.tripId = tripId;
        this.map = null;
        this.markers = [];
        this.searchTimeout = null;
        this.pendingStops = null;
        this.init();
    }

    init() {
        this.initMap();
        this.setupEventListeners();
    }

    initMap() {
        // Initialize Leaflet map
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        const mountMap = () => {
            if (this.map) {
                this.map.invalidateSize();
                if (this.pendingStops) {
                    const stopsToRender = this.pendingStops;
                    this.pendingStops = null;
                    this.renderStopsOnMap(stopsToRender);
                }
                return;
            }

            this.map = L.map('map', {
                zoomControl: false,
                scrollWheelZoom: true
            }).setView([20, 0], 2);

            // CartoDB Dark Matter tiles for a premium dark look
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(this.map);

            // Add zoom control to bottom right
            L.control.zoom({ position: 'bottomright' }).addTo(this.map);

            // Refresh size after a short delay to ensure container is fully rendered
            setTimeout(() => this.map.invalidateSize(), 250);

            if (this.pendingStops) {
                const stopsToRender = this.pendingStops;
                this.pendingStops = null;
                setTimeout(() => this.renderStopsOnMap(stopsToRender), 0);
            }
        };

        if (mapContainer.offsetParent === null) {
            const observer = new MutationObserver(() => {
                if (mapContainer.offsetParent !== null) {
                    observer.disconnect();
                    mountMap();
                }
            });

            observer.observe(mapContainer.closest('#itinerary') || document.body, {
                attributes: true,
                attributeFilter: ['class', 'style']
            });

            this._mapObserver = observer;
            return;
        }

        mountMap();
    }

    setupEventListeners() {
        const citySearch = document.getElementById('city-search');
        const resultsDropdown = document.getElementById('search-results');

        if (citySearch) {
            citySearch.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                const query = e.target.value;
                if (query.length < 2) {
                    resultsDropdown.classList.add('hidden');
                    return;
                }

                this.searchTimeout = setTimeout(() => this.searchCities(query), 300);
            });
        }

        // Close dropdown on click outside
        document.addEventListener('click', (e) => {
            if (resultsDropdown && !resultsDropdown.contains(e.target) && e.target !== citySearch) {
                resultsDropdown.classList.add('hidden');
            }
        });

        // Listen for tab changes to fix map sizing
        const itineraryTab = document.getElementById('itinerary-tab');
        if (itineraryTab) {
            itineraryTab.addEventListener('click', () => {
                setTimeout(() => {
                    if (this.map) {
                        this.map.invalidateSize();
                    } else {
                        this.initMap();
                    }
                }, 100);
            });
        }
    }

    refreshMap() {
        if (this.map) {
            setTimeout(() => this.map.invalidateSize(), 50);
        } else {
            this.initMap();
        }
    }

    async searchCities(query) {
        const dropdown = document.getElementById('search-results');
        const searchInput = document.getElementById('city-search');
        
        // Add loading spinner icon if not present
        let spinner = searchInput.parentElement.querySelector('.search-spinner');
        if (!spinner) {
            spinner = document.createElement('i');
            spinner.className = 'fas fa-spinner fa-spin absolute right-3 top-3 text-violet-500 search-spinner hidden';
            searchInput.parentElement.appendChild(spinner);
        }
        
        try {
            spinner.classList.remove('hidden');
            const res = await fetch(`/api/locations/cities/autocomplete?q=${encodeURIComponent(query)}`);
            const cities = await res.json();
            this.renderSearchResults(cities);
        } catch (e) {
            console.error('City search failed', e);
        } finally {
            spinner.classList.add('hidden');
        }
    }

    renderSearchResults(cities) {
        const dropdown = document.getElementById('search-results');
        if (!dropdown) return;

        if (cities.length === 0) {
            dropdown.classList.add('hidden');
            return;
        }

        dropdown.innerHTML = cities.map(city => `
            <div class="p-3 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-0" 
                 onclick="window.locationManager.selectCity(${JSON.stringify(city).replace(/"/g, '&quot;')})">
                <div class="font-bold text-gray-900 dark:text-white">${city.name}</div>
                <div class="text-xs text-gray-500">${city.region}, ${city.country}</div>
            </div>
        `).join('');
        dropdown.classList.remove('hidden');
    }

    selectCity(city) {
        // Center map
        if (this.map) {
            this.map.setView([city.latitude, city.longitude], 12);
            this.addMarker(city.latitude, city.longitude, city.name);
        }

        // Pre-fill stop modal if open
        const stopName = document.getElementById('stop-name');
        const stopLocation = document.getElementById('stop-location');
        if (stopName) stopName.value = city.name;
        if (stopLocation) stopLocation.value = `${city.region}, ${city.country}`;

        // Store selected coordinates for submission
        this.selectedLat = city.latitude;
        this.selectedLon = city.longitude;

        document.getElementById('search-results').classList.add('hidden');
        document.getElementById('city-search').value = city.name;
        
        // Fetch attractions for this area
        this.fetchAttractions(city.latitude, city.longitude);
    }

    async fetchAttractions(lat, lon) {
        try {
            const res = await fetch(`/api/locations/attractions?lat=${lat}&lon=${lon}`);
            const attractions = await res.json();
            this.renderAttractions(attractions);
        } catch (e) {
            console.error('Failed to fetch attractions', e);
        }
    }

    renderAttractions(attractions) {
        const container = document.getElementById('attractions-container');
        if (!container) return;

        container.innerHTML = attractions.length === 0 
            ? '<p class="text-gray-500 text-sm">No attractions found in this area.</p>'
            : attractions.map(attr => `
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700 flex justify-between items-center">
                    <div>
                        <h4 class="text-sm font-bold dark:text-white">${attr.name}</h4>
                        <p class="text-xs text-gray-400">${attr.kinds.split(',')[0].replace(/_/g, ' ')}</p>
                    </div>
                    <button onclick="window.locationManager.addAttractionAsActivity(${JSON.stringify(attr).replace(/"/g, '&quot;')})" 
                            class="text-violet-600 hover:text-violet-700 text-xs font-medium">
                        <i class="fas fa-plus"></i> Add
                    </button>
                </div>
            `).join('');

        // Add markers for attractions
        attractions.forEach(attr => {
            this.addMarker(attr.latitude, attr.longitude, attr.name, 'amber');
        });
    }

    addMarker(lat, lon, title, color = 'violet') {
        const marker = L.marker([lat, lon]).addTo(this.map)
            .bindPopup(title);
        this.markers.push(marker);
        return marker;
    }

    renderStopsOnMap(stops) {
        if (!this.map) {
            this.pendingStops = Array.isArray(stops) ? stops : [];
            this.initMap();
            return;
        }
        this.clearMarkers();
        
        const coords = [];
        stops.forEach(stop => {
            if (stop.latitude && stop.longitude) {
                this.addMarker(stop.latitude, stop.longitude, stop.name);
                coords.push([stop.latitude, stop.longitude]);
            }
        });

        if (coords.length > 0) {
            // Draw route line
            if (this.routeLine) this.map.removeLayer(this.routeLine);
            this.routeLine = L.polyline(coords, {color: '#7c3aed', weight: 3, opacity: 0.6, dashArray: '5, 10'}).addTo(this.map);
            
            // Fit bounds
            const bounds = L.latLngBounds(coords);
            this.map.fitBounds(bounds, {padding: [50, 50]});
        } else {
            this.map.setView([20, 0], 2);
        }

        this.map.invalidateSize();
    }

    clearMarkers() {
        this.markers.forEach(m => this.map.removeLayer(m));
        this.markers = [];
    }

    async addAttractionAsActivity(attr) {
        const stopName = document.getElementById('stop-name');
        const stopLocation = document.getElementById('stop-location');

        if (!stopName || !stopLocation) return;

        stopName.value = attr.name;
        stopLocation.value = attr.name;

        // Open the stop modal so the attraction is added as a stop in the itinerary.
        openModal('stop-modal');
    }
}

// Global instance
window.locationManager = new LocationManager(tripId);
