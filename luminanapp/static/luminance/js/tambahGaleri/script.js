const imageInput = document.getElementById('inputGroupFile02');
const imagePreview = document.getElementById('imagePreview');
const cardPreview = document.getElementById('cardPreview');


const titleInput = document.getElementById('judulGaleri');
const descriptionInput = document.getElementById('deskripsiGaleri');


const previewTitle = document.getElementById('previewTitle');
const previewDescription = document.getElementById('previewDescription');

imageInput.addEventListener('change', (event) => {
    const file = event.target.files[0];

    if (file) {
        imagePreview.src = URL.createObjectURL(file);
        
        cardPreview.style.display = 'block'; 
    } else {
        
        if (!titleInput.value && !descriptionInput.value) {
            cardPreview.style.display = 'none'; 
        }
    }
});


titleInput.addEventListener('input', (event) => {

    previewTitle.textContent = event.target.value;
 
    if (event.target.value || imageInput.files.length > 0 || descriptionInput.value) {
        cardPreview.style.display = 'block';
    } else {
        cardPreview.style.display = 'none';
    }
});

// Event listener untuk input deskripsi
descriptionInput.addEventListener('input', (event) => {
    // Perbarui teks pratinjau deskripsi
    previewDescription.textContent = event.target.value;
    // Tampilkan card jika ada input deskripsi (dan belum terlihat)
    if (event.target.value || imageInput.files.length > 0 || titleInput.value) {
        cardPreview.style.display = 'block';
    } else {
        cardPreview.style.display = 'none';
    }
});

// Opsional: Atur nilai awal pratinjau saat halaman dimuat
document.addEventListener('DOMContentLoaded', () => {
    if (titleInput.value) {
        previewTitle.textContent = titleInput.value;
    }
    if (descriptionInput.value) {
        previewDescription.textContent = descriptionInput.value;
    }
    // Jika ada nilai awal, tampilkan card
    if (titleInput.value || descriptionInput.value || imageInput.files.length > 0) {
        cardPreview.style.display = 'block';
    }
});