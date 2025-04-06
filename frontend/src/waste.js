function initWaste() {
    const identifyWasteButton = document.getElementById('identify-waste-button');
    const wasteResults = document.getElementById('waste-results');
    const wasteItemsList = document.querySelector('.waste-items-list');
    
    const undockingContainerInput = document.getElementById('undocking-container');
    const undockingDateInput = document.getElementById('undocking-date');
    const maxWeightInput = document.getElementById('max-weight');
    const generatePlanButton = document.getElementById('generate-plan-button');
    
    const returnPlanResults = document.getElementById('return-plan-results');
    const returnPlanDetails = document.querySelector('.return-plan-details');
    const completeUndockingButton = document.getElementById('complete-undocking-button');
    
    // Current undocking container
    let currentUndockingContainer = null;
    
    // Identify waste button click handler
    identifyWasteButton.addEventListener('click', async function() {
        try {
            const response = await api.identifyWaste();
            
            if (response.success) {
                if (response.wasteItems && response.wasteItems.length > 0) {
                    let itemsHtml = '<ul>';
                    response.wasteItems.forEach(item => {
                        itemsHtml += `
                            <li>
                                <strong>${item.name}</strong> (${item.itemId})
                                <br>Reason: ${item.reason}
                                <br>Container: ${item.containerId}
                            </li>
                        `;
                    });
                    itemsHtml += '</ul>';
                    wasteItemsList.innerHTML = itemsHtml;
                } else {
                    wasteItemsList.innerHTML = '<p>No waste items found.</p>';
                }
                
                wasteResults.classList.remove('hidden');
            } else {
                window.showError(response.message || 'Failed to identify waste items');
                wasteResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to identify waste items');
            wasteResults.classList.add('hidden');
        }
    });
    
    // Generate return plan button click handler
    generatePlanButton.addEventListener('click', async function() {
        const undockingContainer = undockingContainerInput.value.trim();
        const undockingDate = undockingDateInput.value;
        const maxWeight = maxWeightInput.value.trim();
        
        if (!undockingContainer) {
            window.showError('Please enter an undocking container ID');
            return;
        }
        
        if (!undockingDate) {
            window.showError('Please select an undocking date');
            return;
        }
        
        if (!maxWeight || isNaN(maxWeight) || Number(maxWeight) <= 0) {
            window.showError('Please enter a valid maximum weight');
            return;
        }
        
        try {
            const response = await api.generateReturnPlan(
                undockingContainer,
                new Date(undockingDate).toISOString(),
                Number(maxWeight)
            );
            
            if (response.success) {
                // Store current undocking container
                currentUndockingContainer = undockingContainer;
                
                // Display return plan
                let planHtml = '<h4>Return Plan Steps:</h4>';
                
                if (response.returnPlan && response.returnPlan.length > 0) {
                    planHtml += '<ol>';
                    response.returnPlan.forEach(step => {
                        planHtml += `
                            <li>
                                Move ${step.itemName} (${step.itemId})
                                from ${step.fromContainer} to ${step.toContainer}
                            </li>
                        `;
                    });
                    planHtml += '</ol>';
                } else {
                    planHtml += '<p>No steps needed.</p>';
                }
                
                // Display retrieval steps
                if (response.retrievalSteps && response.retrievalSteps.length > 0) {
                    planHtml += '<h4>Retrieval Steps:</h4><ol>';
                    response.retrievalSteps.forEach(step => {
                        planHtml += `<li>${step.action} ${step.itemName} (${step.itemId})</li>`;
                    });
                    planHtml += '</ol>';
                }
                
                // Display manifest
                if (response.returnManifest) {
                    const manifest = response.returnManifest;
                    planHtml += `
                        <h4>Return Manifest:</h4>
                        <p><strong>Undocking Container:</strong> ${manifest.undockingContainerId}</p>
                        <p><strong>Undocking Date:</strong> ${window.formatDate(manifest.undockingDate)}</p>
                        <p><strong>Total Volume:</strong> ${manifest.totalVolume.toFixed(2)} cubic units</p>
                        <p><strong>Total Weight:</strong> ${manifest.totalWeight.toFixed(2)} kg</p>
                        
                        <h5>Items to Return:</h5>
                    `;
                    
                    if (manifest.returnItems && manifest.returnItems.length > 0) {
                        planHtml += '<ul>';
                        manifest.returnItems.forEach(item => {
                            planHtml += `
                                <li>
                                    <strong>${item.name}</strong> (${item.itemId})
                                    <br>Reason: ${item.reason}
                                </li>
                            `;
                        });
                        planHtml += '</ul>';
                    } else {
                        planHtml += '<p>No items to return.</p>';
                    }
                }
                
                returnPlanDetails.innerHTML = planHtml;
                returnPlanResults.classList.remove('hidden');
            } else {
                window.showError(response.message || 'Failed to generate return plan');
                returnPlanResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to generate return plan');
            returnPlanResults.classList.add('hidden');
        }
    });
    
    // Complete undocking button click handler
    completeUndockingButton.addEventListener('click', async function() {
        if (!currentUndockingContainer) {
            window.showError('No undocking container selected');
            return;
        }
        
        try {
            const response = await api.completeUndocking(currentUndockingContainer);
            
            if (response.success) {
                alert(`Undocking completed successfully! ${response.itemsRemoved} items removed from inventory.`);
                returnPlanResults.classList.add('hidden');
                undockingContainerInput.value = '';
                undockingDateInput.value = '';
                maxWeightInput.value = '';
                currentUndockingContainer = null;
            } else {
                window.showError(response.message || 'Failed to complete undocking');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to complete undocking');
        }
    });
}

