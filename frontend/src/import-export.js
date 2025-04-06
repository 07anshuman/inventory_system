function initImportExport() {
    const importItemsFile = document.getElementById('import-items-file');
    const importItemsButton = document.getElementById('import-items-button');
    const importContainersFile = document.getElementById('import-containers-file');
    const importContainersButton = document.getElementById('import-containers-button');
    const exportArrangementButton = document.getElementById('export-arrangement-button');
    const importExportResults = document.getElementById('import-export-results');
    const importExportDetails = document.querySelector('.import-export-details');
    
    // Import items button click handler
    importItemsButton.addEventListener('click', async function() {
        if (!importItemsFile.files || importItemsFile.files.length === 0) {
            window.showError('Please select a CSV file to import');
            return;
        }
        
        const file = importItemsFile.files[0];
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            window.showError('Please select a valid CSV file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await api.importItems(formData);
            
            if (response.success) {
                let detailsHtml = `
                    <p><strong>Items Imported:</strong> ${response.itemsImported}</p>
                `;
                
                if (response.errors && response.errors.length > 0) {
                    detailsHtml += '<h4>Import Errors:</h4><ul>';
                    response.errors.forEach(error => {
                        detailsHtml += `<li>Row ${error.row}: ${error.message}</li>`;
                    });
                    detailsHtml += '</ul>';
                }
                
                importExportDetails.innerHTML = detailsHtml;
                importExportResults.classList.remove('hidden');
                
                // Clear file input
                importItemsFile.value = '';
            } else {
                window.showError(response.message || 'Failed to import items');
                importExportResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to import items');
            importExportResults.classList.add('hidden');
        }
    });
    
    // Import containers button click handler
    importContainersButton.addEventListener('click', async function() {
        if (!importContainersFile.files || importContainersFile.files.length === 0) {
            window.showError('Please select a CSV file to import');
            return;
        }
        
        const file = importContainersFile.files[0];
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            window.showError('Please select a valid CSV file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await api.importContainers(formData);
            
            if (response.success) {
                let detailsHtml = `
                    <p><strong>Containers Imported:</strong> ${response.containersImported}</p>
                `;
                
                if (response.errors && response.errors.length > 0) {
                    detailsHtml += '<h4>Import Errors:</h4><ul>';
                    response.errors.forEach(error => {
                        detailsHtml += `<li>Row ${error.row}: ${error.message}</li>`;
                    });
                    detailsHtml += '</ul>';
                }
                
                importExportDetails.innerHTML = detailsHtml;
                importExportResults.classList.remove('hidden');
                
                // Clear file input
                importContainersFile.value = '';
            } else {
                window.showError(response.message || 'Failed to import containers');
                importExportResults.classList.add('hidden');
            }
        } catch (error) {
            window.showError(error.message || 'Failed to import containers');
            importExportResults.classList.add('hidden');
        }
    });
    
    // Export arrangement button click handler
    exportArrangementButton.addEventListener('click', async function() {
        try {
            const blob = await api.exportArrangement();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `arrangement_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            importExportDetails.innerHTML = '<p>Arrangement exported successfully!</p>';
            importExportResults.classList.remove('hidden');
        } catch (error) {
            window.showError(error.message || 'Failed to export arrangement');
            importExportResults.classList.add('hidden');
        }
    });
}

