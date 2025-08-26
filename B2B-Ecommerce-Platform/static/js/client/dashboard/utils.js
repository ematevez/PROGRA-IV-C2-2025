if (document.querySelector(".msg-alert") != undefined) {
    document.querySelectorAll(".msg-alert *")
        .forEach(elem => elem.addEventListener("click", (e) => {
            e.target.closest(".msg-alert").remove("inview")
        }))
        
    document.querySelector(".msg-alert").addEventListener("click", (e) => {
        if (e.target.classList.contains("inview"))
            e.target.classList.remove("inview")
    })
}

function showMessage (status, msg) {
    let className;
    const alertElem = document.querySelector(".msg-alert")
    alertElem.querySelector(".alert-msg").textContent = msg
    alertElem.classList.add("inview")
    alertElem.classList.add(status)
}