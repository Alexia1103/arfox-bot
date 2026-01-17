// Guardamos el teléfono actual
let telefonoActual = "";

// Paso 1: Iniciar soporte
function iniciarSoporte() {
    const telefono = document.getElementById("telefono").value;
    if (!telefono) {
        alert("Por favor escribe tu número primero");
        return;
    }

    telefonoActual = telefono;

    fetch("/buscar_usuario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telefono: telefono })
    })
    .then(res => res.json())
    .then(data => {
        const contenedor = document.getElementById("contenedor-dinamico");

        if (data.status === "error") {
            contenedor.innerHTML = `
                <h3 style="color:#ff6b6b">❌ ${data.mensaje}</h3>
                <button class="btn-primary" onclick="volverInicio()">Volver</button>
            `;
            return;
        }

        // Guardamos los datos del usuario
        window.usuarioActual = data;

        // Mostramos las plataformas disponibles
        let botonesPlataformas = "";
        data.plataformas.forEach(plataforma => {
            botonesPlataformas += `<button class="btn-primary" onclick="seleccionarPlataforma('${plataforma}')">${plataforma}</button>`;
        });

        contenedor.innerHTML = `
            <h3>Hola ${data.nombre} 👋</h3>
            <p>¿En qué plataforma deseas soporte?</p>
            ${botonesPlataformas}
            <div id="correo-netflix" class="correo-cuadro" style="display:none;"></div>
        `;
    })
    .catch(err => {
        console.error(err);
        alert("Error al buscar el usuario");
    });
}

// Paso 2: Seleccionar plataforma
function seleccionarPlataforma(plataforma) {
    const contenedor = document.getElementById("contenedor-dinamico");

    // Solo Netflix tiene flujo de código temporal
    if (plataforma === "Netflix") {
        contenedor.innerHTML = `
            <h3>Deseas obtener el código temporal de Netflix?</h3>
            <button class="btn-primary" onclick="mostrarCodigoNetflix()">Sí, mostrar código</button>
            <button class="btn-primary" onclick="volverInicio()">No, volver</button>
            <div id="correo-netflix" class="correo-cuadro" style="display:none;"></div>
        `;
    } else {
        // Para otras plataformas
        contenedor.innerHTML = `
            <h3>Soporte para ${plataforma}</h3>
            <p>Opciones de soporte próximamente.</p>
            <button class="btn-primary" onclick="volverInicio()">Volver</button>
        `;
    }
}

// Paso 3: Mostrar código y correo Netflix
function mostrarCodigoNetflix() {
    fetch("/buscar_usuario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telefono: telefonoActual })
    })
    .then(res => res.json())
    .then(data => {
        const divCorreo = document.getElementById("correo-netflix");

        if (data.status === "error") {
            divCorreo.style.display = "block";
            divCorreo.innerHTML = `<p style="color:red;">${data.mensaje}</p>`;
            return;
        }

        // Formateamos el correo para que se vea bien
        let correoFormateado = (data.correo_netflix || "No hay correos recientes")
            .replace(/\r\n/g, "\n")      // saltos de línea
            .replace(/\xa0/g, " ");      // espacios extraños

        // Opcional: reemplazar links por [enlace] si quieres simplificar
        correoFormateado = correoFormateado.replace(/https?:\/\/\S+/g, "[enlace]");

        divCorreo.style.display = "block";
        divCorreo.innerHTML = `
            <h4>Código temporal:</h4>
            <p><strong>${data.codigo_netflix || "No encontrado"}</strong></p>
            <hr>
            <pre>${correoFormateado}</pre>
            <button class="btn-primary" onclick="volverInicio()">Volver</button>
        `;
    })
    .catch(err => console.error(err));
}

// Volver al inicio
function volverInicio() {
    document.getElementById("contenedor-dinamico").innerHTML = `
        <h3>¿En qué te puedo ayudar?</h3>
        <input type="text" id="telefono" class="input-text" placeholder="Escribe tu número de WhatsApp">
        <button class="btn-primary" onclick="iniciarSoporte()">Necesito soporte</button>
        <button class="btn-primary">Deseo renovar mi servicio</button>
        <button class="btn-primary">Deseo adquirir un servicio</button>
    `;
}
function seleccionarPlataforma(plataforma) {
    const telefono = document.getElementById("telefono").value;
    if(plataforma === "Netflix") {
        window.open(`/soporte_netflix/${telefono}`, '_blank'); // abre en nueva pestaña
    }
}