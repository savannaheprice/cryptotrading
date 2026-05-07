from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI(title="Bitcoin 30-Day Chart")


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bitcoin Price Dashboard</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Inter, system-ui, Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #111827);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 30px;
        }

        .card {
            width: 100%;
            max-width: 1100px;
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }

        h1 {
            margin: 0;
            font-size: 2.2rem;
            font-weight: 800;
        }

        .subtitle {
            margin-top: 10px;
            color: #cbd5e1;
            font-size: 1rem;
        }

        .stats {
            display: flex;
            gap: 20px;
            margin-top: 25px;
            flex-wrap: wrap;
        }

        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 18px;
            border-radius: 18px;
            min-width: 180px;
            flex: 1;
        }

        .stat-label {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .stat-value {
            margin-top: 8px;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .chart-container {
            margin-top: 35px;
            background: rgba(255,255,255,0.04);
            border-radius: 20px;
            padding: 20px;
        }

        canvas {
            width: 100% !important;
            height: 500px !important;
        }

        .footer {
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.85rem;
            text-align: center;
        }

        @media (max-width: 700px) {
            h1 {
                font-size: 1.7rem;
            }

            canvas {
                height: 320px !important;
            }
        }
    </style>
</head>
<body>

<div class="card">
    <h1>Bitcoin Price Dashboard</h1>
    <div class="subtitle">
        BTC/USD price history for the last 30 days
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="stat-label">Current Price</div>
            <div class="stat-value" id="currentPrice">Loading...</div>
        </div>

        <div class="stat-box">
            <div class="stat-label">30-Day High</div>
            <div class="stat-value" id="highPrice">Loading...</div>
        </div>

        <div class="stat-box">
            <div class="stat-label">30-Day Low</div>
            <div class="stat-value" id="lowPrice">Loading...</div>
        </div>
    </div>

    <div class="chart-container">
        <canvas id="btcChart"></canvas>
    </div>

    <div class="footer">
        Data source: CoinGecko API
    </div>
</div>

<script>
async function loadData() {
    const response = await fetch('/api/bitcoin');
    const data = await response.json();

    const labels = data.prices.map(p => {
        const d = new Date(p[0]);
        return d.toLocaleDateString();
    });

    const prices = data.prices.map(p => p[1]);

    const current = prices[prices.length - 1];
    const high = Math.max(...prices);
    const low = Math.min(...prices);

    document.getElementById('currentPrice').textContent =
        '$' + current.toLocaleString(undefined, {maximumFractionDigits: 0});

    document.getElementById('highPrice').textContent =
        '$' + high.toLocaleString(undefined, {maximumFractionDigits: 0});

    document.getElementById('lowPrice').textContent =
        '$' + low.toLocaleString(undefined, {maximumFractionDigits: 0});

    const ctx = document.getElementById('btcChart').getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 500);
    gradient.addColorStop(0, 'rgba(59,130,246,0.55)');
    gradient.addColorStop(1, 'rgba(59,130,246,0.02)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'BTC Price (USD)',
                data: prices,
                borderColor: '#60a5fa',
                backgroundColor: gradient,
                fill: true,
                tension: 0.35,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            },

            scales: {
                x: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    }
                },

                y: {
                    ticks: {
                        color: '#cbd5e1',
                        callback: value => '$' + value.toLocaleString()
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    }
                }
            }
        }
    });
}

loadData();
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.get("/api/bitcoin")
async def bitcoin_data():
    url = (
        "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        "?vs_currency=usd&days=30"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    return {
        "prices": data["prices"]
    }