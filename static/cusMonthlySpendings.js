function drawBarChart2() {
  const arrayLength = monthly_spendings.length;
  let content = [["Spendings", "Amount of Spendings", { role: 'style' } ]];
  for (var i = 0; i < arrayLength; i++) {
    content.push([months[i], monthly_spendings[i], 'color: #57068c' ]);
  }

  var data = new google.visualization.arrayToDataTable(content);

  var options = {
    legend: { position: "none" },
    chart: {
      title: "Monthly Spendings",
    },
    axes: {
      x: {
        0: { side: "bottom", label: "Monthly Spendings" },
      },
    },
    bar: { groupWidth: "50%" },
  };

  var chart = new google.charts.Bar(
    document.getElementById("cusMonthlySpending")
  );
  chart.draw(data, google.charts.Bar.convertOptions(options));
}
