var productInCreationProgress = {
    detailsComplete : false,
    mediaComplete: false,
    labellingComplete: false,
    pricingComplete: false,
    storeComplete: false
};

document.querySelectorAll(".product-colors").forEach(
    elem => elem.addEventListener("change", () => {
        if (CSS.supports('color', elem.value)) {
            if (elem.classList.contains("with-error")) {
                elem.classList.remove('with-error')
            }
            elem.style.border = `1px solid ${elem.value}`
            elem.style.color = elem.value;
        }
        else {
            elem.classList.add('with-error')
        }
    })
)

function handleSubmit(event) {
    event.preventDefault()
}
async function submitProductDetails(currentPartId) {
    // get form data
    let formData = new FormData(document.querySelector(`form#${currentPartId}`));
    let inputs = document.querySelectorAll(`#${currentPartId} input, #${currentPartId} textarea`)
    inputs.forEach(elem => {
        formData[elem.name] = elem.value;
    })

    document.querySelector("#form-part-next").dataset.loading = true
    return await makeRequest(`/api/supplier/products/create/`, method="POST", data=formData)
}
async function submitProductMedia(currentPartId) {

    let formData = new FormData(document.querySelector(`form#${currentPartId}`))
    document.querySelector("#form-part-next").dataset.loading = true
    return await makeRequest(`/api/supplier/products/${productInCreationProgress.slug}/create/media/`, method="POST", data=formData, dataType="media")

}
async function submitProductStore(currentPartId) {
    let formData = new FormData(document.querySelector(`form#${currentPartId}`))
    let inputs = document.querySelectorAll(`#${currentPartId} input, #${currentPartId} textarea`)
    inputs.forEach(elem => {
        formData[elem.name] = elem.value;
    })
    document.querySelector("#form-part-next").dataset.loading = true
    return await makeRequest(`/api/supplier/products/${productInCreationProgress.slug}/create/store/`, method="POST", data=formData)
}
async function submitProductlabels(currentPartId) {
    let formData = new FormData(document.querySelector(`form#${currentPartId}`))
    let inputs = document.querySelectorAll(`#${currentPartId} input, #${currentPartId} textarea`)
    inputs.forEach(elem => {
        formData[elem.name] = elem.value;
    })
    document.querySelector("#form-part-next").dataset.loading = true
    return await makeRequest(`/api/supplier/products/${productInCreationProgress.slug}/create/labels/`, method="POST", data=formData)
}
async function submitProductPricing(currentPartId) {
    let formData = new FormData(document.querySelector(`form#${currentPartId}`))
    let inputs = document.querySelectorAll(`#${currentPartId} input, #${currentPartId} textarea`)
    inputs.forEach(elem => {
        formData[elem.name] = elem.value;
    })
    document.querySelector("#form-part-next").dataset.loading = true
    return await makeRequest(`/api/supplier/products/${productInCreationProgress.slug}/create/pricing/`, method="POST", data=formData)
}

function checkRequired(currentPartId) {
    let error_found = false
    const requiredFields = document.querySelectorAll(`#${currentPartId} input[required], #${currentPartId} textarea[required]`);

    // Function to check if a field is empty
    function isFieldEmpty(field) {
        return !field.value.trim();
    }

    // Function to handle field validation
    requiredFields.forEach(field => {
        if (isFieldEmpty(field)) {
            field.classList.add('with-error');
            setTimeout(() => {
                field.classList.remove('with-error');
            }, 5000)
            error_found = true
        } else {
            field.classList.remove('with-error');
        }
    });
    return error_found
}

function SubmitData(currentPartId) {

    if (checkRequired(currentPartId)) return;

    return new Promise(async (resolve, reject) => {
        let response;
        switch (currentPartId) {
            case 'product-details-form-part':
                if (productInCreationProgress.detailsComplete) {
                    resolve()
                    break;
                }
                try {
                    response = await submitProductDetails(currentPartId)
                    productInCreationProgress.slug = response.data.slug
                    productInCreationProgress.detailsComplete = true
                    showMessage("SUCCESS", response.message);
                    document.querySelector("#form-part-next").dataset.loading = false
                    resolve()
                }
                catch (err) {
                    if (err != undefined) {
                        showMessage("ERROR", err);
                        document.querySelector("#form-part-next").dataset.loading = false
                        reject()
                    }
                }
                break;
            case 'product-media-form-part':
                if (productInCreationProgress.mediaComplete) {
                    resolve()
                    break;
                }
                try {
                    response = await submitProductMedia(currentPartId)
                    productInCreationProgress.mediaComplete = true
                    showMessage("SUCCESS", response.message);
                    document.querySelector("#form-part-next").dataset.loading = false
                    resolve()
                }
                catch (err) {
                    if (err != undefined) {
                        showMessage("ERROR", err);
                        document.querySelector("#form-part-next").dataset.loading = false
                        reject()
                    }
                }
                break;
            case 'product-store-form-part':
                if (productInCreationProgress.storeComplete) {
                    resolve()
                    break;
                }
                try {
                    response = await submitProductStore(currentPartId)
                    productInCreationProgress.storeComplete = true
                    showMessage("SUCCESS", response.message);
                    document.querySelector("#form-part-next").dataset.loading = false
                    resolve()
                }
                catch (err) {
                    if (err != undefined) {
                        showMessage("ERROR", err);
                        document.querySelector("#form-part-next").dataset.loading = false
                        reject()
                    }
                }
                break;
            case 'product-labelling-form-part':
                if (productInCreationProgress.labellingComplete) {
                    resolve()
                    break;
                }
                try {
                    response = await submitProductlabels(currentPartId)
                    productInCreationProgress.labellingComplete = true
                    showMessage("SUCCESS", response.message);
                    document.querySelector("#form-part-next").dataset.loading = false
                    resolve()
                }
                catch (err) {
                    if (err != undefined) {
                        showMessage("ERROR", err);
                        document.querySelector("#form-part-next").dataset.loading = false
                        reject()
                    }
                }
                break;
            case 'product-pricing-form-part':
                if (productInCreationProgress.pricingComplete) {
                    resolve()
                    break;
                }
                try {
                    response = await submitProductPricing(currentPartId)
                    productInCreationProgress.pricingComplete = true
                    showMessage("SUCCESS", response.message);
                    document.querySelector("#form-part-next").dataset.loading = false
                    resolve()
                }
                catch (err) {
                    if (err != undefined) {
                        showMessage("ERROR", err);
                        document.querySelector("#form-part-next").dataset.loading = false
                        reject()
                    }
                }
                break;
        }
    })
}
function previousFormPart(event) {
    event.preventDefault()
    let currentPart = document.querySelector(".part-body.in-view")
    SubmitData(currentPart.id)
    .then(() => {
        let currentPartId = parseInt(currentPart.dataset.partIdx)
        if (currentPartId == 0) return;
        let prevPart = document.querySelector(`.part-body[data-part-idx="${currentPartId - 1}"]`)
        currentPart.classList.remove("in-view")
        prevPart.classList.add("in-view")
        document.querySelector("#form-part-title").textContent = prevPart.dataset.partTitle
    })
    .catch(() => {

    })
}
function nextFormPart(event) {
    event.preventDefault()
    if (document.querySelector("#form-part-next").dataset.loading == "true") {
        return;
    }
    let currentPart = document.querySelector(".part-body.in-view")
    SubmitData(currentPart.id)
    .then(() => {
        let currentPartId = parseInt(currentPart.dataset.partIdx)
        if ((currentPartId + 1) >= document.querySelectorAll(".part-body").length) {
            window.location.reload()
        };
        let nextPart = document.querySelector(`.part-body[data-part-idx="${currentPartId + 1}"]`)
        currentPart.classList.remove("in-view")
        nextPart.classList.add("in-view")
        document.querySelector("#form-part-title").textContent = nextPart.dataset.partTitle
    })
    .catch(() => {

    })
}


// HANDLING FILE DROPPING
var dropArea = document.querySelectorAll('.drop-area');
if (dropArea && dropArea.length > 0) {
    dropArea.forEach(elem => elem.addEventListener('dragover', event => {
        event.preventDefault();
        elem.classList.add('drag-over');
    }, false))
    dropArea.forEach(elem => elem.addEventListener('dragleave', event => {
        event.preventDefault();
        elem.classList.remove('drag-over');
    }, false))
}
if (document.getElementById("product-images-area") != null) {
    document.getElementById("product-images-area")
        .addEventListener('drop', (event) => {
            event.preventDefault();
            document.getElementById("product-images-area").classList.remove('drag-over');

            var files = event.dataTransfer.files;
            document.getElementById("product-images").files = files;

            // Handle the dropped files here or trigger form submission
            renderSelectedImages()
        }, false);
}

if (document.getElementById("product-videos-area") != null) {
    document.getElementById("product-videos-area")
        .addEventListener('drop', (event) => {
            event.preventDefault();
            document.getElementById("product-videos-area").classList.remove('drag-over');

            var files = event.dataTransfer.files;
            document.getElementById("product-videos").files = files;

            // Handle the dropped files here or trigger form submission
            renderSelectedVideos()
        }, false);
}
if (document.getElementById("product-images") != null) {
    document.getElementById("product-images")
        .addEventListener("change", (event) => renderSelectedImages(event))
}

function renderSelectedImages (event) {
    let imageInput = document.getElementById("product-images");
    let previewContainer = document.querySelector(".selected-images#images")
    // Clear the existing previews
    previewContainer.innerHTML = '';

    // Get the selected files
    const selectedFiles = Array.from(imageInput.files);

    // Iterate over the selected files
    for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];

        // Create a preview element for each file
        const previewElement = document.createElement('div');
        previewElement.classList.add('preview');

        // Create an image element for the preview
        const imageElement = document.createElement('img');
        imageElement.src = URL.createObjectURL(file);
        imageElement.alt = file.name;

        // Attach a click event handler to unselect the image
        imageElement.addEventListener('click', () => {
            // Remove the file from the selectedFiles array
            const newFiles = selectedFiles.filter(f => f !== file);

            // Create a new FileList object
            const newFileList = new DataTransfer();
            newFiles.forEach(f => newFileList.items.add(f));

            // Set the new FileList object as the input's files
            imageInput.files = newFileList.files;

            // Rebuild the previews
            renderSelectedImages();
        });

        // Append the image element to the preview element
        previewElement.appendChild(imageElement);

        // Append the preview element to the container
        previewContainer.appendChild(previewElement);
    }
}

if (document.getElementById("product-videos") != null) {
document.getElementById("product-videos")
    .addEventListener("change", (event) => renderSelectedVideos(event))
}

function renderSelectedVideos (event) {
    let imageInput = document.getElementById("product-videos");
    let previewContainer = document.querySelector(".selected-images#videos")
    // Clear the existing previews
    previewContainer.innerHTML = '';

    // Get the selected files
    const selectedFiles = Array.from(imageInput.files);

    // Iterate over the selected files
    for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];

        // Create a preview element for each file
        const previewElement = document.createElement('div');
        previewElement.classList.add('preview');

        // Create an image element for the preview
        const imageElement = document.createElement('video');
        imageElement.src = URL.createObjectURL(file);
        imageElement.alt = file.name;

        // Attach a click event handler to unselect the image
        imageElement.addEventListener('click', () => {
            // Remove the file from the selectedFiles array
            const newFiles = selectedFiles.filter(f => f !== file);

            // Create a new FileList object
            const newFileList = new DataTransfer();
            newFiles.forEach(f => newFileList.items.add(f));

            // Set the new FileList object as the input's files
            imageInput.files = newFileList.files;

            // Rebuild the previews
            renderSelectedVideos();
        });

        // Append the image element to the preview element
        previewElement.appendChild(imageElement);

        // Append the preview element to the container
        previewContainer.appendChild(previewElement);
    }
}

if (document.getElementById("bulk_upload_file_area") != null) {
    document.getElementById("bulk_upload_file_area")
        .addEventListener('drop', (event) => {
            event.preventDefault();
            document.getElementById("bulk_upload_file_area").classList.remove('drag-over');

            var files = event.dataTransfer.files;
            document.getElementById("bulk_upload_file").files = files;
            let previewContainer = document.querySelector(".selected-excel-file#file")
            previewContainer.style.display = "block"
        }, false);
        
    document.getElementById("bulk_upload_file")
        .addEventListener("change", (event) => {
            let previewContainer = document.querySelector(".selected-excel-file#file")
            previewContainer.style.display = "block"
        })
}