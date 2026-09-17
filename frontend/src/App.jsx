import React, { useState } from 'react';
import './index.css';

export default function App() {
  const [spots] = useState([
    { spot_id: 'L1-EV-01', spot_type: 'EV', is_occupied: false },
    { spot_id: 'L1-STD-01', spot_type: 'STANDARD', is_occupied: true },
    { spot_id: 'L1-CMP-01', spot_type: 'COMPACT', is_occupied: false },
  ]);

  const [licensePlate, setLicensePlate] = useState('');
  const [vehicleType, setVehicleType] = useState('STANDARD');

  const handleCheckIn = (e) => {
    e.preventDefault();
    alert(`Check-in request for ${licensePlate} (${vehicleType})`);
    setLicensePlate('');
  };

  return (
    <div>
      <nav className="navbar">
        <h2>🅿️ Parking Lot Manager</h2>
        <button className="button">Admin Login</button>
      </nav>

      <div className="container">
        <div className="card">
          <h3>Vehicle Check-In</h3>
          <form onSubmit={handleCheckIn} style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              placeholder="License Plate (e.g. ABC-1234)"
              value={licensePlate}
              onChange={(e) => setLicensePlate(e.target.value)}
              required
              style={{ padding: '8px', flex: 1, borderRadius: '4px', border: '1px solid #ccc' }}
            />
            <select
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            >
              <option value="COMPACT">Compact</option>
              <option value="STANDARD">Standard</option>
              <option value="EV">EV</option>
            </select>
            <button type="submit" className="button">Park Vehicle</button>
          </form>
        </div>

        <div className="card">
          <h3>Parking Spot Status</h3>
          <div className="grid">
            {spots.map((spot) => (
              <div
                key={spot.spot_id}
                className={`spot-card ${spot.is_occupied ? 'occupied' : 'available'}`}
              >
                <div>{spot.spot_id}</div>
                <small>{spot.spot_type}</small>
                <div>{spot.is_occupied ? 'Occupied' : 'Free'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
