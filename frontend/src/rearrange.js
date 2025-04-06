function initRearrange() {
    const checkSpaceButton = document.getElementById('check-space-button');
    const rearrangeResults = document.getElementById('rearrange-results');
    const rearrangeDetails = document.querySelector('.rearrange-details');
    
    // Check space button click handler
    checkSpaceButton.addEventListener('click', async function() {
        try {
            const response = await api.getRearrangementRecommendations();
            
            if (response.success) {
                let detailsHtml = '';
                
                if (response.spaceEfficiency) {
                    detailsHtml += `
                        <p><strong>Current Space Efficiency:</strong> ${(response.spaceEfficiency * 100).toFixed(2)}%</p>
                    `;
                }
                
                if (response.recommendations && response.recommendations.length > 0) {
                    detailsHtml += '<h4>Rearrangement Recommendations:</h4>';
                    
                    response.recommendations.forEach((rec, index) => {
                        detailsHtml += `
                            <div class="recommendation">
                                <h5>Recommendation ${index + 1}</h5>
                                <p><strong>Estimated Efficiency Gain:</strong> ${(rec.efficiencyGain * 100).toFixed(2)}%</p>
                                <p><strong>Estimated Time Required:</strong> ${rec.timeRequired} minutes</p>
                                
                                <h6>Movement Plan:</h6>
                        `;
                        
                        if (rec.movementPlan && rec.movementPlan.length > 0) {
                            detailsHtml += '<ol>';
                            rec.movementPlan.forEach(step => {
                                detailsHtml += `
                                    <li>
                                        Move ${step.itemName} (${step.itemId})
                                        from ${step.fromContainer} to ${step.toContainer}
                                    </li>
                                `;
                            });
                            detailsHtml += '</ol>';
                        } else {
                            detailsHtml += '<p>No movement steps required.</p>';
                        }
                        
                        detailsHtml += '</div>';
                    });
                } else {
                    detailsHtml += '<p>No rearrangement recommendations available.</p>';
                }
                
                rearrangeDetails.innerHTML = detailsHtml;
                rearrangeResults.classList.remove('hidden');
            } else {
                window.showError(response.message || 'Failed to get rearrangement recommendations');
                rearrangeResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to get rearrangement recommendations');
            rearrangeResults.classList.add('hidden');
        }
    });
}

