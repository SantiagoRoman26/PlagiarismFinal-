window.onload = function() {
  var form = document.querySelector('form');
  var progressBar = document.getElementById('progress-bar');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var fileInput = document.querySelector('input[type="file"]');
    var file = fileInput.files[0];

    if (file) {
      var formData = new FormData();
      formData.append('archivo', file);

      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/documento/upload', true);

      // Obtener el valor del token CSRF del formulario
      var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

      // Adjuntar el token CSRF en el encabezado de la solicitud
      xhr.setRequestHeader('X-CSRFToken', csrfToken);

      xhr.upload.addEventListener('progress', function(e) {
        var percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
      });

      xhr.onload = function() {
        if (xhr.status === 200) {
          // La solicitud AJAX se completó con éxito, redirigir al usuario a la vista visualizar_archivo
          var response = JSON.parse(xhr.responseText);
          window.location.href = response.redirect_url;
        } else {
          // La solicitud AJAX no se completó correctamente, mostrar mensaje de error o tomar alguna acción apropiada
          console.error('Error en la solicitud AJAX');
        }
      };

      xhr.send(formData);
    }
  });
};
