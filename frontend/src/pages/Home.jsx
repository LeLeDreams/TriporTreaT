import { useState } from 'react';
import HotelFilterForm from '../components/HotelFilters';

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
      <HotelFilterForm onSubmit={handleSearch} />
      
      {submittedFilters && (
        <pre style={{ marginTop: '2rem', background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
          {JSON.stringify(submittedFilters, null, 2)}
        </pre>
      )}
    </div>
  );
}