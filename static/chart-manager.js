google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(readyToChart);

var chart;
window.charlib_loaded = false;
window.chartrefs = {};
window.charts = {};
window.timeouts = {};

function create_new(bridge_name, title="NN", start_from=0) {

    $box = `<div class="box" style="margin-top: 35px;">
      <h3>${title}</h3>
      <p style="margin-bottom: 25px;">
        Sources – Many
      </p>
      <div style="width: 100%; float: left">
        <div id="${bridge_name}"></div>
        <input type="range" style="height: auto; width: 100%;" min="1" max="100" value="50" class="slider" id="${bridge_name}-slider">
      </div>
      <div style="clear: both;"></div>
    </div>`;
    $(".container").prepend($box);
    create(bridge_name, bridge_name, start_from=start_from);

}

function create(container_id, bridge_name, start_from=false) {
  $.get(`/bridges/${bridge_name}`, (response) => {
    if (response["type"] == "line-chart") {
      create_linechart(container_id, bridge_name, start_from);
    }
  })
}

function create_linechart(container_id, bridge_name, start_from=false) {
  $.get(`/bridges/${bridge_name}`, (response) => {
    linechart(container_id, response, false)
    const resp = response;
    const selector = container_id;

    if (start_from === false) start_from = 0;

    window.chartrefs[selector] = false;

    // redraw each x if there's a slider change
    setInterval(() => {
      var sliderValue = parseInt( $(`#${selector}-slider`).val() );
      // console.log(`#${selector}`)
      if (window.chartrefs[selector] !== sliderValue) {
        linechart(container_id, resp, [start_from, sliderValue])
        window.chartrefs[selector] = sliderValue;
      }
    }, 200);

    // resizing handler for this obj
    $(window).resize(() => {
      var sliderValue = parseInt( $(`#${selector}-slider`).val() );
      try { clearTimeout(window.timeouts[selector]) } catch {}
      window.timeouts[selector] = setTimeout(() => {
        linechart(container_id, resp, [start_from, sliderValue])
      }, 200);
    })
  });
}

function linechart(id, bridge_data, range=false) {

  if (id in window.charts) {
    var chart = window.charts[id]
  } else {
    window.charts[id] = new google.charts.Line($(`#${id}`)[0]);
    var chart = window.charts[id];
  }

  // var chart =
  var data = new google.visualization.DataTable();

  // deriving cols from dataset
  for (let header of bridge_data["headers"]) {
    data.addColumn(header[0], header[1]);
  }

  // get original length of dataset
  const data_length = bridge_data["pure"].length - 1;
  console.log(`max data: ${data_length}, id = ${id}`);
  if (range == false) {
    $(`#${id}-slider`).attr("min", 0).attr("max", data_length).attr("value", data_length)
  }
  else {
    $(`#${id}-slider`).attr("min", range[0]).attr("max", data_length).attr("value", data_length)
  }

  // deriving rows from dataset
  const rows = [];
  if (range === false) {
    for (let i = 0; i < bridge_data["pure"].length; i++) {
      let row = [...bridge_data["pure"][i]]
      // let index = row[0];
      // row[0] = new Date(index[0], index[1], index[2])
      // console.log(row)
      row[0] = row[0].split("/")[0]
      rows.push(row)
    }
  } else {
    const [leftrange, rightrange] = range;
    for (let i = 0; i < bridge_data["pure"].length; i++) {
      if (i >= leftrange && i <= rightrange) {
        let row   = [...bridge_data["pure"][i]];
        // let index = row[0]
        // row[0] = new Date(index[0], index[1], index[2])
        // row[0] = row[0].split("/")[0]
        rows.push(row)
      }
    }
  }

  data.addRows(rows);

  // using material opts
  const materialOptions = bridge_data["options"]
  chart.draw(data, materialOptions);
}
