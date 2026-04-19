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

// Search coins function
function searchCoins() {
    const input = document.getElementById('coins-input');
    const query = input.value.trim();
    const tbody = document.getElementById('coins-table-body');
    const totalAmountWrapper = document.getElementById('total-amount-wrapper');
    
    if (query) {
        // Clear existing rows
        tbody.innerHTML = '<tr><td colspan="6">Searching...</td></tr>';
        
        fetch(`/api/coins?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(coins => {
                if (coins.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6">No coins found</td></tr>';
                } else {
                    tbody.innerHTML = coins.map(coin => `
                        <tr>
                            <td>${coin.id}</td>
                            <td>${coin.pcgs_no || '-'}</td>
                            <td>${coin.year}</td>
                            <td>${coin.name}</td>
                            <td>${coin.grade || '-'}</td>
                            <td>$${coin.price_guide_value ? coin.price_guide_value.toFixed(2) : '-'}</td>
                            <td>
                             <a href="edit_coin/${coin.id}" class="btn btn-small btn-secondary">Edit</a>
                             <a href="javascript:void(0);" onclick="confirmDelete(${coin.id}, '${coin.name}')" class="btn btn-small btn-danger">Delete</a>
                           </td>
                        </tr>
                    `).join('');
                    
                    // Calculate and display total
                    const total = coins.reduce((sum, coin) => sum + (coin.price_guide_value || 0), 0);
                    document.getElementById('total-amount').innerText = `$${total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                    totalAmountWrapper.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                tbody.innerHTML = '<tr><td colspan="6">Error fetching data</td></tr>';
            });
    } else {
        tbody.innerHTML = '';
        totalAmountWrapper.style.display = 'none';
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
    // Search on Enter key
    document.getElementById('coins-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchCoins();
        }
    });
});
