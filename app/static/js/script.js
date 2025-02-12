// Dynamic Results Per Page Selection
document.addEventListener('DOMContentLoaded', function() {
    const perPageSelector = document.querySelector('select');
    if (perPageSelector) {
        perPageSelector.addEventListener('change', function() {
            const perPage = this.value;
            window.location.href = `?per_page=${perPage}`;
        });
    }
});

// Optional: Client-side filtering (if implemented)
// Add event listeners for filter inputs and make fetch requests