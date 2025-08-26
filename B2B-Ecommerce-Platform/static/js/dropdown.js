const dropdownMenu = document.querySelector('#dropdown-menu');
const toggleDropdown = document.querySelector('#toggle-dropdown');
let isDropdownToggled = false;

try {
    toggleDropdown.addEventListener('click', (event) => {
        if (!isDropdownToggled) {
            isDropdownToggled = true;
            dropdownMenu.style.display = "block";
        } else {
            isDropdownToggled = false;
            dropdownMenu.style.display = "none";
        }
    });
    
    if (!dropdownMenu.classList.contains('right') || !dropdownMenu.classList.contains('right')) {
        dropdownMenu.classList.add('dropdown-menu-default');
    }
}
catch (err) {
    
}