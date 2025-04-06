function initLogs() {
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const itemIdInput = document.getElementById('item-id-logs');
    const userIdInput = document.getElementById('user-id-logs');
    const actionTypeSelect = document.getElementById('action-type');
    const getLogsButton = document.getElementById('get-logs-button');
    const logsResults = document.getElementById('logs-results');
    const logsList = document.querySelector('.logs-list');
    
    // Get logs button click handler
    getLogsButton.addEventListener('click', async function() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const itemId = itemIdInput.value.trim();
        const userId = userIdInput.value.trim();
        const actionType = actionTypeSelect.value;
        
        if (!startDate || !endDate) {
            window.showError('Please select both start and end dates');
            return;
        }
        
        try {
            const response = await api.getLogs(
                new Date(startDate).toISOString(),
                new Date(endDate).toISOString(),
                itemId || undefined,
                userId || undefined,
                actionType || undefined
            );
            
            if (response.logs && response.logs.length > 0) {
                let logsHtml = '<table class="logs-table">';
                logsHtml += `
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Item</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                `;
                
                response.logs.forEach(log => {
                    logsHtml += `
                        <tr>
                            <td>${window.formatDate(log.timestamp)}</td>
                            <td>${log.userId}</td>
                            <td>${log.actionType}</td>
                            <td>${log.itemId}</td>
                            <td>
                    `;
                    
                    if (log.details) {
                        if (log.details.fromContainer) {
                            logsHtml += `From: ${log.details.fromContainer}<br>`;
                        }
                        if (log.details.toContainer) {
                            logsHtml += `To: ${log.details.toContainer}<br>`;
                        }

