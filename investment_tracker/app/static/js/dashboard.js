let myChart = null;

document.addEventListener('DOMContentLoaded', () => {

    const assetLinks = document.querySelectorAll(".asset-link");
    
    // Debugging: Check if we actually found any links
    if (assetLinks.length === 0) {
        console.warn("No .asset-link elements found. Check your HTML!");
    }

    assetLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            // Use 'dataset' to read the data-attributes from HTML
            const assetId = e.target.dataset.assetId;
            const assetSymbol = e.target.dataset.assetSymbol;
            
            console.log(`Fetching chart for: ${assetSymbol} (ID: ${assetId})`);
            fetchAndDrawChart(assetId, assetSymbol);
        });
    });
});

async function fetchAndDrawChart(assetId, assetSymbol) {
    try {
        // FIX: Added the '/investments' prefix to match run.py
        const response = await fetch(`/investments/api/price-history/${assetId}`);

        if (!response.ok) {
            console.error(`API Error: ${response.status}`);
            return;
        }

        const priceHistory = await response.json();
        
        // Debugging: See what data came back
        console.log("Data received:", priceHistory);

        if (priceHistory.length === 0) {
            alert("No price history found for this asset.");
            return;
        }

        const labels = priceHistory.map(item => item.date);
        const prices = priceHistory.map(item => item.price);

        renderChart(labels, prices, assetSymbol);
    
    } catch (error) {
        console.error("Fetch error:", error);
    }
}

function renderChart(labels, data, symbol) {
    if (myChart) {
        myChart.destroy();
    }

    const chartCanvas = document.getElementById("priceChart");
    
    // Safety check: Does the canvas exist on the page?
    if (!chartCanvas) {
        console.error("Canvas element 'priceChart' not found in HTML.");
        return;
    }

    const ctx = chartCanvas.getContext("2d");

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${symbol} Price`, // Use the symbol in the label
                data: data,
                borderColor: '#007bff',
                tension: 0.1, // Makes the line slightly smoother
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: `${symbol} Performance` },
                legend: { display: true, position: "top" }
            },
            scales: {
                x: { title: { display: true, text: "Date" } },
                y: { title: { display: true, text: "Price" } }
            }
        }
    });
}