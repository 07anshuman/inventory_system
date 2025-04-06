function initSearch() {
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const userIdInput = document.getElementById('user-id');
    const searchResults = document.getElementById('search-results');
    const itemInfo = document.querySelector('.item-info');
    const retrievalSteps = document.querySelector('.retrieval-steps');
    const retrieveButton = document.getElementById('retrieve-button');
    const placeButton = document.getElementById('place-button');
    
    // Current item data
    let currentItem = null;
    
    // Search button click handler
    searchButton.addEventListener('click', async function() {
        const query = searchInput.value.trim();
        const userId = userIdInput.value.trim();
        
        if (!query) {
            window.showError('Please enter an item ID or name');
            return;
        }
        
        try {
            // Determine if input is an ID or name
            const isItemId = /^[a-zA-Z0-9-]+$/.test(query) && query.length <= 20;
            const response = await api.searchItem(
                isItemId ? query : null,
                !isItemId ? query : null,
                userId
            );
            
            if (response.success && response.found) {
                // Store current item
                currentItem = response.item;
                
                // Display item details
                itemInfo.innerHTML = `
                    <h4>${response.item.name}</h4>
                    <p><strong>Item ID:</strong> ${response.item.itemId}</p>
                    <p><strong>Container:</strong> ${response.item.containerId}</p>
                    <p><strong>Zone:</strong> ${response.item.zone}</p>
                    <p><strong>Position:</strong> 
                        (${response.item.position.startCoordinates.width}, 
                         ${response.item.position.startCoordinates.depth}, 
                         ${response.item.position.startCoordinates.height}) to
                        (${response.item.position.endCoordinates.width}, 
                         ${response.item.position.endCoordinates.depth}, 
                         ${response.item.position.endCoordinates.height})
                    </p>
                `;
                
                // Display retrieval steps
                if (response.retrievalSteps && response.retrievalSteps.length > 0) {
                    let stepsHtml = '<h4>Retrieval Steps:</h4><ol>';
                    response.retrievalSteps.forEach(step => {
                        stepsHtml += `<li>${step.action} ${step.itemName} (${step.itemId})</li>`;
                    });
                    stepsHtml += '</ol>';
                    retrievalSteps.innerHTML = stepsHtml;
                } else {
                    retrievalSteps.innerHTML = '<p>No retrieval steps needed.</p>';
                }
                
                // Show results
                searchResults.classList.remove('hidden');
            } else {
                window.showError(response.message || 'Item not found');
                searchResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to search for item');
            searchResults.classList.add('hidden');
        }
    });
    
    // Retrieve button click handler
    retrieveButton.addEventListener('click', async function() {
        if (!currentItem) {
            window.showError('No item selected');
            return;
        }
        
        const userId = userIdInput.value.trim() || 'anonymous';
        
        try {
            const response = await api.retrieveItem(currentItem.itemId, userId);
            
            if (response.success) {
                alert(`Item ${currentItem.name} has been retrieved successfully!`);
                searchResults.classList.add('hidden');
                searchInput.value = '';
            } else {
                window.showError(response.message || 'Failed to retrieve item');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to retrieve item');
        }
    });
    
    // Place button click handler
    placeButton.addEventListener('click', async function() {
        if (!currentItem) {
            window.showError('No item selected');
            return;
        }
        
        const userId = userIdInput.value.trim() || 'anonymous';
        
        // In a real app, you would show a form to input new position
        // For simplicity, we'll use the same position
        try {
            const response = await api.placeItem(
                currentItem.itemId, 
                userId, 
                currentItem.containerId, 
                currentItem.position
            );
            
            if (response.success) {
                alert(`Item ${currentItem.name} has been placed back successfully!`);
                searchResults.classList.add('hidden');
                searchInput.value = '';
            } else {
                window.showError(response.message || 'Failed to place item');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to place item');
        }
    });
}

