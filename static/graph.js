let timeArray
let tempArray

async function fetchText () {
  // Fetch data from data.txt
  let response = await fetch('static/data.txt')
  let data = await response.text()
  let dataArray = data.split('\n')
  timeArray = dataArray[0].substring(1, dataArray[0].length - 2).replace(/["']/g, "").split(', ')
  tempArray = dataArray[1].substring(1, dataArray[1].length - 2).split(', ').map(Number)
  maxTemp = Math.max(...tempArray)
  minTemp = Math.min(...tempArray)
  console.log(timeArray, tempArray)
  console.log(maxTemp, minTemp)

  // Draw chart
  const ctx = document.getElementById('myChart').getContext('2d');
  const myChart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: timeArray,
          datasets: [{
              label: 'Temperature',
              data: tempArray,
              backgroundColor: [
                  'rgba(255, 99, 132, 0.2)',
                  'rgba(54, 162, 235, 0.2)',
                  'rgba(255, 206, 86, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                  'rgba(153, 102, 255, 0.2)',
                  'rgba(255, 159, 64, 0.2)'
              ],
              borderColor: [
                  'rgba(255, 99, 132, 1)',
                  'rgba(54, 162, 235, 1)',
                  'rgba(255, 206, 86, 1)',
                  'rgba(75, 192, 192, 1)',
                  'rgba(153, 102, 255, 1)',
                  'rgba(255, 159, 64, 1)'
              ],
              borderWidth: 1
          }]
      },
      options: {
          scales: {
              yAxes: [{
                  ticks: {
                      beginAtZero: false,
                      suggestedMin: minTemp,
                      suggestedMax: maxTemp,
                  }
              }]
          }
      }
  });
}

fetchText()
