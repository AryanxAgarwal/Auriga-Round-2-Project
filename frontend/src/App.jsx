import React, { useState, useEffect } from 'react';

export default function App() {
  const [user, setUser] = useState(null);
  const [authForm, setAuthForm] = useState({ username: '', password: '', isRegister: false });
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('id');
  const [order, setOrder] = useState('asc');
  const [data, setData] = useState({ total: 0, results: [] });

  const handleAuth = async (e) => {
    e.preventDefault();
    const endpoint = authForm.isRegister ? '/auth/register' : '/auth/login';
    const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: authForm.username, password: authForm.password })
    });
    const result = await res.json();
    if (res.ok) {
      if (!authForm.isRegister) setUser(result.username);
      alert(authForm.isRegister ? 'Registered! Please login.' : 'Logged in!');
    } else alert(result.detail);
  };

  const fetchData = async () => {
    const res = await fetch(
      `http://127.0.0.1:8000/parkings/search?query=${search}&page=${page}&limit=5&sort_by=${sortBy}&order=${order}`
    );
    const json = await res.json();
    setData(json);
  };

  useEffect(() => { fetchData(); }, [search, page, sortBy, order]);

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px', maxWidth: '900px', margin: 'auto' }}>
      {/* LANDING PAGE SECTION */}
      <header style={{ borderBottom: '2px solid #ccc', pb: '10px' }}>
        <h1>ParkWise - Smart Parking Lot Manager</h1>
        <p><strong>Target Audience:</strong> Commercial Garage Operators & Valet Systems.</p>
        <p><strong>How It Helps:</strong> Streamlines vehicle check-in/checkout, dynamic rate adjustments, and automated valet session transfers.</p>
      </header>

      {/* AUTH SECTION */}
      <section style={{ margin: '20px 0', background: '#f4f4f4', padding: '15px' }}>
        {user ? (
          <div>Logged in as: <strong>{user}</strong> | <button onClick={() => setUser(null)}>Logout</button></div>
        ) : (
          <form onSubmit={handleAuth}>
            <h3>{authForm.isRegister ? 'Register' : 'Login'}</h3>
            <input placeholder="Username" onChange={e => setAuthForm({...authForm, username: e.target.value})} />
            <input type="password" placeholder="Password" onChange={e => setAuthForm({...authForm, password: e.target.value})} />
            <button type="submit">{authForm.isRegister ? 'Sign Up' : 'Log In'}</button>
            <button type="button" onClick={() => setAuthForm({...authForm, isRegister: !authForm.isRegister})}>
              Switch to {authForm.isRegister ? 'Login' : 'Register'}
            </button>
          </form>
        )}
      </section>

      {/* SEARCH, SORTING & PAGINATION SECTION */}
      <section>
        <h2>Parking Lot Dashboard (Search & Analytics)</h2>
        <input 
          type="text" 
          placeholder="Search by License Plate..." 
          value={search} 
          onChange={e => setSearch(e.target.value)} 
        />
        <select onChange={e => setSortBy(e.target.value)}>
          <option value="id">Sort by ID</option>
          <option value="license_plate">Sort by License Plate</option>
        </select>
        <select onChange={e => setOrder(e.target.value)}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>

        <table border="1" cellPadding="8" style={{ width: '100%', marginTop: '10px' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>License Plate</th>
              <th>Spot ID</th>
              <th>Status</th>
              <th>Fee Charged ($)</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.license_plate}</td>
                <td>{r.spot_id}</td>
                <td>{r.is_active ? 'Active' : 'Checked Out'}</td>
                <td>{r.fee_charged || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* PAGINATION */}
        <div style={{ marginTop: '10px' }}>
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
          <span> Page {page} of {Math.ceil(data.total / 5) || 1} </span>
          <button disabled={page >= Math.ceil(data.total / 5)} onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
      </section>

      {/* NEXT 3 FEATURES */}
      <footer style={{ marginTop: '40px', borderTop: '1px solid #ccc', pt: '10px' }}>
        <h3>Three Features We Would Build Next:</h3>
        <ul>
          <li><strong>1. ANPR Camera Integration:</strong> Automated license plate recognition at gate entry.</li>
          <li><strong>2. Stripe Payment Gateway:</strong> In-app digital payments for hourly billing.</li>
          <li><strong>3. Real-time EV Charging Meters:</strong> Live power consumption tracking for EV spots.</li>
        </ul>
      </footer>
    </div>
  );
}