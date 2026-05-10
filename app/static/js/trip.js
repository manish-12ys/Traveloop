/**
 * Trip API & UI interactions for Phase 3
 */

const tripId = document.getElementById('trip-app')?.dataset.tripId;

document.addEventListener('DOMContentLoaded', () => {
    if (!tripId) return;

    // Load initial data
    loadTripDetails();
    loadItinerary();
    loadBudget();
    loadPacking();
    loadNotes();

    // Event Listeners
    document.getElementById('stop-form').addEventListener('submit', handleStopSubmit);
    document.getElementById('activity-form').addEventListener('submit', handleActivitySubmit);
    document.getElementById('packing-form').addEventListener('submit', handlePackingSubmit);
    document.getElementById('budget-form')?.addEventListener('submit', handleBudgetSubmit);
    document.getElementById('note-form')?.addEventListener('submit', handleNoteSubmit);
});

// --- UI Helpers ---
function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
    // Reset forms if applicable
    const form = document.querySelector(`#${id} form`);
    if (form) form.reset();
}

function openStopModal() {
    openModal('stop-modal');
}

function openActivityModal(stopId) {
    document.getElementById('activity-stop-id').value = stopId;
    openModal('activity-modal');
}

// --- Data Loading ---
async function loadTripDetails() {
    try {
        const res = await fetch(`/api/dashboard/trips/${tripId}`);
        if (!res.ok) return;
        const trip = await res.json();
        
        document.getElementById('trip-title').textContent = trip.title;
        const start = DateHelper.format(trip.start_date);
        const end = DateHelper.format(trip.end_date);
        document.getElementById('trip-dates').innerHTML = `<i class="far fa-calendar mr-2"></i><span>${start} - ${end}</span>`;
    } catch (e) {
        Notify.error('Failed to load trip details');
    }
}

async function loadItinerary() {
    try {
        const [stopsRes, activitiesRes, weatherRes, travelRes] = await Promise.all([
            fetch(`/api/trips/${tripId}/stops`),
            fetch(`/api/trips/${tripId}/activities`),
            fetch(`/api/itinerary/${tripId}/weather`),
            fetch(`/api/itinerary/${tripId}/travel-times`)
        ]);
        
        const stops = await stopsRes.json();
        const activities = await activitiesRes.json();
        const weather = await weatherRes.json();
        const travelTimes = await travelRes.json();
        
        renderItinerary(stops, activities, weather, travelTimes);
        if (window.locationManager) {
            window.locationManager.renderStopsOnMap(stops);
        }
    } catch (e) {
        Notify.error('Failed to load itinerary');
    }
}

function renderItinerary(stops, activities, weather = {}, travelTimes = []) {
    const container = document.getElementById('timeline');
    container.innerHTML = '';
    
    if (stops.length === 0) {
        document.getElementById('itinerary-empty').classList.remove('hidden');
        return;
    }
    
    document.getElementById('itinerary-empty').classList.add('hidden');

    stops.forEach((stop, index) => {
        const stopActs = activities.filter(a => a.stop_id === stop.id).sort((a,b) => a.order - b.order);
        const stopWeather = weather[stop.id] || [];
        const currentTravel = travelTimes.find(t => t.from_stop_id === stop.id);

        // Weather summary for the stop
        let weatherHtml = '';
        if (stopWeather.length > 0) {
            const forecast = stopWeather[0]; // Just show the first one as summary
            weatherHtml = `
                <div class="flex items-center gap-2 bg-white dark:bg-gray-800 px-3 py-1 rounded-full border border-gray-100 dark:border-gray-700 shadow-sm text-xs mt-2">
                    <img src="https://openweathermap.org/img/wn/${forecast.icon}.png" class="w-6 h-6" alt="weather">
                    <span class="font-bold dark:text-white">${Math.round(forecast.temp)}°C</span>
                    <span class="text-gray-400 capitalize">${forecast.description}</span>
                </div>
            `;
        }

        const stopEl = document.createElement('div');
        stopEl.className = 'mb-10 ml-6 relative';
        stopEl.innerHTML = `
            <span class="absolute flex items-center justify-center w-8 h-8 bg-violet-100 rounded-full -left-4 ring-4 ring-white dark:ring-gray-900 dark:bg-violet-900 text-violet-600 dark:text-violet-400">
                <i class="fas fa-map-marker-alt text-sm"></i>
            </span>
            <div class="flex justify-between items-start mb-2">
                <div>
                    <h3 class="flex items-center text-lg font-bold text-gray-900 dark:text-white">${stop.name} <span class="text-sm font-normal text-gray-500 ml-2">(${stop.location})</span></h3>
                    <time class="block mb-2 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">${DateHelper.format(stop.arrival_date)} to ${DateHelper.format(stop.departure_date)}</time>
                    ${weatherHtml}
                </div>
                <button onclick="openActivityModal(${stop.id})" class="text-xs bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 rounded px-2 py-1 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <i class="fas fa-plus mr-1"></i> Activity
                </button>
            </div>
            
            <div class="activities-list space-y-3 mt-4" data-stop-id="${stop.id}">
                ${stopActs.map(act => `
                    <div class="activity-item bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex gap-4 cursor-move" data-id="${act.id}">
                        <div class="flex flex-col items-center justify-center text-gray-400">
                            <i class="fas fa-grip-vertical"></i>
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between">
                                <h4 class="font-bold text-gray-900 dark:text-white">${act.title}</h4>
                                ${act.cost ? `<span class="text-emerald-500 font-medium">₹${act.cost.toLocaleString('en-IN')}</span>` : ''}
                            </div>
                            ${act.description ? `<p class="text-sm text-gray-500 mt-1">${act.description}</p>` : ''}
                            ${act.start_time ? `<div class="text-xs text-gray-400 mt-2"><i class="far fa-clock mr-1"></i> ${DateHelper.formatDateTime(act.start_time)}</div>` : ''}
                        </div>
                        <button onclick="deleteActivity(${act.id})" class="text-gray-400 hover:text-red-500"><i class="fas fa-trash"></i></button>
                    </div>
                `).join('')}
            </div>

            ${currentTravel ? `
                <div class="absolute -bottom-8 left-0 flex items-center gap-2 text-xs text-gray-400 bg-gray-50 dark:bg-gray-900/50 px-2 py-1 rounded">
                    <i class="fas fa-car"></i>
                    <span>Travel to next stop: <b>${currentTravel.info.formatted_duration}</b></span>
                    <span class="text-gray-300">|</span>
                    <span>${(currentTravel.info.distance / 1000).toFixed(1)} km</span>
                </div>
            ` : ''}
        `;
        
        container.appendChild(stopEl);
        
        // Init Sortable for this stop's activities
        const actList = stopEl.querySelector('.activities-list');
        new Sortable(actList, {
            group: 'activities',
            animation: 150,
            ghostClass: 'drag-ghost',
            onEnd: function (evt) {
                // Determine new order and save
                const stopId = evt.to.dataset.stopId;
                const itemEls = evt.to.children;
                const activityIds = Array.from(itemEls).map(el => parseInt(el.dataset.id));
                reorderActivities(activityIds);
            }
        });
    });
}

// --- Form Handlers ---
async function handleStopSubmit(e) {
    e.preventDefault();
    Loading.show('Saving stop...');
    const data = {
        name: document.getElementById('stop-name').value,
        location: document.getElementById('stop-location').value,
        arrival_date: document.getElementById('stop-arrival').value,
        departure_date: document.getElementById('stop-departure').value,
        latitude: window.locationManager ? window.locationManager.selectedLat : null,
        longitude: window.locationManager ? window.locationManager.selectedLon : null
    };
    
    try {
        const res = await fetch(`/api/trips/${tripId}/stops`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': API._getCsrfToken()
            },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            Notify.success('Stop added successfully!');
            closeModal('stop-modal');
            loadItinerary();
        } else {
            const err = await res.json();
            Notify.error(err.error || 'Failed to add stop');
        }
    } catch (e) { 
        Notify.error('Network error. Please try again.');
    } finally {
        Loading.hide();
    }
}

async function handleActivitySubmit(e) {
    e.preventDefault();
    Loading.show('Adding activity...');
    const data = {
        stop_id: document.getElementById('activity-stop-id').value,
        title: document.getElementById('activity-title').value,
        description: document.getElementById('activity-desc').value,
        start_time: document.getElementById('activity-start').value || null,
        end_time: document.getElementById('activity-end').value || null,
        cost: document.getElementById('activity-cost').value || 0
    };
    
    try {
        await API.post(`/trips/${tripId}/activities`, data);
        Notify.success('Activity added');
        closeModal('activity-modal');
        loadItinerary();
    } catch (e) { 
        Notify.error('Failed to add activity');
    } finally {
        Loading.hide();
    }
}

async function deleteActivity(id) {
    if (!confirm('Delete this activity?')) return;
    Loading.show('Deleting...');
    try {
        await API.delete(`/trips/${tripId}/activities/${id}`);
        Notify.success('Activity deleted');
        loadItinerary();
    } catch (e) { 
        Notify.error('Error deleting activity');
    } finally {
        Loading.hide();
    }
}

async function reorderActivities(activityIds) {
    try {
        await API.put(`/trips/${tripId}/activities/reorder`, { activity_ids: activityIds });
    } catch (e) { 
        Notify.error('Failed to save new order');
        loadItinerary();
    }
}

// --- Packing Logic ---
async function loadPacking() {
    try {
        const [itemsRes, statsRes] = await Promise.all([
            fetch(`/api/trips/${tripId}/packing`),
            fetch(`/api/itinerary/${tripId}/stats`)
        ]);
        const items = await itemsRes.json();
        const stats = await statsRes.json();
        
        const list = document.getElementById('packing-list');
        list.innerHTML = items.map(item => `
            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div class="flex items-center gap-3">
                    <input type="checkbox" ${item.is_packed ? 'checked' : ''} onchange="togglePacking(${item.id}, this.checked)" class="w-5 h-5 text-violet-600 bg-white border-gray-300 rounded focus:ring-violet-500 dark:focus:ring-violet-600 dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600">
                    <span class="${item.is_packed ? 'line-through text-gray-400' : 'text-gray-900 dark:text-white'}">${item.item_name}</span>
                </div>
                <button onclick="deletePacking(${item.id})" class="text-gray-400 hover:text-red-500"><i class="fas fa-times"></i></button>
            </div>
        `).join('');

        // Update progress bar
        const percent = stats.packing.percent || 0;
        document.getElementById('packing-percent').textContent = `${percent}% Packed`;
        document.getElementById('packing-progress-bar').style.width = `${percent}%`;
    } catch (e) { Notify.error('Failed to load packing list'); }
}

async function handlePackingSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('packing-input');
    Loading.show('Adding item...');
    try {
        await API.post(`/trips/${tripId}/packing`, { item_name: input.value });
        Notify.success('Item added');
        input.value = '';
        loadPacking();
    } catch (e) { 
        Notify.error('Failed to add item');
    } finally {
        Loading.hide();
    }
}

async function togglePacking(id, isPacked) {
    try {
        await API.put(`/trips/${tripId}/packing/${id}`, { is_packed: isPacked });
        loadPacking();
    } catch (e) { Notify.error('Failed to update item'); }
}

async function deletePacking(id) {
    try {
        await API.delete(`/trips/${tripId}/packing/${id}`);
        Notify.success('Item removed');
        loadPacking();
    } catch (e) { Notify.error('Failed to remove item'); }
}

// --- Budget Logic ---
async function loadBudget() {
    try {
        const [itemsRes, statsRes] = await Promise.all([
            fetch(`/api/trips/${tripId}/budget`),
            fetch(`/api/itinerary/${tripId}/stats`)
        ]);
        
        if (!itemsRes.ok || !statsRes.ok) return;
        const items = await itemsRes.json();
        const stats = await statsRes.json();
        if (!Array.isArray(items)) return;
        
        const list = document.getElementById('budget-list');
        list.innerHTML = items.length === 0 
            ? `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-400"><i class="fas fa-receipt mr-2"></i>No expenses yet. Click "Add Expense" to get started.</td></tr>`
            : items.map(item => `
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">${item.category}</td>
                <td class="px-6 py-4">${item.description}</td>
                <td class="px-6 py-4 text-right">₹${item.expected_amount.toLocaleString('en-IN')}</td>
                <td class="px-6 py-4 text-right">₹${item.actual_amount.toLocaleString('en-IN')}</td>
                <td class="px-6 py-4 text-right">
                    <button onclick="deleteBudget(${item.id})" class="text-gray-400 hover:text-red-500"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
        
        // Update summary
        const s = stats.budget;
        document.getElementById('budget-total').textContent = `₹${s.expected_total.toLocaleString('en-IN')}`;
        document.getElementById('budget-spent').textContent = `₹${s.actual_total.toLocaleString('en-IN')}`;
        document.getElementById('budget-remaining').textContent = `₹${s.remaining.toLocaleString('en-IN')}`;

        renderBudgetCharts(s);
    } catch (e) { Notify.error('Failed to load budget data'); }
}

let budgetPieChart = null;
let budgetBarChart = null;

function renderBudgetCharts(stats) {
    const ctxPie = document.getElementById('budgetPieChart')?.getContext('2d');
    const ctxBar = document.getElementById('budgetBarChart')?.getContext('2d');
    
    if (!ctxPie || !ctxBar) return;

    // Categories Chart
    if (budgetPieChart) budgetPieChart.destroy();
    
    const catLabels = Object.keys(stats.categories);
    const catData = Object.values(stats.categories);
    
    if (catLabels.length === 0) {
        catLabels.push('No Expenses');
        catData.push(1);
    }

    budgetPieChart = new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: catLabels,
            datasets: [{
                data: catData,
                backgroundColor: ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#6366f1'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, color: '#94a3b8' } }
            }
        }
    });

    // Budget vs Actual
    if (budgetBarChart) budgetBarChart.destroy();
    budgetBarChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Budgeted', 'Spent'],
            datasets: [{
                label: 'Amount (₹)',
                data: [stats.expected_total, stats.actual_total],
                backgroundColor: ['#e2e8f0', '#8b5cf6'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

async function handleBudgetSubmit(e) {
    e.preventDefault();
    Loading.show('Saving expense...');
    const data = {
        category: document.getElementById('budget-category').value,
        description: document.getElementById('budget-desc').value,
        expected_amount: parseFloat(document.getElementById('budget-expected').value) || 0,
        actual_amount: parseFloat(document.getElementById('budget-actual').value) || 0
    };
    try {
        await API.post(`/trips/${tripId}/budget`, data);
        Notify.success('Expense added');
        closeModal('budget-modal');
        loadBudget();
    } catch (e) { 
        Notify.error('Failed to save expense');
    } finally {
        Loading.hide();
    }
}

async function deleteBudget(id) {
    if (!confirm('Delete this expense?')) return;
    Loading.show('Deleting...');
    try {
        await API.delete(`/trips/${tripId}/budget/${id}`);
        Notify.success('Expense deleted');
        loadBudget();
    } catch (e) { 
        Notify.error('Failed to delete expense');
    } finally {
        Loading.hide();
    }
}

function openBudgetModal() { openModal('budget-modal'); }

// --- Notes Logic ---
async function loadNotes() {
    try {
        const res = await fetch(`/api/trips/${tripId}/notes`);
        if (!res.ok) return; // silently skip if not authorized
        const notes = await res.json();
        if (!Array.isArray(notes)) return;
        
        const list = document.getElementById('notes-list');
        if (notes.length === 0) {
            list.innerHTML = `<div class="col-span-3 text-center py-12 text-gray-400"><i class="fas fa-sticky-note text-3xl mb-3 block"></i>No notes yet. Click "Add Note" to jot something down.</div>`;
            return;
        }
        list.innerHTML = notes.map(note => `
            <div class="bg-yellow-50 dark:bg-yellow-900/20 p-5 rounded-xl shadow-sm border border-yellow-100 dark:border-yellow-800/50 relative group">
                <h3 class="font-bold text-gray-900 dark:text-yellow-500 mb-2">${note.title}</h3>
                <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">${note.content}</p>
                <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick="deleteNote(${note.id})" class="text-gray-400 hover:text-red-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm">
                        <i class="fas fa-trash text-xs"></i>
                    </button>
                </div>
            </div>
        `).join('');
    } catch (e) { Notify.error('Failed to load notes'); }
}

async function handleNoteSubmit(e) {
    e.preventDefault();
    Loading.show('Saving note...');
    const data = {
        title: document.getElementById('note-title').value,
        content: document.getElementById('note-content').value
    };
    try {
        await API.post(`/trips/${tripId}/notes`, data);
        Notify.success('Note saved');
        closeModal('note-modal');
        loadNotes();
    } catch (e) {
        Notify.error('Failed to save note. Please try again.');
    } finally {
        Loading.hide();
    }
}

async function deleteNote(id) {
    if (!confirm('Delete this note?')) return;
    Loading.show('Deleting...');
    try {
        await API.delete(`/trips/${tripId}/notes/${id}`);
        Notify.success('Note deleted');
        loadNotes();
    } catch (e) { 
        Notify.error('Failed to delete note');
    } finally {
        Loading.hide();
    }
}

function openNoteModal() { openModal('note-modal'); }

// --- Sharing Logic ---
async function openShareModal() {
    try {
        const data = await API.get(`/share/${tripId}`);
        updateShareModalUI(data);
        openModal('share-modal');
    } catch (e) {
        Notify.error('Failed to load sharing info');
    }
}

function updateShareModalUI(data) {
    const inactive = document.getElementById('share-inactive-state');
    const active = document.getElementById('share-active-state');
    const input = document.getElementById('share-url-input');
    const toggle = document.getElementById('share-active-toggle');
    const publicToggle = document.getElementById('trip-public-toggle');

    if (data.token) {
        inactive.classList.add('hidden');
        active.classList.remove('hidden');
        input.value = data.full_url;
        toggle.checked = data.is_active;
        publicToggle.checked = data.is_public;
    } else {
        inactive.classList.remove('hidden');
        active.classList.add('hidden');
    }
}

async function generateShareLink() {
    Loading.show('Generating link...');
    try {
        const data = await API.get(`/share/${tripId}`);
        updateShareModalUI(data);
        Notify.success('Public link generated!');
    } catch (e) {
        Notify.error('Failed to generate link');
    } finally {
        Loading.hide();
    }
}

async function toggleShareStatus(isActive) {
    try {
        const data = await API.post(`/share/${tripId}/toggle`, { is_active: isActive });
        updateShareModalUI(data);
        Notify.success(`Link ${isActive ? 'activated' : 'deactivated'}`);
    } catch (e) {
        Notify.error('Failed to update link status');
        document.getElementById('share-active-toggle').checked = !isActive;
    }
}

function copyShareLink() {
    const input = document.getElementById('share-url-input');
    input.select();
    document.execCommand('copy');
    Notify.success('Link copied to clipboard!');
}

async function togglePublicStatus(isPublic) {
    try {
        await API.post(`/trips/${tripId}/visibility`, { is_public: isPublic });
        Notify.success(`Trip is now ${isPublic ? 'public' : 'private'}`);
    } catch (e) {
        Notify.error('Failed to update visibility');
        document.getElementById('trip-public-toggle').checked = !isPublic;
    }
}
