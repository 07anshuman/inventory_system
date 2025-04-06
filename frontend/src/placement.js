function initPlacement() {
    const itemIdInput = document.getElementById('item-id-placement');
    const containerIdInput = document.getElementById('container-id-placement');
    const getPlacementButton = document.getElementById('get-placement-button');
    const placementResults = document.getElementById('placement-results');
    const placementDetails = document.querySelector('.placement-details');
    
    // Get placement button click handler
    getPlacementButton.addEventListener('click', async function() {
        const itemId = itemIdInput.value.trim();
        const containerId = containerIdInput.value.trim();
        
        if (!itemId) {
            window.showError('Please enter an item ID');
            return;
        }
        
        try {
            const response = await api.getPlacementRecommendation(itemId, containerId);
            
            if (response.success) {
                let detailsHtml = '';
                
                if (response.recommendation) {
                    const rec = response.recommendation;
                    detailsHtml += `
                        <p><strong>Item:</strong> ${rec.itemName} (${rec.itemId})</p>
                        <p><strong>Recommended Container:</strong> ${rec.containerId}</p>
                        <p><strong>Position:</strong> 
                            (${rec.position.startCoordinates.width}, 
                             ${rec.position.startCoordinates.depth}, 
                             ${rec.position.startCoordinates.height}) to
                            (${rec.position.endCoordinates.width}, 
                             ${rec.position.endCoordinates.depth}, 
                             ${rec.position.endCoordinates.height})
                        </p>
                        <p><strong>Reason:</strong> ${rec.reason}</p>
                    `;
                    
                    if (rec.steps && rec.steps.length > 0) {
                        detailsHtml += '<h4>Placement Steps:</h4><ol>';
                        rec.steps.forEach(step => {
                            detailsHtml += `<li>${step.description}</li>`;
                        });
                        detailsHtml += '</ol>';
                    }
                } else {
                    detailsHtml = '<p>No placement recommendation available.</p>';
                }
                
                placementDetails.innerHTML = detailsHtml;
                placementResults.classList.remove('hidden');
            } else {
                window.showError(response.message || 'Failed to get placement recommendation');
                placementResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to get placement recommendation');
            placementResults.classList.add('hidden');
        }
    });
}

