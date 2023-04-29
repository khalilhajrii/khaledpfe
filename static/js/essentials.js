let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".sidebarBtn");
sidebarBtn.onclick = function () {
    sidebar.classList.toggle("active");
    if (sidebar.classList.contains("active")) {
        sidebarBtn.classList.replace("bx-menu", "bx-menu-alt-right");
    } else 
        sidebarBtn.classList.replace("bx-menu-alt-right", "bx-menu");
    
}

// Datatatable for users 
let table = new DataTable('#users', {
    responsive: true,
});

// Datatatable for users 
let table_action = new DataTable('#action', {
    responsive: true,
});