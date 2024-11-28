window.onload = function() {
  var form = document.querySelector('form');
  var progressBar = document.getElementById('progress-bar');
  var noFileSelectedMessage = document.getElementById('no-file-selected');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var fileInput = document.querySelector('input[type="file"]');
    var file = fileInput.files[0];

    if (file) {
      noFileSelectedMessage.textContent = '';  // Restablecemos el mensaje si hay un archivo seleccionado

      var formData = new FormData();
      formData.append('archivo', file);

      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/integriscan/documento/upload', true);

      // Obtener el valor del token CSRF del formulario
      var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

      // Adjuntar el token CSRF en el encabezado de la solicitud
      xhr.setRequestHeader('X-CSRFToken', csrfToken);

      xhr.upload.addEventListener('progress', function(e) {
        var percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
      });

      xhr.onload = function() {
        console.error("inicio de la funcion");
        if (xhr.status === 200) {
          try {
            var response = JSON.parse(xhr.responseText);
            if (response.redirect_url) {
              window.location.href = response.redirect_url;
            } else {
              console.error('Respuesta válida, pero falta "redirect_url". Respuesta completa:', response);
            }
          } catch (e) {
            console.error('Error al analizar la respuesta JSON:', e, 'Respuesta recibida:', xhr.responseText);
          }
        } else {
          console.error('Error en la solicitud AJAX:', {
            status: xhr.status,
            statusText: xhr.statusText,
            response: xhr.responseText
          });
        }
      };
      
      xhr.onerror = function() {
        console.error('Error de red en la solicitud AJAX:', {
          status: xhr.status,
          statusText: xhr.statusText
        });
      };
      
      xhr.ontimeout = function() {
        console.error('La solicitud AJAX ha excedido el tiempo de espera.');
      };
      

      xhr.send(formData);
    } else {
      // No se seleccionó ningún archivo, mostrar mensaje en rojo
      noFileSelectedMessage.textContent = 'No se ha seleccionado ningún archivo.';
      noFileSelectedMessage.style.color = 'red';
    }
  });

  // Agregamos un listener al input de archivo para restablecer el color cuando se selecciona un archivo
  document.getElementById('archivo').addEventListener('change', function() {
    noFileSelectedMessage.style.color = '';  // Restablecemos el color a su estado original al seleccionar un archivo
  });
};
