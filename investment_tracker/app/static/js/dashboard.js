let myChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const assetLinks = document.querySelectorAll(".asset-link");
    
    assetLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            // USE currentTarget to ensure we get the tile, not the text inside it
            const assetId = e.currentTarget.dataset.assetId;
            const assetSymbol = e.currentTarget.dataset.assetSymbol;
            const assetName = e.currentTarget.dataset.assetName;
            
            console.log(`Fetching data for: ${assetSymbol} (ID: ${assetId})`);
            fetchAndDrawChart(assetId, assetSymbol, assetName);
        });
    });
});

async function fetchAndDrawChart(assetId, assetSymbol, assetName) {
    // Update UI to show we are working
    const titleElem = document.getElementById("chart-title");
    if (titleElem) titleElem.innerText = `Loading ${assetSymbol}...`;

    try {
        const response = await fetch(`/investments/api/price-history/${assetId}`);

        if (!response.ok) {
            console.error(`API Error: ${response.status}`);
            return;
        }

        const priceHistory = await response.json();

        if (priceHistory.length === 0) {
            if (titleElem) titleElem.innerText = "No price history found";
            alert(`No price history found for ${assetSymbol}. Add some in the Manage page!`);
            return;
        }

        const labels = priceHistory.map(item => item.date);
        const prices = priceHistory.map(item => item.price);

        renderChart(labels, prices, assetSymbol, assetName);
    
    } catch (error) {
        console.error("Fetch error:", error);
    }
}

function renderChart(labels, data, symbol, name) {
    const chartCanvas = document.getElementById("priceChart");
    if (!chartCanvas) return;
    const ctx = chartCanvas.getContext("2d");

    // Helper: Compare current point to previous point for segment color
    const segmentDown = (ctx, value) => ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;

    // 1. If chart exists, just update data to keep animations smooth
    if (myChart) {
        myChart.data.labels = labels;
        myChart.data.datasets[0].data = data;
        
        // Update titles
        document.getElementById("chart-title").innerText = `${symbol} (${name})`;
        
        myChart.update(); // This will animate the transition
        return; 
    }

    // 2. Initial Chart Creation (only runs once)
    document.getElementById("chart-title").innerText = `${symbol} (${name})`;
    document.getElementById("chart-label").innerText = `Market Analysis / Multi-Trend`;

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Price',
                data: data,
                borderWidth: 3, 
                fill: false,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 6,
                borderColor: '#4ade80', // Default color
                segment: {
                    // Red if going down, Green if going up
                    borderColor: ctx => segmentDown(ctx, '#f87171') || '#4ade80',
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeInOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                // Built-in plugins go here
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#161616',
                    titleFont: { family: 'JetBrains Mono' },
                    bodyFont: { family: 'JetBrains Mono' },
                    displayColors: false,
                    borderColor: '#333',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#444', font: { size: 10, family: 'JetBrains Mono' } }
                },
                y: {
                    position: 'right',
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { 
                        color: '#888', 
                        font: { family: 'JetBrains Mono', size: 10 }
                    }
                }
            }
        },
        plugins: [{
            // Custom plugins (the Glow effect) go here as a sibling to 'options'
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                const _stroke = ctx.stroke;
                ctx.stroke = function() {
                    ctx.save();
                    ctx.shadowColor = ctx.strokeStyle; // Neon glow matches line color
                    ctx.shadowBlur = 10;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 4;
                    _stroke.apply(this, arguments);
                    ctx.restore();
                };
            }
        }]
});
}