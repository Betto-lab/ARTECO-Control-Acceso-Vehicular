const apiInput = document.querySelector("#api-url");
const result = document.querySelector("#result");
const history = document.querySelector("#history");
const historyRows = document.querySelector("#history-rows");
const historySummary = document.querySelector("#history-summary");
const queryApi = new URLSearchParams(location.search).get("api");
const deployedApi = window.ARTECO_CONFIG?.api_url || "";
apiInput.value = queryApi || localStorage.getItem("artecoApiUrl") || deployedApi;

function endpoint() {
  const base = apiInput.value.trim().replace(/\/$/, "");
  if (!base) throw new Error("Ingrese la URL del API DEV");
  return base.endsWith("/demo/vehicle-access") ? base : base + "/demo/vehicle-access";
}

async function callApi(method, payload, query = "") {
  result.textContent = "Procesando...";
  const response = await fetch(endpoint() + query, {
    method,
    headers: {"Content-Type": "application/json"},
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const body = await response.json();
  result.textContent = JSON.stringify(body, null, 2);
  if (!response.ok) throw new Error(body.error || "Error del API");
  return body;
}

document.querySelector("#save-api").addEventListener("click", () => {
  localStorage.setItem("artecoApiUrl", apiInput.value.trim());
  result.textContent = "API DEV guardada.";
});

document.querySelector("#vehicle-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const ownerName = document.querySelector("#owner-name").value.trim();
    if (!ownerName || [...ownerName].length > 120) {
      result.textContent = "El propietario debe contener entre 1 y 120 caracteres.";
      return;
    }
    await callApi("POST", {
      action: "register_vehicle",
      plate: document.querySelector("#vehicle-plate").value,
      owner_name: ownerName,
    });
  } catch (error) {
    result.textContent += "\n" + error.message;
  }
});

document.querySelector("#access-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await callApi("POST", {
      plate: document.querySelector("#plate").value,
      event_type: document.querySelector("#event-type").value,
      gate_id: document.querySelector("#gate-id").value,
    });
  } catch (error) {
    result.textContent += "\n" + error.message;
  }
});

document.querySelector("#refresh-events").addEventListener("click", async () => {
  try {
    const plate = document.querySelector("#history-plate").value.trim();
    const query = plate ? "?" + new URLSearchParams({plate}).toString() : "";
    const body = await callApi("GET", undefined, query);
    historyRows.replaceChildren();
    const events = Array.isArray(body.events) ? body.events : [];
    historySummary.textContent = events.length ? `${events.length} accesos encontrados` : "No se encontraron accesos.";
    for (const access of events) {
      const row = document.createElement("tr");
      const values = [access.occurred_at, access.plate, access.event_type === "ENTRY" ? "Ingreso" : "Salida", access.gate_id, access.authorized ? "Autorizado" : "Denegado"];
      for (const value of values) {
        const cell = document.createElement("td");
        cell.textContent = value ?? "";
        row.append(cell);
      }
      historyRows.append(row);
    }
    history.hidden = false;
    result.textContent = "";
  } catch (error) {
    history.hidden = true;
    result.textContent += "\n" + error.message;
  }
});
