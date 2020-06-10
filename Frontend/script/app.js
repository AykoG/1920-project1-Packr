const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_knop, html_start, html_historiek, html_beheer, html_metingen;

const showTableData = function(data) {
  const table = document.querySelector(".js-table");
  let tableHTML = `<tr class="c-row is-header">
  <th class="c-cell">Metingsid</th>
  <th class="c-cell">Apparaatid</th>
  <th class="c-cell">Tijdstip</th>
  <th class="c-cell">Waarde</th>
  <th class="c-cell">Eenheid</th>
  </tr>`;
  for (const row of data.metingen) {
      tableHTML += 
      `<tr class="c-row">
          <td class="c-cell">${row.metingsid}</td>
          <td class="c-cell">${row.apparaatid}</td>
          <td class="c-cell">${row.tijdstip}</td>
          <td class="c-cell">${row.waarde}</td>
          <td class="c-cell">${row.eenheid}</td>
      </tr>`;
  }
  table.innerHTML = tableHTML;
};

const showChart = function(data) {
  console.log(data);
  let omgezette_xWaarden = [];
  let omgezette_yWaarden = [];
  const apparaatid = data.metingen[0].apparaatid;
  const eenheid = data.metingen[0].eenheid;
  let titel = "";
  if (apparaatid == "TEM") {
    titel = "Temperatuur";
  }
  if (apparaatid == "HUM") {
    titel = "Vochtigheid";
  }
  if (apparaatid == "IR1") {
    titel = "Brieven";
  }
  if (apparaatid == "IR2") {
    titel = "Pakketten";
  }
  for (const meting of data.metingen) {
    omgezette_xWaarden.push(meting.tijdstip);
    omgezette_yWaarden.push(meting.waarde);
  }
  drawChart(omgezette_xWaarden, omgezette_yWaarden, apparaatid, eenheid, titel);
};

const drawChart = function(xWaarden, yWaarden, apparaatid, eenheid, titel) {
    let ctx = document.querySelector(`#chart${apparaatid}`).getContext('2d');
    let config = {
        type: 'line',
        data: {
            labels: xWaarden,
            datasets: [
                {
                    label: titel,
                    backgroundColor: 'white',
                    borderColor: '#71494A',
                    data: yWaarden,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: titel
            },
            tooltips: {
                mode: 'index',
                intersect: true
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [
                    {
                        display: true,
                        scaleLabel: {
                            display : true,
                            labelString: 'Tijdstip'
                        }
                    }
                ],
                yAxes: [
                    {
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: eenheid
                        }
                    }
                ]
            }
        }
    };
    let myChart = new Chart(ctx, config);
}

const showMetingenPerId = function(data) {
  console.log(data);
  const table = document.querySelector(".js-table");
  let tableHTML = `<tr class="c-row is-header">
  <th class="c-cell">ID</th>
  <th class="c-cell">Waarde</th>
  <th class="c-cell">Tijdstip</th>
  </tr>`;
  for (const row of data.metingen) {
      tableHTML += 
      `<tr class="c-row">
          <td class="c-cell">${row.metingsid}</td>
          <td class="c-cell">${row.waarde} ${row.eenheid}</td>
          <td class="c-cell">${row.tijdstip}</td>
      </tr>`;
  }
  table.innerHTML = tableHTML;
  showChart(data);
}

const getCharts = function() {
  handleData(`http://10.15.3.115:5000/api/v1/metingen/TEM`, showChart);
  handleData(`http://10.15.3.115:5000/api/v1/metingen/HUM`, showChart);
  handleData(`http://10.15.3.115:5000/api/v1/metingen/IR/IR1`, showChart);
  handleData(`http://10.15.3.115:5000/api/v1/metingen/IR/IR2`, showChart);
};

const getMetingenPerId = function(apparaatid) {
  handleData(`http://10.15.3.115:5000/api/v1/metingen/${apparaatid}`, showMetingenPerId);
};

const listenToUIStart = function () {
  const knoppen = document.querySelectorAll(".js-action-btn");
  for (const knop of knoppen) {
    knop.addEventListener("click", function () {
      const id = this.dataset.apparaatid;
      const apparaat = document.querySelector(`.js-apparaat[data-apparaatid="${id}"]`);
      const knop = apparaat.querySelector('.js-action-btn');
      if (id == "IR1" || id == "IR2") {
        if (knop.innerHTML == `Legen?`) {
          knop.innerHTML = `Laden...`;
          socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 1 });
        }
        else {
          knop.innerHTML = `Legen?`;
        }
      }
      else {
        knop.innerHTML = `Laden...`;
        socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 0 });
      }
    });
  }
};

const listenToUIBeheer = function () {
  const knoppen = document.querySelectorAll(".js-action-btn");
  for (const knop of knoppen) {
    knop.addEventListener("click", function () {
      const id = this.dataset.apparaatid;
      const actie = this.dataset.action;
      const apparaat = document.querySelector(`.js-apparaat[data-apparaatid="${id}"]`);
      const knop = apparaat.querySelector(`.js-action-btn[data-action="${actie}"]`);
      if (actie == "Status") {
        knop.innerHTML = `Laden...`;
        socket.emit("F2B_read_latest_meting_per_id", id);
      }
      if (actie == "Metingen") {
        window.location.href = `/metingen.html?apparaatid=${id}`;
      }
      if (actie == "Legen") {
        if (knop.innerHTML == `Legen?`) {
          knop.innerHTML = `Legen`;
          socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 1 });
        }
        else {
          knop.innerHTML = `Legen?`;
        }
      }
      if (actie == "Vergrendel") {
        socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 1 });
      }
      if (actie == "Ontgrendel") {
        socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 2 });
      }
      if (actie == "Inlezen") {
        knop.innerHTML = `Laden...`;
        socket.emit("F2B_execute_device", { apparaat_id: id, geforceerde_waarde: 0 });
      }
      if (actie == "IP") {
        knop.innerHTML = `${window.location.hostname}`;
      }
      if (actie == "Herstarten") {
        if (knop.innerHTML == `Zeker?`) {
          socket.emit("F2B_reboot");
          window.location.href = "/reload.html";
        }
        else {
          knop.innerHTML = `Zeker?`;
          
        }
      }
      if (actie == "Uitschakelen") {
        if (knop.innerHTML == `Zeker?`) {
          socket.emit("F2B_shutdown");
          window.location.href = "/reload.html";
        }
        else {
          knop.innerHTML = `Zeker?`;
          
        }
      }
    });
  }
};

const listenToSocketStart = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
  socket.on("B2F_metingen", function (jsonObject) {
    console.log("Dit zijn de metingen");
    console.log(jsonObject);
    //showTableData(jsonObject);
  });
  socket.on("B2F_executed_device", function (jsonObject) {
    console.log(`De actie voor apparaat ${jsonObject.meting.apparaatid} is uitgevoerd`);
    console.log(jsonObject);
    const apparaat = document.querySelector(`.js-apparaat[data-apparaatid="${jsonObject.meting.apparaatid}"]`);
    const knop = apparaat.querySelector('.js-action-btn');
    if (jsonObject.meting.apparaatid == "SER") {
      if (jsonObject.meting.waarde == 0) {
        knop.innerHTML = `Ontgrendeld`;
      }
      else {
        knop.innerHTML = `Vergrendeld`;
      }
    }
    else {
      knop.innerHTML = `${jsonObject.meting.waarde} ${jsonObject.meting.eenheid}`;
    }
  });
};

const listenToSocketBeheer = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
  socket.on("B2F_metingen", function (jsonObject) {
    console.log("Dit zijn de metingen");
    console.log(jsonObject);
  });
  socket.on("B2F_executed_device", function (jsonObject) {
    console.log(`De actie voor apparaat ${jsonObject.meting.apparaatid} is uitgevoerd`);
    console.log(jsonObject);
    const apparaat = document.querySelector(`.js-apparaat[data-apparaatid="${jsonObject.meting.apparaatid}"]`);
    let knop = apparaat.querySelector('.js-action-btn[data-action="Status"]');
    if (jsonObject.meting.apparaatid == "TEM" || jsonObject.meting.apparaatid == "HUM") {
      knop = apparaat.querySelector('.js-action-btn[data-action="Inlezen"]');
    }
    if (jsonObject.meting.apparaatid == "SER") {
      if (jsonObject.meting.waarde == 0) {
        knop.innerHTML = `Ontgrendeld`;
      }
      else {
        knop.innerHTML = `Vergrendeld`;
      }
    }
    else {
      knop.innerHTML = `${jsonObject.meting.waarde} ${jsonObject.meting.eenheid}`;
    }
  });
};

const toggleNav = function() {
  let toggleTrigger = document.querySelectorAll(".js-toggle-nav");
  for (let i = 0; i < toggleTrigger.length; i++) {
      toggleTrigger[i].addEventListener("click", function() {
          console.log("ei");
          document.querySelector("body").classList.toggle("has-mobile-nav");
      })
  }
}

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  html_start = document.querySelector(".js-start");
  html_historiek = document.querySelector(".js-historiek");
  html_beheer = document.querySelector(".js-beheer");
  html_metingen = document.querySelector(".js-metingen");
  if (html_start) {
    console.log("Start");
    html_knop = document.querySelectorAll(".js-action-btn");
    listenToUIStart();
    listenToSocketStart();
    socket.emit("F2B_read_status");
    
  }
  if (html_historiek) {
    console.log("Historiek");
    getCharts();
  }
  if (html_beheer) {
    console.log("Beheer");
    listenToUIBeheer();
    listenToSocketBeheer();
  }
  if (html_metingen) {
    let urlParams = new URLSearchParams(window.location.search);
    let apparaatid = urlParams.get("apparaatid");
    const apparaat = document.querySelector(".js-chart");
    apparaat.innerHTML = `<canvas id="chart${apparaatid}" width="300" height="90"></canvas>`;
    if (apparaatid) {
      getMetingenPerId(apparaatid);
    }
    else {
      window.location.href = "/beheer.html";
    }
  }
  toggleNav();
});