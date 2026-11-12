document.querySelector("#access-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const plate = document.querySelector("#plate").value.toUpperCase().replace(/[^A-Z0-9]/g, "");
  const payload = {plate, event_type: document.querySelector("#event-type").value, gate_id: document.querySelector("#gate-id").value};
  const valid = /^[A-Z0-9]{5,8}$/.test(plate);
  document.querySelector("#result").textContent = JSON.stringify({valid, payload, note: "Validación local; integración API pendiente de despliegue."}, null, 2);
});
