import { useState } from 'react';
import HotelFilterForm from '../components/HotelFilters';
import HotelScatterPlot from "../components/HotelScatterPlot";

export default function Home() {
  const [submittedFilters, setSubmittedFilters] = useState(null);

  const handleSearch = (filters) => {
    console.log('User submitted:', filters);
    setSubmittedFilters(filters);
    // TODO: call your API here later
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Hotel</h1>

      {/* ✅ Filter Form */}
      <HotelFilterForm onSubmit={handleSearch} />

      {/* ✅ Show submitted filters for debugging */}
      {submittedFilters && (
        <pre style={{ marginTop: '2rem', background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
          {JSON.stringify(submittedFilters, null, 2)}
        </pre>
      )}

      {/* ✅ Render Plotly Chart Once Filters Are Submitted */}
      {submittedFilters && (
        <div style={{ marginTop: "2rem" }}>
          <HotelScatterPlot filters={submittedFilters} />
        </div>
      )}
    </div>
  );
}