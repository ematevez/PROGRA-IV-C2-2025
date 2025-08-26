document.addEventListener('DOMContentLoaded', () => {
    // state
    const clientModal = document.querySelector("#client-modal");
    const clientModalCloseActivator = document.querySelector('#client-modal-deactivator');
    let isClientModalOpen = false;

    const productModal = document.querySelector("#product-modal");
    const productModalCloseActivator = document.querySelector('#product-modal-deactivator');
    let isProductModalOpen = false;


    const contractModal = document.querySelector("#contract-modal");
    const contractModalCloseActivator = document.querySelector('#contract-modal-deactivator');
    let isContractModalOpen = false;

    const operationConfirmModal = document.querySelector("#operation-confirm-modal");
    let isOperationConfirmModal = false;

    const serviceModal = document.querySelector("#manager-service-modal");
    const serviceModalCloseActivator = document.querySelector("#manager-service-modal-deactivator");
    let isServiceModalOpen = false;

    let pageNum = 1;
    let fetchState = {
        "supplier_was_loaded": false,
        "buyer_was_loaded": false,
        "products_was_loaded": false,
        "contracts_was_loaded": false,
        "showrooms_was_loaded" : false,
        "services_was_loaded" : false,
        "stores_was_loaded" : false,
        "memberships_was_loaded" : false,
        "adverts_was_loaded" : false,
    }

    let BASE_API_URL
    let BASE_URL

    if (window.location.href.includes("localhost")) {
        BASE_API_URL = 'http://localhost:8000/en/admin-api';
        BASE_URL = 'http://localhost:8000';
    }
    else {
        BASE_API_URL = 'http://mugisa.tech/en/admin-api';
        BASE_URL = 'http://mugisa.tech/';
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


    const paginate = (response, invoker) => {
        document.querySelector('section.content:not(.cs-hidden) #next-page').addEventListener('click', () => {
            if (response.count / 10 > pageNum)
            {
                pageNum = pageNum + 1;
                invoker();
            }
        })

        document.querySelector('section.content:not(.cs-hidden) #previous-page').addEventListener('click', () => {
            if (pageNum > 1)
            {
                pageNum--;
                invoker();
            }
        })
        document.querySelector('section.content:not(.cs-hidden) #current-page').textContent = pageNum;
        document.querySelector('section.content:not(.cs-hidden) #current-page-0').textContent = pageNum;
        document.querySelector('section.content:not(.cs-hidden) #max-page').textContent = Math.ceil(response.count / 10);
    }


    // CLIENT MODAL
    const clientItems = document.querySelectorAll('.client-item'); 
    const closeClientModel = () => {
        clientModal.classList.remove('cs-grid');
        clientModal.classList.add('cs-hidden');
        isClientModalOpen = false;
        document.body.classList.remove('modal-open');
    }
    
    const openClientModal = (response) => {
        document.body.classList.add('modal-open');
        clientModal.classList.remove('cs-hidden');
        clientModal.classList.add('cs-grid');
        isClientModalOpen = true;

        clientModal.querySelector('#client-username').textContent = response.user.username;
        clientModal.querySelector('#client-business_name').textContent = response.business_name;
        clientModal.querySelector('#client-country').textContent = response.country;
        clientModal.querySelector('#client-vta').textContent = response.vat_number;
        clientModal.querySelector('#client-lei').textContent = response.legal_etity_identifier;
        clientModal.querySelector('#client-membership').textContent = response.membership;
        
        if (response.user.account_type == "SUPPLER") {
            clientModal.querySelector('#view-client-page').href = `${BASE_URL}suppliers/supplier/${response.slug}`
        }

        // contact user
        clientModal.querySelector('#contact-user-cta').href = `${BASE_URL}support/admin/contact/${response.slug}`

        // get stores
        if (response.user.account_type == 'SUPPLIER') {
            let storesElem = document.querySelector('#client-stores');
            while (storesElem.firstChild) {
                storesElem.removeChild(storesElem.firstChild);
            }
            fetchData(`stores/supplier/${response.slug}`, has_page_num=false)
            .then(stores_response => {
                if (stores_response.count < 1) {
                    let storeElem = document.createElement('span');
                    storeElem.className = 'cs-text-md';
                    storeElem.textContent = "No Stores Found.";
                    storesElem.appendChild(storeElem);
                } else {
                    stores_response.results.forEach(record => {
                        let storeElem = document.createElement('span');
                        storeElem.className = 'cs-bg-hover-color br-md cs-text-md';
                        storeElem.style.padding =  ".25rem .75rem";
                        storeElem.textContent = record.name;
                        storesElem.appendChild(storeElem);
                    })
                }
            })
            
            // get showrooms
            let showroomsElem = document.querySelector('#client-showrooms');
            while (showroomsElem.firstChild) {
                showroomsElem.removeChild(showroomsElem.firstChild);
            }
            fetchData(`showrooms/supplier/${response.slug}`, has_page_num=false)
            .then(showrooms_response => {
                if (showrooms_response < 1) {
                    let showroomElem = document.createElement('span');
                    showroomElem.className = 'cs-text-md';
                    showroomElem.textContent = "No Showrooms Found.";
                    showroomsElem.appendChild(showroomElem);
                } else {
                    showrooms_response.forEach(record => {
                        let showroomElem = document.createElement('span');
                        showroomElem.className = 'cs-bg-hover-color br-md cs-text-md';
                        showroomElem.style.padding =  ".25rem .75rem";
                        showroomElem.textContent = record.name;
                        showroomsElem.appendChild(showroomElem);
                    })
                }
            })
        }
        else {
            clientModal.querySelector('#membership-group').parentNode.removeChild(clientModal.querySelector('#membership-group'));

            clientModal.querySelector('#stores-group').parentElement.removeChild(clientModal.querySelector('#stores-group'));

            clientModal.querySelector('#showrooms-group').parentElement.removeChild(clientModal.querySelector('#showrooms-group'));

            clientModal.querySelector('#veiw-product-cta').parentElement.removeChild(clientModal.querySelector('#veiw-product-cta'));
        }

        if (isClientModalOpen) {
            clientModal.querySelector('#suspend-btn').addEventListener('click', (e) => openOperationConfirmModal(msg='Are you sure you want to suspend client account.', postUrl= `suspend-account/${response.slug}`, data={"id": response.id}))
        }
    }

    if (clientModalCloseActivator) {
        clientModalCloseActivator.addEventListener('click', () => {
            closeClientModel()
        })
    }
    // CLIENT MODAL

    // PRODUCT MODAL
    const productItems = document.querySelectorAll('.product-item');

    const closeProductModel = () => {
        productModal.classList.remove('cs-grid');
        productModal.classList.add('cs-hidden');
        isProductModalOpen = false;
        document.body.classList.remove('modal-open');
    }
    
    const openProductModal = (response) => {
        document.body.classList.add('modal-open');
        productModal.classList.remove('cs-hidden');
        productModal.classList.add('cs-grid');
        isProductModalOpen = true;

        productModal.querySelector('#product-name').textContent = response.name;
        productModal.querySelector('#product-supplier').textContent = response.supplier;
        productModal.querySelector('#product-category').textContent = response.sub_category.category.name;
        productModal.querySelector('#product-subCategory').textContent = response.sub_category.name;
        productModal.querySelector('#product-price').textContent = `${response.currency} ${response.price}`;
        productModal.querySelector('#product-description').textContent = response.description;
        
        productModal.querySelector('#view-product-page').href = `${BASE_URL}suppliers/products/${response.slug}`
        // contact user
        productModal.querySelector('#contact-user-cta').href = `${BASE_URL}support/admin/contact/${response.supplier_slug}`

        if (response.is_verified == true) {
            document.querySelector("#product-modal #verify-btn").classList.remove("cs-grid");
            document.querySelector("#product-modal #verify-btn").classList.add("cs-hidden");
            document.querySelector("#product-modal #suspend-btn").classList.add("cs-grid");
            document.querySelector("#product-modal #suspend-btn").classList.remove("cs-hidden");
        } else {
            document.querySelector("#product-modal #suspend-btn").classList.remove("cs-grid");
            document.querySelector("#product-modal #suspend-btn").classList.add("cs-hidden");
            document.querySelector("#product-modal #verify-btn").classList.add("cs-grid");
            document.querySelector("#product-modal #verify-btn").classList.remove("cs-hidden");
        }


        let storesElem = document.querySelector('#product-images');
            while (storesElem.firstChild) {
                storesElem.removeChild(storesElem.firstChild);
            }
            fetchData(`product-images/${response.slug}`, has_page_num=false)
            .then(images_response => {
                images_response.results.forEach((record, i) => {
                    if (i < 8) {
                        let storeElem = document.createElement('img');
                        storeElem.className = 'cs-bg-hover-color br-md cs-text-md';
                        storeElem.style.objectFit =  "cover";
                        storeElem.style.aspectRatio =  "1";
                        storeElem.style.alt =  response.name;
                        storeElem.src =  record.image;
                        storesElem.appendChild(storeElem);
                    }
                })
            })


        if (isProductModalOpen) {
            productModal.querySelector('#suspend-btn').addEventListener('click', (e) => openOperationConfirmModal(msg='Are you sure you want to suspend product.', postUrl=`product/delete/${response.slug}`, renderProducts))
            
            productModal.querySelector('#verify-btn').addEventListener('click', (e) => openOperationConfirmModal(msg='Are you sure you want to verify this Product.', postUrl=`product/verify/${response.slug}`, renderProducts))
        }
    }

    if (productModalCloseActivator) {
        productModalCloseActivator.addEventListener('click', () => {
            closeProductModel()
        })
    }
    // PRODUCT MODAL

    // CONTRACT MODAL

    const closecontractModel = () => {
        contractModal.classList.remove('cs-grid');
        contractModal.classList.add('cs-hidden');
        isContractModalOpen = false;
        document.body.classList.remove('modal-open');
    }
    
    const openContractModal = (response) => {
        document.body.classList.add('modal-open');
        contractModal.classList.remove('cs-hidden');
        contractModal.classList.add('cs-grid');
        isContractModalOpen = true;

        contractModal.querySelector('#contract-supplier').textContent = response.supplier.username
        contractModal.querySelector('#contract-buyer').textContent = response.buyer.username
        contractModal.querySelector('#contract-service').textContent = response.service.name
        contractModal.querySelector('#contract-iscomplete').textContent = response.is_complete
        contractModal.querySelector('#contract-price').textContent = `${response.receipt.currency} ${response.receipt.amount_paid}`;
        
        // contractModal.querySelector('#view-product-page').href = `${BASE_URL}suppliers/products/${response.slug}`

        if (isContractModalOpen) {
            return
            contractModal.querySelector('#suspend-btn').addEventListener('click', (e) => openOperationConfirmModal(msg='Are you sure you want to suspend contract.', postUrl='test/', data={"id": response.id}))
        }
    }

    if (contractModalCloseActivator) {
        contractModalCloseActivator.addEventListener('click', () => {
            closecontractModel()
        })
    }
    // CONTRACT MODAL


    // track active tabs
    let activeTab = null;

    // utils
    // requests
    const fetchData = async (url, has_page_num=true) => {
        let response;
        if (has_page_num) {
            response = await fetch(`${BASE_API_URL}/${url}/?page=${pageNum}`, {

                method: "GET",
                headers: {
                    'Content-Type' : 'application/json'
                },
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
    // requests


    // render functions
    const renderSuppliers = async () => {
        if (!fetchState["supplier_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["supplier_was_loaded"] = true;
        }

        let response = await fetchData(url='suppliers');

        const tableBody = document.querySelector('#client-suppliers-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.business_name}</td>
                    <td>${record.country}</td>
                    <td>${record.vat_number}</td>
                    <td>${record.legal_etity_identifier}</td>
                    <td>${record.membership}</td>
                    <td>${record.stores}</td>
                    <td>${record.user.date_joined}</td>
                `;
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`supplier/${record.slug}`, has_page_num=false)
                        .then(response => openClientModal(response));                        
                    }
                })
            })
        }

        // change page number
        paginate(response, invoker = renderSuppliers);
    }

    const renderBuyer = async () => {
        if (!fetchState["buyer_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["buyer_was_loaded"] = true;
        }
        let response = await fetchData(url='buyers');

        const tableBody = document.querySelector('#client-buyers-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.business_name}</td>
                    <td>${record.country}</td>
                    <td>${record.vat_number}</td>
                    <td>${record.legal_etity_identifier}</td>
                    <td>${record.user.date_joined}</td>
                `;
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`buyer/${record.slug}`, has_page_num=false)
                        .then(response => openClientModal(response));                        
                    }
                })
            })
        }

        // change page number
        paginate(response, invoker = renderBuyer)
    }
    
    const renderProducts = async () => {
        if (!fetchState["products_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["products_was_loaded"] = true;
        }
        let response = await fetchData(url='products');

        const tableBody = document.querySelector('#client-products-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.supplier}</td>
                    <td>${record.sub_category.category.name}</td>
                    <td>${record.sub_category.name}</td>
                `;
                if (!record.is_verified) {
                    tableRow.classList.add("alert")
                }
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`product/${record.slug}`, has_page_num=false)
                        .then(response => openProductModal(response));                        
                    }
                })
            })
        }

        // change page number
        paginate(response, invoker = renderProducts)
    }
    
    const renderContracts = async () => {
        if (!fetchState["contracts_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["contracts_was_loaded"] = true;
        }
        let response = await fetchData(url='contracts');

        const tableBody = document.querySelector('#client-contracts-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.supplier.username}</td>
                    <td>${record.buyer.username}</td>
                    <td>${record.service.name}</td>
                    <td>${record.is_complete}</td>
                    <td>${record.is_accepted}</td>
                    <td>${record.receipt.currency} ${record.receipt.amount_paid}</td>
                    <td>${record.created_on}</td>
                `;
                tableBody.appendChild(tableRow);
                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`contract/${record.id}`, has_page_num=false)
                        .then(response => openContractModal(response));                      
                    }
                })
            })
        }

        paginate(response, invoker = renderContracts)
    }

    const renderStores = async () => {
        if (!fetchState["stores_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["stores_was_loaded"] = true;
        }
        let response = await fetchData(url='stores');

        const tableBody = document.querySelector('#client-stores-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);

                if (!record.is_verified) {
                    tableRow.classList.add("alert")
                    tableRow.innerHTML = `
                        <td>${i + 1}</td>
                        <td>${record.name}</td>
                        <td>${record.supplier}</td>
                        <td>${record.products}</td>
                        <td><button class="btn cs-grid cs-justify-center cs-align-center cs-bg-success cs-text-white cs-text-md br-sm" id="verify-store" style="padding: .5rem;inline-size: 10vw">Verify</button></td>
                    `;

                    tableRow.querySelector("#verify-store").addEventListener("click", () => {
                        fetch(`${BASE_API_URL}/stores/verify/${record.slug}`, {
                            method: "POST",
                            headers: {'X-CSRFToken': getCookie('csrftoken')},
                        })
                        .then(response => {
                            if (response.ok) {
                               renderStores()
                            }
                            else {
                                const err = document.createElement('p');
                                err.className = 'cs-text-md';
                                err.style.color = 'red';
                                // err.textContent = "An Error Occurred! Reload Page."
                                operationConfirmModal.querySelector('#msg').appendChild(err);
                            }
                        })
                    })
                }
                else {
                    tableRow.innerHTML = `
                        <td>${i + 1}</td>
                        <td class="store-name">${record.name}</td>
                        <td>${record.supplier}</td>
                        <td>${record.products}</td>
                        <td><button class="btn cs-grid cs-justify-center cs-align-center cs-bg-danger cs-text-white cs-text-md br-sm" id="suspend-store" style="padding: .5rem;inline-size: 10vw">Suspend</button></td>
                    `;

                    tableRow.querySelector("#suspend-store").addEventListener("click", () => {
                        fetch(`${BASE_API_URL}/stores/delete/${record.slug}`, {
                            method: "POST",
                            headers: {'X-CSRFToken': getCookie('csrftoken')},
                        })
                        .then(response => {
                            if (response.ok) {
                               renderStores()
                            }
                            else {
                                const err = document.createElement('p');
                                err.className = 'cs-text-md';
                                err.style.color = 'red';
                                err.textContent = "An Error Occurred! Reload Page."
                                operationConfirmModal.querySelector('#msg').appendChild(err);
                            }
                        })
                    })
                    tableRow.querySelector(".store-name").addEventListener('click', () => {
                        window.open(`${BASE_URL}suppliers/store/${record.slug}`, '_blank');
                    })
                }
                tableBody.appendChild(tableRow);

                // tableRow.addEventListener("mouseover", () => {
                //     const _iframe = document.createElement("iframe")
                //     _iframe.style.position = "fixed"
                //     _iframe.style.inset = "0 0"
                //     _iframe.style.width = "50vw"
                //     _iframe.style.height = "50vh"
                //     _iframe.src = `${BASE_URL}suppliers/store/${record.slug}`
                //     document.body.appendChild(_iframe)
                // })

            })
        }

        // change page number
        paginate(response, invoker = renderStores)

    }
    
    const renderAdverts = async () => {
        if (!fetchState["adverts_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["adverts_was_loaded"] = true;
        }
        let response = await fetchData(url='adverts');

        const tableBody = document.querySelector('#client-adverts-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count;
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.product.slice(0,50)}</td>
                    <td>${record.supplier}</td>
                    <td>${record.amount}</td>
                    <td>${record.start_date}</td>
                    <td>${record.end_date}</td>
                `;
                
                if ((new Date(record.end_date) > new Date()) && record.is_active == true) {
                    tableRow.classList.add("active")
                }
                tableBody.appendChild(tableRow);
                // tableRow.addEventListener('click', async () => {
                //     if (!isClientModalOpen) {
                //         // fetch client data
                //         // open modal
                //         fetchData(`product/${record.slug}`, has_page_num=false)
                //         .then(response => openProductModal(response));                        
                //     }
                // })
            })
        }

        // change page number
        paginate(response, invoker = renderProducts)
    }
    
    // detect page
    const nav = document.querySelector('nav[data-page]');
    
    // client page
    // if (nav && nav.dataset['page'] === 'client') {
        const clientRoutes = ["client-overview", "client-suppliers", "client-adverts", "client-buyers","client-stores", "client-contracts","client-products","client-buyers-overview","client-stores-overview","client-products-overview", "client-contracts-overview","client-suppliers-overview","client-adverts-overview"];
        
        // SWITCHING TABS
        activeTab = clientRoutes[0];
        
        clientRoutes.forEach(route => {
            const activator = document.querySelector(`#${route}-activator`);
            const section = document.querySelector(`#${route.split('-').slice(0,2).join('-')}-section`);

            if (route === activeTab) {
                try {
                    activator.classList.add('active');
                    section.classList.remove('cs-hidden');
                    section.classList.add('cs-grid');
                } catch (e)  {

                }
            }

            if(activator) {
                activator.addEventListener('click', () => {
                    if (activator.id != `${activeTab}-activator`) {
                        
                        // change active tab state
                        document.querySelector(`#${activeTab}-activator`).classList.remove('active');
                        document.querySelector(`#${activeTab}-section`).classList.remove('cs-grid');
                        document.querySelector(`#${activeTab}-section`).classList.add('cs-hidden');

                        section.classList.remove('cs-hidden');
                        section.classList.add('cs-grid');
                        
                        activeTab = activator.id.split('-').slice(0,2).join('-');                    
                        document.querySelector(`#${activeTab}-activator`).classList.add('active');

                        // fetch data
                        if (activeTab.includes('supplier')) {
                            renderSuppliers();
                        }
                        else if (activeTab.includes('buyers')) {
                            renderBuyer();
                        }
                        else if (activeTab.includes('products')) {
                            renderProducts();
                        }
                        else if (activeTab.includes('contracts')) {
                            renderContracts();
                        }
                        else if (activeTab.includes('stores')) {
                            renderStores();
                        }
                        else if (activeTab.includes('adverts')) {
                            renderAdverts();
                        }

                    }
                });
            }
        });

        // SWITCHING TABS      

        
    // }
    
    // client page


    // manager page

                
    const closeServiceModel = () => {
        serviceModal.classList.remove('cs-grid');
        serviceModal.classList.add('cs-hidden');
        isServiceModalOpen = false;
        document.body.classList.remove('modal-open');
    }
    if (serviceModalCloseActivator)
    serviceModalCloseActivator.addEventListener('click', () => closeServiceModel());

    const openServiceModel = async (response) => {
        // fetch
        data = await fetchData();

        document.body.classList.add('modal-open');
        serviceModal.classList.remove('cs-hidden');
        serviceModal.classList.add('cs-grid');
        isServiceModalOpen = true;
        
        serviceModal.querySelector('#modal-service-name').textContent = response.name
        serviceModal.querySelector('#modal-service-description').textContent = response.description
        
        if (isServiceModalOpen) {
            serviceModal.querySelector('#suspend-btn').addEventListener('click', (e) => {
                openOperationConfirmModal(msg='Are you sure you want to delete this service.', postUrl='test/', data={"id": response.id})
            })
        }
    }

    const renderShowrooms = async () => {
        
        if (!fetchState["showrooms_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["showrooms_was_loaded"] = true;
        }
        let response = await fetchData(url='showrooms');

        const tableBody = document.querySelector('#manager-showroom-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.name}</td>
                    <td>${record.store.length}</td>
                    <td>${record.products}</td>
                `;
                tableBody.appendChild(tableRow);
            })
        }
        
        // change page number
        paginate(response, invoker = renderShowrooms);
    }

    const renderServices = async () => {
        if (!fetchState["services_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["services_was_loaded"] = true;
        }
        let response = await fetchData(url='services');

        const tableBody = document.querySelector('#manager-services-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.name}</td>
                    <td>${record.description.slice(0,200)} ...</td>
                `;
                tableBody.appendChild(tableRow);

                tableRow.addEventListener('click', async () => {
                    if (!isClientModalOpen) {
                        // fetch client data
                        // open modal
                        fetchData(`service/${record.slug}`, has_page_num=false)
                        .then(response => openServiceModel(response));                        
                    }
                })
            })


            // change page number
            paginate(response, invoker = renderServices);
        }
    }

    const renderMemberships = async () => {
        if (!fetchState["services_was_loaded"]) {
            // if it is the first time we are loading suppliers, we set pageNum to 1
            pageNum = 1;
            fetchState["services_was_loaded"] = true;
        }
        let response = await fetchData(url='memberships');

        const tableBody = document.querySelector('#manager-memberships-section table tbody');

        if (tableBody.childNodes.length > 0) {
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            document.querySelector('#table-item-count').textContent = response.count
    
            response.results.forEach((record, i) => {
                let tableRow = document.createElement('tr')
                tableRow.classList = 'cs-text-md cs-font-500 client-item';
                if (record.status) {
                    tableRow.classList.add("active")
                }
                tableRow.setAttribute('data-slug', record.slug);
                tableRow.setAttribute('data-id', record.id);
                tableRow.setAttribute('data-account-type', record.account_type);
                tableRow.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${record.profile}</td>
                    <td>${record.feature.name}</td>
                    <td>${record.created_on}</td>
                    <td>${record.billing_period_end_date}</td>
                `;
                tableBody.appendChild(tableRow);

                // tableRow.addEventListener('click', async () => {
                //     if (!isClientModalOpen) {
                //         // fetch client data
                //         // open modal
                //         fetchData(`service/${record.slug}`, has_page_num=false)
                //         .then(response => openServiceModel(response));                        
                //     }
                // })
            })


            // change page number
            paginate(response, invoker = renderMemberships);
        }
    }

        // client page
        if (nav && nav.dataset['page'] === 'manager') {
            const clientRoutes = ["manager-overview", "manager-showroom","manager-services", "manager-memberships","manager-showroom-overview","manager-services-overview","manager-memberships-overview"];
            
            // SWITCHING TABS
            activeTab = clientRoutes[0];
            
            clientRoutes.forEach(route => {
                const activator = document.querySelector(`#${route}-activator`);
                const section = document.querySelector(`#${route.split('-').slice(0,2).join('-')}-section`);
    
                if (route === activeTab) {
                    activator.classList.add('active');
                    section.classList.remove('cs-hidden');
                    section.classList.add('cs-grid');
                }
    
                if(activator) {
                    activator.addEventListener('click', () => {
                        if (activator.id != `${activeTab}-activator`) {
                            
                            // change active tab state
                            document.querySelector(`#${activeTab}-activator`).classList.remove('active');
                            document.querySelector(`#${activeTab}-section`).classList.remove('cs-grid');
                            document.querySelector(`#${activeTab}-section`).classList.add('cs-hidden');
    
                            section.classList.remove('cs-hidden');
                            section.classList.add('cs-grid');
                            
                            activeTab = activator.id.split('-').slice(0,2).join('-');                    
                            document.querySelector(`#${activeTab}-activator`).classList.add('active');
    
                            // fetch data


                            // fetch data
                            if (activeTab.includes('showroom')) {
                                renderShowrooms();
                            }
                            else if (activeTab.includes('service')) {
                                renderServices();
                            }
                            else if (activeTab.includes('memberships')) {
                                renderMemberships();
                            }
                        }
                    });
                }
            });
    
            // SWITCHING TABS
        }    

    // manager page


    function closeAllModals() {
        document.querySelectorAll(".modal").forEach(
            modal => {
                document.body.classList.remove('modal-open');
                modal.classList.add("cs-hidden")
                modal.classList.remove("cs-grid")
            }
        )
    }


    // CONFIRM MODAL
    const openOperationConfirmModal = (msg, postUrl, renderFunc) => {
        operationConfirmModal.querySelector('#confirm-msg').textContent = msg;
        operationConfirmModal.querySelector('form').action = `${BASE_API_URL}/${postUrl}`;

        document.body.classList.add('modal-open');
        operationConfirmModal.classList.remove('cs-hidden');
        operationConfirmModal.classList.add('cs-grid');
        isOperationConfirmModal = true;

        if (operationConfirmModal) {
            operationConfirmModal.querySelector('#cancel-operation').addEventListener('click', () => {
                operationConfirmModal.classList.add('cs-hidden');
                operationConfirmModal.classList.remove('cs-grid');
                isOperationConfirmModal = false;
            })

            operationConfirmModal.querySelector('form').addEventListener('submit', (e) => {
                e.preventDefault();

                fetch(`${BASE_API_URL}/${postUrl}`, {
                    method: "POST",
                    headers: {'X-CSRFToken': getCookie('csrftoken')},
                })
                .then(response => {
                    if (response.ok) {
                        // window.location.reload()
                        // close all modals
                        closeAllModals()
                        renderFunc()
                    }
                    else {
                        const err = document.createElement('p');
                        err.className = 'cs-text-md';
                        err.style.color = 'red';
                        err.textContent = "An Error Occurred! Reload Page."
                        operationConfirmModal.querySelector('#msg').appendChild(err);
                    }
                })
            })
        }
    }
    // CONFIRM MODAL

    document.querySelectorAll('table td:not(.delete)').forEach(cell => {
        const MAXWORDCOUNT = 13;
        if (cell.textContent.split(" ").length > MAXWORDCOUNT) {
            cell.textContent = `${cell.textContent.split(" ").slice(0, MAXWORDCOUNT).join(" ")} ....`
        }
    })

    const handleAddInput = (target, subCategoryCount, subCategoryGroup, lastAddElem) => {
        if (subCategoryCount == 10) return;
        // remove add btn
        lastAddElem.removeChild(target)
        const deleteInputBtn = lastAddElem.querySelector('.delete-input');

        // add delete btn
        deleteInputBtn.classList.remove('cs-hidden');
        deleteInputBtn.classList.add('cs-grid');

        // handle delete inputs
        deleteInputBtn.addEventListener('click', (e) => {
            subCategoryGroup.removeChild(subCategoryGroup.querySelector(`.subcategory-inputs[data-subcategorycount="${subCategoryCount}"]`));
        })

        // create form element
        const subCategoryElem = document.createElement('div');
        subCategoryElem.classList.add(...['cs-grid', 'cs-align-center', 'subcategory-inputs']);

        subCategoryElem.innerHTML = `
            <input type="text" name='subcategory-${subCategoryCount + 1}' id="subcategory-${subCategoryCount + 1}" placeholder="Sub Category Name" required>
            <input type="file" name="sub-category-image-${subCategoryCount + 1}" id="sub-category-image-${subCategoryCount + 1}" required>
            <button class="btn cs-grid cs-justify-center cs-align-center cs-bg-hover-color cs-text-secondary br-full" id="add-input" style="padding: 1rem .5rem;" onclick="(function(){
            })();return false;">
                <i class="fa fa-plus"></i>
            </button>

            <button class="btn cs-justify-center cs-align-center cs-bg-hover-color cs-text-secondary br-full cs-hidden delete-input" data-subcategoryDeleteCcount="${subCategoryCount + 1}" style="padding: 1rem .5rem;" onclick="(function(){
            })();return false;">
                <i class="fa fa-trash"></i>
            </button>
        `
        let _subCategoryCount = subCategoryCount + 1;
        
        subCategoryElem.dataset['subcategorycount'] = _subCategoryCount;
        subCategoryGroup.appendChild(subCategoryElem);

        lastAddElem = subCategoryElem;

        const addInputBtn = lastAddElem.querySelector('#add-input');
        addInputBtn.addEventListener('click', () => handleAddInput(addInputBtn, _subCategoryCount, subCategoryGroup, lastAddElem));
    }

    // add form inputs
    const categoryForm = document.querySelector('#category-form');
    if (categoryForm && categoryForm != undefined) {
        let subCategoryCount = 1;
        const subCategoryGroup = document.querySelector('#subCategory-group');
        let lastAddElem = document.querySelector(`.subcategory-inputs[data-subcategorycount="1"]`)


        const addInputBtn = lastAddElem.querySelector('#add-input');
        addInputBtn.addEventListener('click', () => handleAddInput(addInputBtn, subCategoryCount, subCategoryGroup, lastAddElem));
    }

    // active tba should not reload page
    document.querySelectorAll('a').forEach(tab => {
        tab.addEventListener('click', (e) => {
            if ((e.target.classList.contains('active') && !e.target.classList.contains('manager')) || (e.target.parentNode.classList.contains('active') && !e.target.parentNode.classList.contains('manager'))) {
                e.preventDefault();
            }
        })
    })

    // notification popup
    const notificationCta = document.querySelector('.notification-cta');
    const notificationPopup =  document.querySelector('.notification-list')
    notificationCta.addEventListener('click', () => {
        notificationPopup.classList.toggle('cs-hidden');
        notificationPopup.classList.toggle('cs-grid');
    });

    const navEmphCta = document.querySelector('#nav-emph-cta');
    if (navEmphCta) {
        navEmphCta.addEventListener('click', () => {
            const ctaEmph = document.querySelector('.cta-emph');
            ctaEmph.classList.toggle('cs-hidden');
            ctaEmph.classList.toggle('cs-grid');
        });
    }
});

if(window.innerWidth < 800)
{
    if (window.location.href.includes('/admin/') || window.location.href.includes('dashboard')) {
        let domain = full = location.protocol + '//' + location.host
        window.location.replace(`${domain}/blocked`);
    }
}