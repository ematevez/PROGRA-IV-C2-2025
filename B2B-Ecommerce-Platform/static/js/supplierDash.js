document.addEventListener("DOMContentLoaded", () => {
    let pageNum = 1;
    let fetchState = {
        "stores_loaded": false,
        "products_loaded": false,
        "contract_loaded": false,
        "buyer_contract_loaded": false,
        "services_loaded": false,
    }

    let BASE_API_URL
    let BASE_URL

    if (window.location.href.includes("localhost")) {
        BASE_API_URL = 'http://localhost:8000';
        BASE_URL = 'http://localhost:8000';
    }
    else {
        BASE_API_URL = 'http://mugisa.tech';
        BASE_URL = 'http://mugisa.tech';
    }

    const fetchData = async (url, has_page_num = true) => {
        let response;
        if (has_page_num) {
            response = await fetch(
            `${BASE_API_URL}/${url}/?page=${pageNum}`, {
                method: "GET",
                mode: "same-origin",
                cache: "no-cache",
                credentials: 'same-origin'
            });
        }
        else {
            response = await fetch(`${BASE_API_URL}/${url}`);
        }
        if (response.ok) {
            const data = await response.json();
            return data;
        }
    }


    const paginate = (response, invoker) => {
        document.querySelector('.table-pagination #next-page').addEventListener('click', () => {
            if (response.count / 10 > pageNum) {
                pageNum = pageNum + 1;
                invoker();
            }
        })

        document.querySelector('.table-pagination #previous-page').addEventListener('click', () => {
            if (pageNum > 1) {
                pageNum--;
                invoker();
            }
        })
        document.querySelector('.table-pagination #current-page').textContent = pageNum;
        document.querySelector('.table-pagination #current-page-0').textContent = pageNum;
        document.querySelector('.table-pagination #max-page').textContent = Math.ceil(response.count / 10);
    }


    // MODAL
    const openStoreModal = (storeSlug) => {
        const storeModal = document.querySelector('#store-modal');
        storeModal.style.display = "grid";

        const showroomForm = document.querySelector("#showroom-form");
        showroomForm.action = `${storeSlug}/assign-showroom/`;
        
        const productForm = document.querySelector("#product-form");
        productForm.action = `${storeSlug}/add-product/`;
    }

    const closeStoreModal = () => {
        const storeModal = document.querySelector('#store-modal');
        // storeModal.style.display = "none"
    }

    // STORES
    const renderStores = async () => {
        if (!fetchState["stores_loaded"]) {
            pageNum = 1;
            fetchState["stores_loaded"] = true;
        }

        let response = await fetchData(url = 'api/stores');

        const tableBody = document.querySelector('table#stores tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;

            response.results.forEach((record, i) => {
                console.log(record)
                let tableRow = document.createElement('tr')
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.products}</td>
                    <td style="text-transform: capitalize;">${record.is_verified}</td>
                    <td>${record.created_on}</td>
                `;
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    // if (!isClientModalOpen) {
                    //     // fetch client data
                    //     // open modal
                    //     fetchData(`product/${record.slug}`, has_page_num=false)
                    //     .then(response => openProductModal(response));                        
                    // }

                    tableRow.addEventListener('click', (e) => {
                        // Retrieve data for this row
                        // and construct the object to pass to the modal

                        // Open Modal
                        openStoreModal(tableRow.dataset['slug'])

                        // Close Modal
                        document.querySelector('#close-modal').addEventListener('click', (event) => {
                            if (event.target.classList.contains('ti-close'))
                                closeStoreModal();
                        });
                    })
                })
            })
        }

        // change page number
        paginate(response, invoker = renderStores)
    }

    const storesTable = document.querySelector("table#stores");
    if (storesTable) {
        renderStores();
    }
    // STORES

    function openOperationConfirmModal (url) {
        const operationConfirmModal = document.querySelector("#operation-confirm-modal");
        operationConfirmModal.classList.remove('cs-hidden');
        operationConfirmModal.classList.add('cs-grid');

        operationConfirmModal.querySelector("form#confirm_delete").action = url
        
        operationConfirmModal.querySelector("#cancel-operation")
            .addEventListener("click", () => {
                operationConfirmModal.classList.remove('cs-grid');
                operationConfirmModal.classList.add('cs-hidden');
            })
    }

    // PRODUCTS

    async function openProductModal(response) {
        let selected_product_preview = document.querySelector(".selected_product_preview")
        selected_product_preview.classList.add("in-view")
        
        document.querySelector(".selected_product_preview #close_selected_product_preview")
            .addEventListener('click', () => {
                selected_product_preview.classList.remove("in-view")
            })

        selected_product_preview.querySelector("#delete_product")
            .addEventListener("submit", e => {
                e.preventDefault()
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/delete/`
                openOperationConfirmModal(deleteUrl)
            })

        selected_product_preview.querySelector(".product_name").textContent = response.name
        selected_product_preview.querySelector(".product_desc").textContent = response.description

        let store_area = selected_product_preview.querySelector(".category-area")
        store_area.innerHTML = ""
        response.store.forEach(store => {
            let elem = document.createElement("span")
            elem.className = "store"
            elem.innerHTML = `<p>${store.name}</p>`
            store_area.appendChild(elem)

            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/store/${store.slug}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            elem.appendChild(delete_cta)
        })

        // category
        let cat_elem = document.createElement("span")
        cat_elem.textContent = response.sub_category.category.name
        store_area.appendChild(cat_elem)
        
        // let cat_delete_cta = document.createElement("button")
        // cat_delete_cta.className = "delete_cta"
        // cat_delete_cta.innerHTML = '<i class="ti-trash"></i>'
        // cat_delete_cta.addEventListener("click", () => {
        //     let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/category/${response.sub_category.category.slug}/delete/`
        //     openOperationConfirmModal(deleteUrl)
        // })
        // cat_elem.appendChild(cat_delete_cta)

        let s_cat_elem = document.createElement("span")
        s_cat_elem.textContent = response.sub_category.name
        store_area.appendChild(s_cat_elem)
        
        // let s_cat_delete_cta = document.createElement("button")
        // s_cat_delete_cta.className = "delete_cta"
        // s_cat_delete_cta.innerHTML = '<i class="ti-trash"></i>'
        // s_cat_delete_cta.addEventListener("click", () => {
        //     let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/sub_category/${response.sub_category.slug}/delete/`
        //     openOperationConfirmModal(deleteUrl)
        // })
        // s_cat_elem.appendChild(s_cat_delete_cta)

        // princing
        let pricings = selected_product_preview.querySelector(".pricings")
        pricings.innerHTML = ""
        response.pricings.forEach(pricing => {
            let elem = document.createElement("div")
            elem.className = "pricing"
            elem.innerHTML = `
                <span class="currency">${pricing.currency}</span>
                <span class="min_price">${pricing.min_price}</span>
                <span class="max_price">${pricing.max_price}</span>
            `
            pricings.appendChild(elem)
            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/pricing/${pricing.id}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            elem.appendChild(delete_cta)
        })

        // tags
        let tags = selected_product_preview.querySelector(".product_labels#tags")
        tags.innerHTML = ""
        response.tags.forEach(tag => {
            let elem = document.createElement("span")
            elem.textContent = tag.name
            tags.appendChild(elem)

            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/tag/${tag.id}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            elem.appendChild(delete_cta)
        })

        // colors
        let colors = selected_product_preview.querySelector(".product_labels#colors")
        colors.closest(".labelling").style.display = "grid"
        if (response.colors.length > 0) {
            colors.innerHTML = ""
            response.colors.forEach(color => {
                let elem = document.createElement("span")
                elem.textContent = color.name
                colors.appendChild(elem)

                // delete cta
                let delete_cta = document.createElement("button")
                delete_cta.className = "delete_cta"
                delete_cta.innerHTML = '<i class="ti-trash"></i>'
                delete_cta.addEventListener("click", () => {
                    let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/color/${color.id}/delete/`
                    openOperationConfirmModal(deleteUrl)
                })
                elem.appendChild(delete_cta)
            })
        }
        else {
            // colors.closest(".labelling").style.display = "none"
        }

        // materials
        let materials = selected_product_preview.querySelector(".product_labels#materials")
        materials.closest(".labelling").style.display = "grid"
        materials.innerHTML = ""
        response.materials.forEach(material => {
            let elem = document.createElement("span")
            elem.textContent = material.name
            materials.appendChild(elem)

            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/material/${material.id}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            elem.appendChild(delete_cta)
        })
        if (response.materials.length < 1) {
            // materials.closest(".labelling").style.display = "none"
        }

        // images
        let images = selected_product_preview.querySelector(".product_media #images .body")
        images.closest(".media_section").style.display = "grid"
        images.innerHTML = ""
        response.images.forEach(image => {
            let elem = document.createElement("img")
            elem.src = image.image
            
            let wrapper = document.createElement("div")
            wrapper.className = "wrapper"
            wrapper.appendChild(elem)
            images.appendChild(wrapper)

            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/image/${image.slug}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            wrapper.appendChild(delete_cta)
        })
        if (response.images.length < 1) {
            // images.closest(".media_section").style.display = "none"
        }

        // videos
        let videos = selected_product_preview.querySelector(".product_media #videos .body")
        videos.closest(".media_section").style.display = "grid"
        videos.innerHTML = ""
        response.videos.forEach(video => {
            let elem = document.createElement("video")
            elem.src = video.video
            elem.controls = true
            
            let wrapper = document.createElement("div")
            wrapper.className = "wrapper"
            wrapper.appendChild(elem)
            videos.appendChild(wrapper)

            // delete cta
            let delete_cta = document.createElement("button")
            delete_cta.className = "delete_cta"
            delete_cta.innerHTML = '<i class="ti-trash"></i>'
            delete_cta.addEventListener("click", () => {
                let deleteUrl = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/video/${video.slug}/delete/`
                openOperationConfirmModal(deleteUrl)
            })
            wrapper.appendChild(delete_cta)
        })
        if (response.videos.length < 1) {
            // videos.closest(".media_section").style.display = "none"
        }

        
        // set edit form action
        selected_product_preview.querySelectorAll(".floating_form")
            .forEach(elem => {
                elem.action = `${BASE_URL}/en/suppliers/dashboard/product/${response.slug}/edit/`
            })

        selected_product_preview.querySelectorAll(".floating_form .cancel-cta")
            .forEach(elem => elem.addEventListener("click", e => {
                e.preventDefault()
                elem.closest(".floating_form").classList.remove("inview")
                elem.closest(".floating_form").reset()
            }))

        selected_product_preview.querySelectorAll(".edit_cta")
            .forEach(elem => elem.addEventListener("click", () => {
                elem.parentNode.querySelector(".floating_form").classList.add("inview")
            }))
       
    }

    const renderProducts = async () => {
        if (!fetchState["products_loaded"]) {
            pageNum = 1;
            fetchState["products_loaded"] = true;
        }

        let response = await fetchData(url = 'api/supplier/products');

        const tableBody = document.querySelector('table#products tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;

            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.sub_category.category.name}</td>
                    <td>${record.sub_category.name}</td>
                    <td>${record.currency} ${record.price}</td>
                    <td>${record.created_on}</td>
                    <td>${record.is_verified}</td>
                    `;
                    // <td><i class="fa fa-info-circle"></i></td>
                tableRow.addEventListener('click', () => openProductModal(record))
                tableBody.appendChild(tableRow);
            })
        }

        // change page number
        paginate(response, invoker = renderProducts)
    }

    const productsTable = document.querySelector("table#products");
    if (productsTable) {
        renderProducts();
    }
    // PRODUCTS

    // CONTRACTS
    const renderContracts = async () => {
        if (!fetchState["contract_loaded"]) {
            pageNum = 1;
            fetchState["contract_loaded"] = true;
        }

        // which dashboard are we on
        let url;
        if (window.location.href.includes('/suppliers/')) {
            url = "api/supplier/contracts";
        }
        else {
            url = "api/contracts";
        }

        let response = await fetchData(url = url);

        const tableBody = document.querySelector('table#contracts tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;

            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.setAttribute('data-id', record.id);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.service.name}</td>
                    <td>${record.buyer.username}</td>
                    <td>${record.created_on}</td>
                    <td><a style="display:grid; justify-items:center;align-items:center;" href="${BASE_URL}/suppliers/dashboard/contractsdetails/${record.id}"><i class="fa fa-info-circle"></i></a></td>
                `;
                tableBody.appendChild(tableRow);
            })
        }

        // change page number
        paginate(response, invoker = renderContracts)
    }

    const contractsTable = document.querySelector("table#contracts");
    if (contractsTable) {
        renderContracts();
    }
    // CONTRACTS

    // SERVICES
    const renderServices = async () => {
        if (!fetchState["services_loaded"]) {
            pageNum = 1;
            fetchState["services_loaded"] = true;
        }

        let response = await fetchData(url = 'api/services');
        console.log(response)

        const tableBody = document.querySelector('table#services tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;

            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.setAttribute('data-id', record.id);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.description.slice(0, 150)} ...</td>
                    <td>${record.currency} ${record.price}</td>
                    <td>${record.created_on}</td>
                `;
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`product/${record.slug}`, has_page_num = false)
                            .then(response => openProductModal(response));
                    }
                })
            })
        }

        // change page number
        paginate(response, invoker = renderServices)
    }

    const servicesTable = document.querySelector("table#services");
    if (servicesTable) {
        renderServices();
    }
    // SERVICES

    // BUYER CONTRACTS
    const renderBuyerContracts = async () => {
        if (!fetchState["buyer_contract_loaded"]) {
            pageNum = 1;
            fetchState["buyer_contract_loaded"] = true;
        }

        let response = await fetchData(url = 'api/contracts');

        const tableBody = document.querySelector('table#buyer-contracts tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;

            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.setAttribute('data-id', record.id);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.service.name}</td>
                    <td>${record.supplier.username}</td>
                    <td>${record.created_on}</td>
                    <td style="display:grid; justify-content:center;align-items:center;text-center:"><a href="${BASE_URL}/buyer/dashboard/contractsdetails/${record.id}"><i class="fa fa-info-circle"></i></a></td>
                `;
                tableBody.appendChild(tableRow);
            })
        }

        // change page number
        paginate(response, invoker = renderBuyerContracts)
    }

    const buyerContractsTable = document.querySelector("table#buyer-contracts");
    if (buyerContractsTable) {
        renderBuyerContracts();
    }
    // BUYER CONTRACTS
});


// if (window.innerWidth < 800) {
//     if (window.location.href.includes('/admin/') || window.location.href.includes('dashboard')) {
//         let domain = full = location.protocol + '//' + location.host
//         window.location.replace(`${domain}/blocked`);
//     }
// }