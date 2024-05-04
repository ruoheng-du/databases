google.charts.load("current", { packages: ["bar"] });
google.charts.setOnLoadCallback(drawBarChart2);

const person6 = ppl2[0];
const person7 = ppl2[1];
const person8 = ppl2[2];
const person9 = ppl2[3];
const person10 = ppl2[4];
const num6 = commissions[0];
const num7 = commissions[1];
const num8 = commissions[2];
const num9 = commissions[3];
const num10 = commissions[4];

function drawBarChart2() {
  var data = new google.visualization.arrayToDataTable([
    ["Commissions", "Amount of Commissions"],
    [person6, num6],
    [person7, num7],
    [person8, num8],
    [person9, num9],
    [person10, num10],
  ]);

  var options = {
    // width: 800,
    legend: { position: "none" },
    chart: {
      title: "Top 5 Customers",
    },
    axes: {
      x: {
        0: { side: "bottom", label: "The Amount of Commission Received in the Past Year" },
      },
    },
    bar: { groupWidth: "50%" },
    colors: ["#57068c", "#57068c", "#57068c", "#57068c", "#57068c"],
  };

  var chart = new google.charts.Bar(document.getElementById("right"));
  // Convert the Classic options to Material options.
  chart.draw(data, google.charts.Bar.convertOptions(options));
}
