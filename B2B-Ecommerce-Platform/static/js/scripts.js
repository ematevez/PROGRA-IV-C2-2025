document.addEventListener('DOMContentLoaded', () => {

    if (window.location.href.includes('/ar/')) {
        document.body.classList.add('rtl');
    }

    // global state
    let IsMobileMenuOpen = false;

    const imgMagnifier = document.querySelector('.img-magnifier');
    const productImagesContainer = document.querySelector('.product-images-list');

    if ((imgMagnifier && imgMagnifier != null) && (productImagesContainer && productImagesContainer != null)) {
        
        const productImgs = productImagesContainer.querySelectorAll('img');
        const productVideos = productImagesContainer.querySelectorAll('video');
        let activeMedia = productImgs[0];
        activeMedia.classList.add('active');
        
        // set initial image
        let mainImg = imgMagnifier.querySelector('img');
        mainImg.src = activeMedia.src;
        let mainVideo = imgMagnifier.querySelector('video');

        productImgs.forEach(img => img.addEventListener('click', () => {
            if (mainImg.style.display == "none") {
                mainVideo.pause()
                mainImg.style.display = "block"
                mainVideo.style.display = "none"
            }
            activeMedia.classList.remove('active');
            activeMedia = img;
            mainImg.src = activeMedia.src;
            activeMedia.classList.add('active');
        }));
        productVideos.forEach(vid => vid.addEventListener('click', () => {
            if (mainVideo.style.display == "none") {
                mainVideo.style.display = "block"
                mainImg.style.display = "none"
            }
            activeMedia.classList.remove('active');
            activeMedia = vid;
            mainVideo.src = activeMedia.src;
            activeMedia.classList.add('active');
        }));

        // magnify product image
        imgMagnifier.addEventListener('mouseenter', (e) => {
            
            // // scale up image
            // mainImg.style.transform = 'scale(1.2)';

            // // move image
            // mainImg.style.transform = `translate(${-(e.clientX /e.clientX) +10 }px, ${-e.clientY}px)`
        })
    }


    // make header sticky
    const navBar = document.querySelector('nav');
    document.addEventListener('scroll', function(e) {
        if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
            navBar.classList.remove('bg-lghterBackgroundColor');
            navBar.classList.add('bg-white');
            navBar.classList.add("cs-fixed");
            navBar.classList.add("card");

            navBar.querySelectorAll('.text-white').forEach(tab => {
                tab.classList.remove('text-white');
                tab.classList.add('text-lghterBackgroundColor');
            })
        }
        else {
            navBar.classList.add('bg-lghterBackgroundColor');
            navBar.classList.remove('bg-white');
            navBar.classList.remove("cs-fixed");
            navBar.classList.remove("card");

            navBar.querySelectorAll('ul.text-lghterBackgroundColor').forEach(tab => {
                tab.classList.add('text-white');
                tab.classList.remove('text-lghterBackgroundColor');
            })
        }
    })

    // mobile menu
    const mobileMenuActivator = document.querySelector('#mobile-menu-activator');
    const mobileMenu = document.querySelector('#mobile-menu');
    mobileMenuActivator.addEventListener('click', () => {
        if (!IsMobileMenuOpen) {
            IsMobileMenuOpen = true;
            mobileMenu.classList.add('open');
            document.body.classList.add('menuOpen');
        }
        else {
            IsMobileMenuOpen = false;
            mobileMenu.classList.remove('open');
            document.body.classList.remove('menuOpen');
        }
    })

    // mobile search bar
    const mobileSearchbarActivator = document.querySelector('#mobile-searchbar-activator');
    const mobileSearchbar = document.querySelector('#mobile-searchbar');
    
    mobileSearchbarActivator.addEventListener('click', () => {
        mobileSearchbar.classList.toggle('open');
        if (mobileSearchbar.classList.contains('open')) {
            mobileSearchbarActivator.querySelector('i').classList.remove('fa-search');
            mobileSearchbarActivator.querySelector('i').classList.add('fa-close');
        } else {
            mobileSearchbarActivator.querySelector('i').classList.add('fa-search');
            mobileSearchbarActivator.querySelector('i').classList.remove('fa-close');
        }
    })

    

    // close mobile menu
    document.body.addEventListener('click', (e) => {
        if (IsMobileMenuOpen && e.target != mobileMenu && e.target != mobileMenuActivator && e.target != mobileMenuActivator.querySelector('i')) {
            IsMobileMenuOpen = false;
            mobileMenu.classList.remove('open');
            document.body.classList.remove('menuOpen');
        }
    })

    // set default dates for contract forms
    const setDefaultDate = () => {
        
        const startDate = document.querySelector('#contract-start-date');
        const endDate = document.querySelector('#contract-end-date');

        if ((startDate && startDate != null) && (endDate && endDate != null)) {

            var date = new Date();
    
            var day = date.getDate();
            var month = date.getMonth() + 1;
            var year = date.getFullYear();
    
            if (month < 10) month = "0" + month;
            if (day < 10) day = "0" + day;
    
            var today = year + "-" + month + "-" + day;

            // after year
            var afterYear = (year + 1) + "-" + month + "-" + day;
    
            startDate.value = today;
            endDate.value = afterYear;

        }

    }
    
    setDefaultDate();


    // // responsive store cards
    // const storeListSm = document.querySelector('.store-list-sm');
    // if (storeListSm && storeListSm != undefined) {
    //     const storeCardProducts = document.querySelectorAll('.store-card-sm .products');
    //     storeCardProducts.forEach(card => {
    //         let productCount = card.querySelectorAll('a.product').length;
    //         card.classList.add(`grid-cols-${productCount}`);
    //     })
    // }

})


// if(window.innerWidth < 800)
// {
//     if (window.location.href.includes('/admin/') || window.location.href.includes('/dashboard/')) {
//         window.location.href = `${location.hostname}/blocked`;
//     }
// }

