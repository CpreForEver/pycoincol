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
});
