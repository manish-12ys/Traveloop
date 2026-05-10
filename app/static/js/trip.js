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
        console.error(e);
    }
}

async function loadItinerary() {
    try {
        const [stopsRes, activitiesRes] = await Promise.all([
            fetch(`/api/trips/${tripId}/stops`),
            fetch(`/api/trips/${tripId}/activities`)
        ]);
        
        const stops = await stopsRes.json();
        const activities = await activitiesRes.json();
        
        renderItinerary(stops, activities);
    } catch (e) {
        console.error('Failed to load itinerary', e);
    }
}

function renderItinerary(stops, activities) {
    const container = document.getElementById('timeline');
    container.innerHTML = '';
    
    if (stops.length === 0) {
        document.getElementById('itinerary-empty').classList.remove('hidden');
        return;
    }
    
    document.getElementById('itinerary-empty').classList.add('hidden');

    stops.forEach(stop => {
        const stopActs = activities.filter(a => a.stop_id === stop.id).sort((a,b) => a.order - b.order);
        
        const stopEl = document.createElement('div');
        stopEl.className = 'mb-10 ml-6';
        stopEl.innerHTML = `
            <span class="absolute flex items-center justify-center w-8 h-8 bg-violet-100 rounded-full -left-4 ring-4 ring-white dark:ring-gray-900 dark:bg-violet-900 text-violet-600 dark:text-violet-400">
                <i class="fas fa-map-marker-alt text-sm"></i>
            </span>
            <div class="flex justify-between items-start mb-2">
                <div>
                    <h3 class="flex items-center text-lg font-bold text-gray-900 dark:text-white">${stop.name} <span class="text-sm font-normal text-gray-500 ml-2">(${stop.location})</span></h3>
                    <time class="block mb-2 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">${DateHelper.format(stop.arrival_date)} to ${DateHelper.format(stop.departure_date)}</time>
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
    const data = {
        name: document.getElementById('stop-name').value,
        location: document.getElementById('stop-location').value,
        arrival_date: document.getElementById('stop-arrival').value,
        departure_date: document.getElementById('stop-departure').value
    };
    
    try {
        const res = await fetch(`/api/trips/${tripId}/stops`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            closeModal('stop-modal');
            loadItinerary();
        }
    } catch (e) { console.error(e); }
}

async function handleActivitySubmit(e) {
    e.preventDefault();
    const data = {
        stop_id: document.getElementById('activity-stop-id').value,
        title: document.getElementById('activity-title').value,
        description: document.getElementById('activity-desc').value,
        start_time: document.getElementById('activity-start').value || null,
        end_time: document.getElementById('activity-end').value || null,
        cost: document.getElementById('activity-cost').value || 0
    };
    
    try {
        const res = await fetch(`/api/trips/${tripId}/activities`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            closeModal('activity-modal');
            loadItinerary();
        }
    } catch (e) { console.error(e); }
}

async function deleteActivity(id) {
    if (!confirm('Delete this activity?')) return;
    try {
        await fetch(`/api/trips/${tripId}/activities/${id}`, { method: 'DELETE' });
        loadItinerary();
    } catch (e) { console.error(e); }
}

async function reorderActivities(activityIds) {
    try {
        await fetch(`/api/trips/${tripId}/activities/reorder`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ activity_ids: activityIds })
        });
    } catch (e) { console.error(e); }
}

// --- Packing Logic ---
async function loadPacking() {
    try {
        const res = await fetch(`/api/trips/${tripId}/packing`);
        const items = await res.json();
        
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
    } catch (e) { console.error(e); }
}

async function handlePackingSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('packing-input');
    try {
        await fetch(`/api/trips/${tripId}/packing`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ item_name: input.value })
        });
        input.value = '';
        loadPacking();
    } catch (e) { console.error(e); }
}

async function togglePacking(id, isPacked) {
    try {
        await fetch(`/api/trips/${tripId}/packing/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ is_packed: isPacked })
        });
        loadPacking(); // Reload to update line-through
    } catch (e) { console.error(e); }
}

async function deletePacking(id) {
    try {
        await fetch(`/api/trips/${tripId}/packing/${id}`, { method: 'DELETE' });
        loadPacking();
    } catch (e) { console.error(e); }
}

// --- Budget Logic ---
async function loadBudget() {
    try {
        const res = await fetch(`/api/trips/${tripId}/budget`);
        if (!res.ok) return; // silently skip if not authorized
        const items = await res.json();
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
        const expectedTotal = items.reduce((sum, item) => sum + (item.expected_amount || 0), 0);
        const actualTotal = items.reduce((sum, item) => sum + (item.actual_amount || 0), 0);
        const remaining = expectedTotal - actualTotal;
        
        document.getElementById('budget-total').textContent = `₹${expectedTotal.toLocaleString('en-IN')}`;
        document.getElementById('budget-spent').textContent = `₹${actualTotal.toLocaleString('en-IN')}`;
        document.getElementById('budget-remaining').textContent = `₹${remaining.toLocaleString('en-IN')}`;
    } catch (e) { console.error('loadBudget error:', e); }
}

async function handleBudgetSubmit(e) {
    e.preventDefault();
    const data = {
        category: document.getElementById('budget-category').value,
        description: document.getElementById('budget-desc').value,
        expected_amount: parseFloat(document.getElementById('budget-expected').value) || 0,
        actual_amount: parseFloat(document.getElementById('budget-actual').value) || 0
    };
    try {
        const res = await fetch(`/api/trips/${tripId}/budget`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            closeModal('budget-modal');
            loadBudget();
        } else {
            const err = await res.json().catch(() => ({}));
            alert('Failed to save expense: ' + (err.error || res.statusText));
        }
    } catch (e) { 
        console.error('handleBudgetSubmit error:', e);
        alert('Network error saving expense. Please try again.');
    }
}

async function deleteBudget(id) {
    if (!confirm('Delete this expense?')) return;
    try {
        await fetch(`/api/trips/${tripId}/budget/${id}`, { method: 'DELETE' });
        loadBudget();
    } catch (e) { console.error(e); }
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
    } catch (e) { console.error('loadNotes error:', e); }
}

async function handleNoteSubmit(e) {
    e.preventDefault();
    const data = {
        title: document.getElementById('note-title').value,
        content: document.getElementById('note-content').value
    };
    try {
        const res = await fetch(`/api/trips/${tripId}/notes`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            closeModal('note-modal');
            loadNotes();
        } else {
            const err = await res.json().catch(() => ({}));
            alert('Failed to save note: ' + (err.error || res.statusText));
        }
    } catch (e) {
        console.error('handleNoteSubmit error:', e);
        alert('Network error saving note. Please try again.');
    }
}

async function deleteNote(id) {
    if (!confirm('Delete this note?')) return;
    try {
        await fetch(`/api/trips/${tripId}/notes/${id}`, { method: 'DELETE' });
        loadNotes();
    } catch (e) { console.error(e); }
}

function openNoteModal() { openModal('note-modal'); }
