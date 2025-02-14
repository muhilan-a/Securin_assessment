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


let currentPage = 1;

function applyFilters() {
    const params = new URLSearchParams({
        cve_id: document.getElementById('cve_id').value,
        year: document.getElementById('year').value,
        score: document.getElementById('score').value,
        last_modified_days: document.getElementById('last_modified').value,
        per_page: 10,  
        page: currentPage
    });

    fetch(`/api/cves?${params}`)
        .then(response => response.json())
        .then(data => updateTable(data));
}

function updateTable(data) {
    const tbody = document.getElementById('cveTableBody');
    tbody.innerHTML = '';  

    data.forEach(cve => {
        const row = `<tr onclick="window.location='/cves/${cve.id}'">
            <td>${cve.id}</td>
            <td>${new Date(cve.published).toLocaleDateString()}</td>
            <td>${new Date(cve.last_modified).toLocaleDateString()}</td>
            <td>${cve.status}</td>
            <td>${cve.base_score_v2}</td>
            
        </tr>`;
        tbody.innerHTML += row;
    });
}

function changePage(delta) {
    currentPage += delta;
    if (currentPage < 1) currentPage = 1;
    document.getElementById('currentPage').textContent = currentPage;
    applyFilters();  
}


applyFilters();