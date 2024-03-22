document.addEventListener('DOMContentLoaded', function() {
    const searchBar = document.getElementById('searchBar');
    searchBar.addEventListener('keyup', function(e) {
        const term = e.target.value.toLowerCase();
        const links = document.getElementById('linksList').getElementsByTagName('a');
        
        Array.from(links).forEach(function(link) {
            const title = link.textContent;
            if (title.toLowerCase().indexOf(term) != -1) {
                link.parentElement.style.display = '';
            } else {
                link.parentElement.style.display = 'none';
            }
        });
    });
});
