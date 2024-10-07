// scripts.js
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');

    sidebar.addEventListener('mouseover', function () {
        this.classList.remove('collapsed');
        this.classList.add('expanded');
    });

    sidebar.addEventListener('mouseout', function () {
        this.classList.remove('expanded');
        this.classList.add('collapsed');
    });
});
