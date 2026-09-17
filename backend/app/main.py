from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app import auth

app = FastAPI(title="ParkWise Management System")

# Include Auth & Search Router
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ParkWise | Parking Lot Management System</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --border: #e2e8f0;
                --success: #15803d;
                --success-bg: #dcfce7;
                --warning: #b45309;
                --warning-bg: #fef3c7;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text-main); padding: 40px 20px; line-height: 1.5; }
            .wrapper { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }

            /* Header & Landing Banner */
            .banner { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; border-radius: 12px; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            .banner h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
            .banner p.subtitle { color: #94a3b8; font-size: 1rem; margin-bottom: 24px; }
            .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
            .info-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 16px; }
            .info-card h4 { color: #38bdf8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
            .info-card p { font-size: 0.9rem; color: #cbd5e1; }

            /* Grid Layout for Forms */
            .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px; }

            /* Cards & Headers */
            .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .card-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 16px; color: var(--text-main); }

            /* Forms & Inputs */
            .form-group { display: flex; flex-direction: column; gap: 12px; }
            .form-inline { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
            input, select { padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
            input:focus, select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
            
            .btn { background: var(--primary); color: white; padding: 10px 20px; border: none; border-radius: 8px; font-weight: 500; font-size: 0.9rem; cursor: pointer; transition: background 0.2s; }
            .btn:hover { background: var(--primary-dark); }
            .btn-outline { background: transparent; color: var(--text-main); border: 1px solid var(--border); }
            .btn-outline:hover { background: #f1f5f9; }

            /* Table Styling */
            .table-container { overflow-x: auto; margin-top: 16px; }
            table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }
            th { background-color: #f8fafc; color: var(--text-muted); font-weight: 600; padding: 12px 16px; border-bottom: 1px solid var(--border); }
            td { padding: 16px; border-bottom: 1px solid var(--border); }
            tr:hover td { background-color: #f8fafc; }

            /* Status Badges */
            .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
            .badge-active { background: var(--success-bg); color: var(--success); }
            .badge-checkout { background: var(--warning-bg); color: var(--warning); }

            .pagination-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
            .status-msg { margin-top: 12px; font-size: 0.875rem; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <!-- LANDING PAGE BANNER -->
            <header class="banner">
                <h1>ParkWise Manager</h1>
                <p class="subtitle">Next-Generation Parking Lot Operations & Valet Control System</p>
                <div class="grid-3">
                    <div class="info-card">
                        <h4>What It Is</h4>
                        <p>Full-stack parking platform with dynamic rate parsing, automated check-in/out, and valet plate transfers.</p>
                    </div>
                    <div class="info-card">
                        <h4>Target Audience</h4>
                        <p>Commercial garage operators, event venues, residential complexes, and valet services.</p>
                    </div>
                    <div class="info-card">
                        <h4>How It Helps</h4>
                        <p>Replaces manual logbooks with automated spot allocation, duration-based pricing, and live analytics.</p>
                    </div>
                </div>
            </header>

            <!-- AUTH & OPERATIONS ROW -->
            <div class="grid-2">
                <!-- CHECK-IN / SPOT ALLOCATION CARD -->
                <section class="card">
                    <h2 class="card-title">🚗 Vehicle Check-In (Allocate Spot)</h2>
                    <div class="form-group">
                        <input id="checkinPlate" placeholder="Vehicle License Plate (e.g. ABC-1234)">
                        <input id="checkinSpot" type="number" placeholder="Spot ID (e.g. 101)">
                        <button class="btn" onclick="executeCheckIn()">Allocate Spot & Check In</button>
                    </div>
                    <div id="checkinStatus" class="status-msg"></div>
                </section>

                <!-- CHECK-OUT / FEE CALCULATION CARD -->
                <section class="card">
                    <h2 class="card-title">💳 Vehicle Check-Out</h2>
                    <div class="form-group">
                        <input id="checkoutPlate" placeholder="Vehicle License Plate to Check-Out">
                        <button class="btn btn-outline" onclick="executeCheckOut()">Process Check-Out & Calculate Fee</button>
                    </div>
                    <div id="checkoutStatus" class="status-msg"></div>
                </section>
            </div>

            <!-- OPERATOR AUTHENTICATION CARD -->
            <section class="card">
                <h2 class="card-title">Operator Access</h2>
                <div class="form-inline">
                    <input id="username" placeholder="Enter username..." style="flex: 1; min-width: 180px;">
                    <input id="password" type="password" placeholder="Enter password..." style="flex: 1; min-width: 180px;">
                    <button class="btn" onclick="executeAuth('/auth/login')">Sign In</button>
                    <button class="btn btn-outline" onclick="executeAuth('/auth/register')">Register Account</button>
                </div>
                <div id="authStatus" class="status-msg"></div>
            </section>

            <!-- LIVE DASHBOARD TABLE -->
            <section class="card">
                <h2 class="card-title">Live Parking Dashboard</h2>
                <div class="form-inline" style="justify-content: space-between; margin-bottom: 16px;">
                    <input id="searchInput" placeholder="🔍 Search license plate..." style="flex: 1; min-width: 220px;" oninput="fetchParkingData()">
                    <div style="display: flex; gap: 8px;">
                        <select id="sortSelect" onchange="fetchParkingData()">
                            <option value="id">Sort by Spot ID</option>
                            <option value="license_plate">Sort by License Plate</option>
                        </select>
                        <select id="orderSelect" onchange="fetchParkingData()">
                            <option value="asc">Ascending</option>
                            <option value="desc">Descending</option>
                        </select>
                    </div>
                </div>

                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Record ID</th>
                                <th>License Plate</th>
                                <th>Spot Allocation</th>
                                <th>Session Status</th>
                                <th>Fee Charged</th>
                            </tr>
                        </thead>
                        <tbody id="parkingRows"></tbody>
                    </table>
                </div>

                <div class="pagination-bar">
                    <button id="prevBtn" class="btn btn-outline" onclick="navigatePage(-1)">Previous</button>
                    <span id="pageTracker" style="font-size: 0.875rem; color: var(--text-muted);">Page 1</span>
                    <button id="nextBtn" class="btn btn-outline" onclick="navigatePage(1)">Next</button>
                </div>
            </section>
        </div>

        <script>
            let currentPage = 1;

            async function executeCheckIn() {
                const plate = document.getElementById('checkinPlate').value;
                const spot = document.getElementById('checkinSpot').value;
                const statusEl = document.getElementById('checkinStatus');

                if (!plate || !spot) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Please enter both license plate and spot ID.';
                    return;
                }

                try {
                    const res = await fetch('/parkings/checkin', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ license_plate: plate, spot_id: parseInt(spot) })
                    });
                    const data = await res.json();

                    if (res.ok) {
                        statusEl.style.color = 'var(--success)';
                        statusEl.innerText = `Checked in ${plate} to Spot #${spot} successfully!`;
                        document.getElementById('checkinPlate').value = '';
                        document.getElementById('checkinSpot').value = '';
                        fetchParkingData();
                    } else {
                        statusEl.style.color = 'var(--warning)';
                        statusEl.innerText = data.detail || 'Check-in failed.';
                    }
                } catch (err) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Error connecting to check-in endpoint.';
                }
            }

            async function executeCheckOut() {
                const plate = document.getElementById('checkoutPlate').value;
                const statusEl = document.getElementById('checkoutStatus');

                if (!plate) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Please enter a license plate to checkout.';
                    return;
                }

                try {
                    const res = await fetch('/parkings/checkout', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ license_plate: plate })
                    });
                    const data = await res.json();

                    if (res.ok) {
                        statusEl.style.color = 'var(--success)';
                        statusEl.innerText = `Checkout complete for ${plate}. Fee: $${Number(data.fee_charged || 0).toFixed(2)}`;
                        document.getElementById('checkoutPlate').value = '';
                        fetchParkingData();
                    } else {
                        statusEl.style.color = 'var(--warning)';
                        statusEl.innerText = data.detail || 'Checkout failed.';
                    }
                } catch (err) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Error connecting to checkout endpoint.';
                }
            }

            async function executeAuth(endpoint) {
                const u = document.getElementById('username').value;
                const p = document.getElementById('password').value;
                const statusEl = document.getElementById('authStatus');

                if (!u || !p) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Please enter both a username and password.';
                    return;
                }

                try {
                    const res = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: u, password: p })
                    });
                    const data = await res.json();

                    if (res.ok) {
                        statusEl.style.color = 'var(--success)';
                        statusEl.innerText = data.message || 'Authenticated successfully!';
                    } else {
                        statusEl.style.color = 'var(--warning)';
                        statusEl.innerText = data.detail || 'Authentication failed.';
                    }
                } catch (err) {
                    statusEl.style.color = 'var(--warning)';
                    statusEl.innerText = 'Unable to connect to server.';
                }
            }

            async function fetchParkingData() {
                const query = document.getElementById('searchInput').value;
                const sortBy = document.getElementById('sortSelect').value;
                const order = document.getElementById('orderSelect').value;

                try {
                    const res = await fetch(`/parkings/search?query=${query}&sort_by=${sortBy}&order=${order}&page=${currentPage}&limit=5`);
                    const data = await res.json();

                    const tbody = document.getElementById('parkingRows');
                    tbody.innerHTML = '';

                    if (!data.results || data.results.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">No active parking sessions found</td></tr>`;
                    } else {
                        data.results.forEach(item => {
                            const badge = item.is_active 
                                ? `<span class="badge badge-active">Active Session</span>`
                                : `<span class="badge badge-checkout">Checked Out</span>`;
                            tbody.innerHTML += `
                                <tr>
                                    <td>#${item.id}</td>
                                    <td><strong>${item.license_plate}</strong></td>
                                    <td>Spot #${item.spot_id}</td>
                                    <td>${badge}</td>
                                    <td>$${Number(item.fee_charged).toFixed(2)}</td>
                                </tr>
                            `;
                        });
                    }

                    const totalPages = Math.ceil((data.total || 0) / 5) || 1;
                    document.getElementById('pageTracker').innerText = `Page ${data.page || 1} of ${totalPages}`;
                    document.getElementById('prevBtn').disabled = currentPage <= 1;
                    document.getElementById('nextBtn').disabled = currentPage >= totalPages;
                } catch (err) {
                    console.error("Error loading table data:", err);
                }
            }

            function navigatePage(direction) {
                currentPage = Math.max(1, currentPage + direction);
                fetchParkingData();
            }

            fetchParkingData();
        </script>
    </body>
    </html>
    """