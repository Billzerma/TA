
  const fileInput = document.getElementById("editThumbGaleri");
  const imagePreview = document.getElementById("imagePreview");

  fileInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (event) {
        imagePreview.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  });

document.addEventListener('DOMContentLoaded', function() {
  // 1. Cari elemen kontainer yang menyimpan data prediksi dari Django
  const dataContainer = document.getElementById('prediction-data-container');

  // 2. Jika elemen dan datanya ada, lanjutkan
  if (dataContainer && dataContainer.dataset.prediction) {
    try {
      // Ambil string JSON dari atribut 'data-prediction' dan parse
      const predictionData = JSON.parse(dataContainer.dataset.prediction);

      // Ambil elemen modal dari DOM
      const predictionModalElement = document.getElementById('predictionResultModal');
      
      if (predictionModalElement) {
        // Isi konten modal dengan data
        document.getElementById('modalPredictionStyle').textContent = predictionData.predicted_style;
        document.getElementById('modalConfidenceScore').textContent = predictionData.confidence + '%';

        const allConfidencesList = document.getElementById('modalAllConfidences');
        allConfidencesList.innerHTML = ''; // Kosongkan list untuk jaga-jaga

        // Urutkan confidence dari tertinggi ke terendah
        const sortedConfidences = Object.entries(predictionData.all_confidences)
          .sort(([, a], [, b]) => b - a);

        // Buat list item untuk setiap confidence
        for (const [style, score] of sortedConfidences) {
          const listItem = document.createElement('li');
          listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
          listItem.innerHTML = `${style} <span class="badge bg-primary rounded-pill">${score}%</span>`;
          allConfidencesList.appendChild(listItem);
        }

        // Buat instance modal Bootstrap dan tampilkan
        const predictionModal = new bootstrap.Modal(predictionModalElement);
        predictionModal.show();
      }
    } catch (e) {
      console.error("Gagal mem-parsing data prediksi JSON:", e);
    }
  }
});