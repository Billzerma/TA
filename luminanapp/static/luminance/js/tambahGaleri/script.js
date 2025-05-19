    const imageInput = document.getElementById('inputGroupFile02');
    const imagePreview = document.getElementById('imagePreview');
    const cardPreview = document.getElementById('cardPreview');

    imageInput.addEventListener('change', (event) => {
        const file = event.target.files[0];

        if (file) {
            imagePreview.src = URL.createObjectURL(file);
            cardPreview.style.display = 'block'; // Tampilkan card
        } else {
            cardPreview.style.display = 'none'; // Sembunyikan card jika tidak ada gambar
        }
    });