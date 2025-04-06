function initSimulation() {
    const nextDayButton = document.getElementById('next-day-button');
    const daysToSimulateInput = document.getElementById('days-to-simulate');
    const fastForwardButton = document.getElementById('fast-forward-button');
    const itemsToUseList = document.getElementById('items-to-use-list');
    const addItemToUseButton = document.getElementById('add-item-to-use-button');
    const simulationResults = document.getElementById('simulation-results');
    const simulationDetails = document.querySelector('.simulation-details');
    
    // Add item to use button click handler
    addItemToUseButton.addEventListener('click', function() {
        const newItem = document.createElement('div');
        newItem.className = 'item-to-use';
        newItem.innerHTML = `
            <input type="text" class="item-id-input" placeholder="Item ID">
            <input type="text" class="item-name-input" placeholder="Item Name">
            <button class="remove-item-button">✕</button>
        `;
        
        // Add event listener to remove button
        newItem.querySelector('.remove-item-button').addEventListener('click', function() {
            itemsToUseList.removeChild(newItem);
        });
        
        itemsToUseList.appendChild(newItem);
    });
    
    // Helper function to get items to be used
    function getItemsToBeUsed() {
        const items = [];
        const itemElements = itemsToUseList.querySelectorAll('.item-to-use');
        
        itemElements.forEach(element => {
            const itemId = element.querySelector('.item-id-input').value.trim();
            const itemName = element.querySelector('.item-name-input').value.trim();
            
            if (itemId || itemName) {
                items.push({
                    itemId: itemId || undefined,
                    name: itemName || undefined
                });
            }
        });
        
        return items;
    }
    
    // Next day button click handler
    nextDayButton.addEventListener('click', async function() {
        const itemsToBeUsed = getItemsToBeUsed();
        
        if (itemsToBeUsed.length === 0) {
            window.showError('Please add at least one item to be used');
            return;
        }
        
        try {
            const response = await api.simulateDay(1, null, itemsToBeUsed);
            displaySimulationResults(response);
        } catch (error) {
            window.showError(error.message || 'Failed to simulate day');
            simulationResults.classList.add('hidden');
        }
    });
    
    // Fast forward button click handler
    fastForwardButton.addEventListener('click', async function() {
        const daysToSimulate = parseInt(daysToSimulateInput.value);
        
        if (isNaN(daysToSimulate) || daysToSimulate <= 0) {
            window.showError('Please enter a valid number of days');
            return;
        }
        
        const itemsToBeUsed = getItemsToBeUsed();
        
        if (itemsToBeUsed.length === 0) {
            window.showError('Please add at least one item to be used');
            return;
        }
        
        try {
            const response = await api.simulateDay(daysToSimulate, null, itemsToBeUsed);
            displaySimulationResults(response);
        } catch (error) {
            window.showError(error.message || 'Failed to simulate days');
            simulationResults.classList.add('hidden');
        }
    });
    
    // Display simulation results
    function displaySimulationResults(response) {
        if (response.success) {
            let resultsHtml = `
                <p><strong>New Date:</strong> ${window.formatDate(response.newDate)}</p>
                
                <h4>Items Used:</h4>
            `;
            
            if (response.changes.itemsUsed && response.changes.itemsUsed.length > 0) {
                resultsHtml += '<ul>';
                response.changes.itemsUsed.forEach(item => {
                    resultsHtml += `
                        <li>
                            <strong>${item.name}</strong> (${item.itemId})
                            <br>Remaining Uses: ${item.remainingUses}
                        </li>
                    `;
                });
                resultsHtml += '</ul>';
            } else {
                resultsHtml += '<p>No items used.</p>';
            }
            
            resultsHtml += '<h4>Items Expired:</h4>';
            
            if (response.changes.itemsExpired && response.changes.itemsExpired.length > 0) {
                resultsHtml += '<ul>';
                response.changes.itemsExpired.forEach(item => {
                    resultsHtml += `
                        <li>
                            <strong>${item.name}</strong> (${item.itemId})
                        </li>
                    `;
                });
                resultsHtml += '</ul>';
            } else {
                resultsHtml += '<p>No items expired.</p>';
            }
            
            resultsHtml += '<h4>Items Depleted:</h4>';
            
            if (response.changes.itemsDepletedToday && response.changes.itemsDepletedToday.length > 0) {
                resultsHtml += '<ul>';
                response.changes.itemsDepletedToday.forEach(item => {
                    resultsHtml += `
                        <li>
                            <strong>${item.name}</strong> (${item.itemId})
                        </li>
                    `;
                });
                resultsHtml += '</ul>';
            } else {
                resultsHtml += '<p>No items depleted.</p>';
            }
            
            simulationDetails.innerHTML = resultsHtml;
            simulationResults.classList.remove('hidden');
        } else {
            window.showError(response.message || 'Simulation failed');
            simulationResults.classList.add('hidden');
        }
    }
}

