let myChart = null;

// Wait for page to load
document.addEventListener('DOMContentLoaded', () => {

    const assetLinks = document.querySelectorAll(".asset-link");
    assetLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            // Get the data from HTML
            assetId = e.target.dataset.assetId;
            assetSymbol = e.target.dataset.assetSymbol;

            fetchAndDrawChart(assetId, assetSymbol);
        });
    });
});

async function fetchAndDrawChart(assetId, assetSymbol) {
    response = await fetch(`/api/price-history/${assetId}`);

    if(response.ok == true) {
        priceHistory = await response.json()

        const labels = priceHistory.map(item => item.date);
        const prices = priceHistory.map(item => item.price);

        renderChart(labels, prices)
    }
}

function renderChart(labels, data) {
    // Destroy old chart if it exists
    if (myChart) {
        myChart.destroy();
    }

    const chartCanvas = document.getElementById("priceChart")
    const ctx = chartCanvas.getContext("2d")

    myChart = new Chart(ctx, 
        {
            type: 'line', // This tells it to draw a line chart
            data: {
                labels: labels, // This is your X-axis (dates)
                datasets: [
                    {
                        label: 'Price',
                        data: data, // This is your Y-axis (prices)
                        borderColor: '#007bff'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: "Asset Price History"
                    },
                    legend: {
                        display: true,
                        position: "top"
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Date"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Price (in local currency)"
                        }
                    }
                }
            }
        });
}