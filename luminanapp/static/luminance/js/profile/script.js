
  document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("inputProfilePicture");
    if (fileInput) {
      fileInput.addEventListener("change", function () {
        document.getElementById("formFoto").submit();
      });
    }
  });

