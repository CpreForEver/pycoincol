// Confirmation dialog for delete actions
function confirmDelete(id, name) {
    if (confirm(`Are you sure you want to delete "${name}" from your collection? This action cannot be undone.`)) {
        fetch(`/delete_coin/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/coins';
            } else {
                alert('Error deleting coin. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting coin. Please try again.');
        });
    }
}

function searchAll() {
    const input = document.getElementById('search-input');
    const query = input.value.trim();
    const tbody = document.getElementById('coins-table-body');
    const noResultsRow = tbody.querySelector('.no-results');
    
    if (query) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Searching...</td></tr>';
        
        fetch(`/search_all?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const results = data.results || [];
                
                if (results.length === 0) {
                    noResultsRow.style.display = 'table-row';
                    tbody.innerHTML = '';
                    tbody.appendChild(noResultsRow);
                } else {
                    noResultsRow.style.display = 'none';
                    tbody.innerHTML = results.map(item => {
                        const pcgsNo = item.pcgs_no ? `<td>${item.pcgs_no}</td>` : '<td>-</td>';
                        
                        if (item.type === 'coin') {
                            return `
                                <tr>
                                    <td>${item.id}</td>
                                    <td><span class="type-badge type-coin">Coin</span></td>
                                    ${pcgsNo}
                                    <td>${item.year}</td>
                                    <td>${item.name}</td>
                                    <td>${item.grade || '-'}</td>
                                    <td style="text-align: right;">${item.value ? '$' + item.value.toFixed(2) : '-'}</td>
                                </tr>
                            `;
                        } else if (item.type === 'note') {
                            return `
                                <tr>
                                    <td>${item.id}</td>
                                    <td><span class="type-badge type-note">Note</span></td>
                                    ${pcgsNo}
                                    <td>${item.year}</td>
                                    <td>${item.name}</td>
                                    <td>${item.grade || '-'}</td>
                                    <td style="text-align: right;">${item.value ? '$' + item.value.toFixed(2) : '-'}</td>
                                </tr>
                            `;
                        } else if (item.type === 'coin_set') {
                            return `
                                <tr>
                                    <td>${item.id}</td>
                                    <td><span class="type-badge type-coinset">Set</span></td>
                                    <td>-</td>
                                    <td>${item.year || '-'}</td>
                                    <td>${item.region || item.grade || '-'}</td>
                                    <td>${item.grade && item.name ? item.grade : '-'}</td>
                                    <td style="text-align: right;">${item.value ? '$' + item.value.toFixed(2) : '-'}</td>
                                </tr>
                            `;
                        }
                    }).join('');
                    
                    document.getElementById('total-amount').innerText = '$' + data.total_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
            })
            .catch(error => {
                console.error('Error:', error);
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Error fetching data</td></tr>';
            });
    } else {
        tbody.innerHTML = '';
        noResultsRow.style.display = 'none';
    }
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('description');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        // Trigger once on load
        this.style.height = (this.scrollHeight) + 'px';
    }
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchAll();
        }
    });
});
