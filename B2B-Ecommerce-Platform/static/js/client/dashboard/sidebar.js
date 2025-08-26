const sidebarSubMenus = document.querySelectorAll('.sub-menu');
// const sidebarSubMenuToggleDropdowns = document.querySelectorAll('.ti-angle-down');
const sidebarSubMenuToggleDropdowns = document.querySelectorAll('li.link a');


const path = window.location.pathname;
const page = path.split("/").pop();


if (page === "create-store.html" || page === "manage-store.html") {
    sidebarSubMenus[0].style.display = "grid";
    for (i = 0; i < sidebarSubMenuToggleDropdowns.length; i++) {
        sidebarSubMenuToggleDropdowns[i].addEventListener("click", function () {

            this.classList.toggle("active");
            const dropdownContent = this.nextElementSibling;

            // this.querySelector('.ti-angle-down').classList.toggle('toggle');

            if (dropdownContent.style.display === "grid") {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "none";
            } else {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "grid";
            }
        });
    }
} else if (page === "manage-product.html") {
    sidebarSubMenus[1].style.display = "grid";
    for (i = 0; i < sidebarSubMenuToggleDropdowns.length; i++) {
        sidebarSubMenuToggleDropdowns[i].addEventListener("click", function () {
            this.classList.toggle("active");
            const dropdownContent = this.nextElementSibling;

            // this.querySelector('.ti-angle-down').classList.toggle('toggle');

            if (dropdownContent.style.display === "grid") {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "none";
            } else {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "grid";
            }
        });
    }
} else {
    for (i = 0; i < sidebarSubMenuToggleDropdowns.length; i++) {
        sidebarSubMenuToggleDropdowns[i].addEventListener("click", function () {
            this.classList.toggle("active");
            const dropdownContent = this.nextElementSibling;

            // this.querySelector('.ti-angle-down').classList.toggle('toggle');

            if (dropdownContent.style.display === "grid") {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "none";
            } else {
                sidebarSubMenus.forEach(subMenu => {
                    subMenu.style.display = "none";
                });
                dropdownContent.style.display = "grid";
            }
        });
    }
}



document.addEventListener("DOMContentLoaded", () => {

})