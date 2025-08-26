// class Modal {
//     // Build the template
//     static build(product) {
//         const template = document.createElement('div');
//         template.innerHTML = `
//             <div class="modal">
//             <div class="modal-head">
//                 <h2>Edit Product</h2>
//                 <i class="ti-close" id="close-modal"></i>
//             </div>
//             <div class="modal-body">
//                 <div class="edit-form">
//                     <form action="">
//                         <div class="" style="position:relative;z-index:5;block-size:auto;width:fit-content;">
//                             <div
//                                 style="background-color:#fff;padding:0 .2rem;width:fit-content;block-size:auto;position:absolute;z-index:10;top:1%;left:0%;transform: translate(50%, -50%);">
//                                 <h3 class="flex" style="margin:0;">Product Details</h3>
//                             </div>
//                             <div class="product-name-category"
//                                 style="justify-content:flex-start;block-size:fit-content;border:1px solid rgb(238, 234, 234);border-radius:0;padding:.8rem .6rem;">
//                                 <div class="flex" style="gap:.4rem;margin-top:.8rem;">
//                                     <div class="form-control">
//                                         <label for="produt-name">Product Name</label>
//                                         <input type="text" name="product-name" id="product-name" value="${product.name}">
//                                     </div>
//                                     <div class="form-control">
//                                         <label for="produt-model">Model</label>
//                                         <input type="text" name="product-model" id="product-model"
//                                             value="${product.model}">
//                                     </div>
//                                     <div class="form-control">
//                                         <label for="produt-serial">Serial Number</label>
//                                         <input type="text" name="product-serial" id="product-serial" value="${product.serialNumber}">
//                                     </div>
//                                     <div class="form-control">
//                                         <label for="product-category">Category</label>
//                                         <select name="product-category" id="product-category">
//                                             <option value="">${product.category}</option>
//                                             <option value="">Gadgets</option>
//                                             <option value="">Gadgets</option>
//                                             <option value="">Gadgets</option>
//                                             <option value="">Gadgets</option>
//                                         </select>
//                                     </div>
//                                     <div class="form-control">
//                                         <label for="produt-price">Product Price</label>
//                                         <input type="text" name="product-price" id="product-price" value="${product.price}">
//                                     </div>
//                                 </div>

//                                 <div class="form-control" style="margin-top:.8rem;">
//                                     <label for="product-description">Description</label>
//                                     <textarea name="product-description" id="product-description" cols="30"
//                                         rows="10">${product.description}</textarea>
//                                 </div>
//                             </div>
//                         </div>
//                         <div class="" style="position:relative;z-index:5;block-size:auto;width:100%;margin-top:1.6rem;">
//                             <div
//                                 style="background-color:#fff;padding:0 .2rem;width:fit-content;block-size:auto;position:absolute;z-index:10;top:1%;left:0%;transform: translate(50%, -50%);">
//                                 <h3 class="flex" style="margin:0;">Product Images</h3>
//                             </div>
//                             <div class="product-name-category"
//                                 style="justify-content:flex-start;block-size:fit-content;border:1px solid rgb(238, 234, 234);border-radius:0;padding:.8rem .6rem;width:100%;">
//                                 <div class="form-control" style="margin-top:.4rem;">
//                                     <label for="product-image"></label>
//                                     <input type="file" name="product-image" id="product-image">
//                                 </div>
//                             </div>
//                         </div>
//                         <div class="product-save-cancel flex mt-5" style="margin-top:.8rem;">
//                             <div class="form-control">
//                                 <input type="submit" value="Save" name="btn-create" class="btn">
//                             </div>
//                             <div class="form-control">
//                                 <input type="submit" value="Cancel" name="btn-cancel" class="btn">
//                             </div>
//                         </div>
//                     </form>
//                 </div>
//             </div>
//             <div class="modal-foot">

//             </div>
//         </div>
//         `;
//         return template;
//     }

//     // Display the modal
//     static show(product) {
//         const modal = this.build(product);
//         document.body.appendChild(modal);
//     }

//     // Remove the modal
//     static hide(event) {
//         const modal = event.target.parentElement.parentElement.parentElement;
//         document.body.removeChild(modal);
//     }

// }