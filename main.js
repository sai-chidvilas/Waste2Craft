document.addEventListener('DOMContentLoaded', () => {
    // Image Preview for Uploads
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.classList.add('hidden');
            }
        });
    }

    // Dynamic Search for Eco-Marketplace
    const productSearch = document.getElementById('product-search');
    if (productSearch) {
        productSearch.addEventListener('input', (event) => {
            const searchTerm = event.target.value.toLowerCase();
            const products = document.querySelectorAll('.product-item');
            products.forEach((product) => {
                const name = product.dataset.name;
                if (name.includes(searchTerm)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        });
    }

    // Dynamic Search for Waste Listings
    const wasteSearch = document.getElementById('waste-search');
    if (wasteSearch) {
        wasteSearch.addEventListener('input', (event) => {
            const searchTerm = event.target.value.toLowerCase();
            const listings = document.querySelectorAll('.waste-item');
            listings.forEach((listing) => {
                const title = listing.dataset.title;
                const category = listing.dataset.category;
                if (title.includes(searchTerm) || category.includes(searchTerm)) {
                    listing.style.display = 'block';
                } else {
                    listing.style.display = 'none';
                }
            });
        });
    }
});