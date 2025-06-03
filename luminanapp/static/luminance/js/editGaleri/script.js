
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

