// Custom drag and drop functionality for channel selection

// Store for dropped channels
window.droppedChannels = [];

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', function() {
    initializeDragDrop();
});

// Re-initialize after Dash updates
if (window.dash_clientside) {
    window.dash_clientside.clientside = {
        setup_drag_drop: function() {
            setTimeout(initializeDragDrop, 100);
            return window.dash_clientside.no_update;
        }
    };
}

function initializeDragDrop() {
    console.log('Initializing drag and drop...');

    // Set up drag start for all draggable channels
    const draggableItems = document.querySelectorAll('[draggable="true"]');
    draggableItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });

    // Set up drop zone
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);
    }
}

function handleDragStart(e) {
    console.log('Drag started');
    const itemId = e.target.id;

    // Extract channel ID from the element's ID
    try {
        const idData = JSON.parse(itemId);
        const channelId = idData.channel;
        e.dataTransfer.setData('text/plain', channelId);
        e.dataTransfer.effectAllowed = 'copy';
        e.target.style.opacity = '0.5';
        console.log('Dragging channel:', channelId);
    } catch (err) {
        console.error('Error parsing channel ID:', err);
    }
}

function handleDragEnd(e) {
    e.target.style.opacity = '1';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    e.currentTarget.style.backgroundColor = '#e3f2fd';
    e.currentTarget.style.borderColor = '#2196F3';
}

function handleDragLeave(e) {
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';

    const channelId = e.dataTransfer.getData('text/plain');
    console.log('Dropped channel:', channelId);

    if (channelId) {
        // Add to global store if not already present
        if (!window.droppedChannels.includes(channelId)) {
            window.droppedChannels.push(channelId);
            console.log('Updated channels:', window.droppedChannels);

            // Trigger Dash callback by setting a value on a hidden div
            const triggerDiv = document.getElementById('drop-trigger');
            if (triggerDiv) {
                triggerDiv.setAttribute('data-channels', JSON.stringify(window.droppedChannels));
                triggerDiv.setAttribute('data-timestamp', Date.now());
            }
        }
    }
}

// Function to remove channel
function removeChannel(channelId) {
    const index = window.droppedChannels.indexOf(channelId);
    if (index > -1) {
        window.droppedChannels.splice(index, 1);
        const triggerDiv = document.getElementById('drop-trigger');
        if (triggerDiv) {
            triggerDiv.setAttribute('data-channels', JSON.stringify(window.droppedChannels));
            triggerDiv.setAttribute('data-timestamp', Date.now());
        }
    }
}

// Function to clear all channels
function clearAllChannels() {
    window.droppedChannels = [];
    const triggerDiv = document.getElementById('drop-trigger');
    if (triggerDiv) {
        triggerDiv.setAttribute('data-channels', JSON.stringify(window.droppedChannels));
        triggerDiv.setAttribute('data-timestamp', Date.now());
    }
}

// Expose functions to global scope
window.removeChannel = removeChannel;
window.clearAllChannels = clearAllChannels;
