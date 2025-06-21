
  document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("inputProfilePicture");
    if (fileInput) {
      fileInput.addEventListener("change", function () {
        document.getElementById("formFoto").submit();
      });
    }
  });


  document.addEventListener('DOMContentLoaded', function () {
    const galleryDropdownButton = document.getElementById('galleryDropdown');
    const statsPlaceholder = document.getElementById('stats-placeholder');
    const statsContent = document.getElementById('stats-content');

    // Inisialisasi Chart (kosong pada awalnya)
    let visitsChart, stylesChart;

    const pieChartCanvas = document.getElementById('stylesPieChart').getContext('2d');
    stylesChart = new Chart(pieChartCanvas, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e'], // Primary, Success, Info, Warning
                hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#dda20a'],
                hoverBorderColor: "rgba(234, 236, 244, 1)",
            }],
        },
        options: {
            maintainAspectRatio: false,
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                borderColor: '#dddfeb',
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
            },
            legend: {
                display: false
            },
            cutoutPercentage: 80,
        },
    });

    const areaChartCanvas = document.getElementById('visitsAreaChart').getContext('2d');
    visitsChart = new Chart(areaChartCanvas, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Kunjungan",
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                borderColor: "rgba(78, 115, 223, 1)",
                pointRadius: 3,
                pointBackgroundColor: "rgba(78, 115, 223, 1)",
                pointBorderColor: "rgba(78, 115, 223, 1)",
                pointHoverRadius: 3,
                pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: [],
            }],
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                xAxes: [{ time: { unit: 'date' }, gridLines: { display: false, drawBorder: false }, ticks: { maxTicksLimit: 7 } }],
                yAxes: [{ ticks: { maxTicksLimit: 5, padding: 10, callback: function(value) { if (Number.isInteger(value)) { return value; } } }, gridLines: { color: "rgb(234, 236, 244)", zeroLineColor: "rgb(234, 236, 244)", drawBorder: false, borderDash: [2], zeroLineBorderDash: [2] } }],
            },
            legend: { display: false },
        }
    });

    // Fungsi untuk mengambil dan menampilkan data
    async function fetchAndDisplayStats(galleryId) {
        // Tampilkan loading spinner atau semacamnya jika ada
        statsContent.style.display = 'none';
        statsPlaceholder.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        statsPlaceholder.style.display = 'block';

        try {
            const response = await fetch(`/api/stats/gallery/${galleryId}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // Update UI dengan data baru
            document.getElementById('total-likes-value').textContent = data.total_likes;
            
            // Update Area Chart (Kunjungan)
            visitsChart.data.labels = data.area_chart.labels;
            visitsChart.data.datasets[0].data = data.area_chart.data;
            visitsChart.update();

            // Update Pie Chart (Gaya Lukis)
            stylesChart.data.labels = data.pie_chart.labels;
            stylesChart.data.datasets[0].data = data.pie_chart.data;
            stylesChart.update();
            
            // Generate Legenda Pie Chart
            const legendContainer = document.getElementById('pie-chart-legend');
            legendContainer.innerHTML = '';
            const colors = stylesChart.data.datasets[0].backgroundColor;
            data.pie_chart.labels.forEach((label, index) => {
                const legendItem = `
                    <span class="me-2">
                        <i class="fas fa-circle" style="color:${colors[index % colors.length]}"></i> ${label}
                    </span>`;
                legendContainer.innerHTML += legendItem;
            });

            // Tampilkan konten statistik
            statsPlaceholder.style.display = 'none';
            statsContent.style.display = 'block';

        } catch (error) {
            console.error("Gagal mengambil data statistik:", error);
            statsPlaceholder.innerHTML = '<h4 class="text-danger">Terjadi kesalahan saat memuat data.</h4>';
            statsPlaceholder.style.display = 'block';
            statsContent.style.display = 'none';
        }
    }

    // Tambahkan event listener ke setiap item dropdown
    document.querySelectorAll('.gallery-select-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const galleryId = this.dataset.galleryId;
            const galleryName = this.textContent;
            
            // Update tombol dropdown untuk menampilkan galeri yang dipilih
            galleryDropdownButton.textContent = galleryName;
            
            // Panggil fungsi untuk memuat data
            fetchAndDisplayStats(galleryId);
        });
    });
});
