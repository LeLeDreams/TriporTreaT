import { useState } from 'react';
import './HotelFilters.css';   // optional – see CSS below

export default function HotelFilterForm({ onSubmit, initialFilters = {} }) {
  const [filters, setFilters] = useState({
    rating_min: initialFilters.rating_min ?? 4.0,
    rating_max: initialFilters.rating_max ?? 5.0,
    price_min:  initialFilters.price_min  ?? 0,
    price_max:  initialFilters.price_max  ?? 1000,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: name.includes('rating') ? parseFloat(value) || 0 : parseInt(value) || 0
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(filters);
  };

  return (
    <form onSubmit={handleSubmit} className="hotel-filter-form">
      <div className="form-group">
        <label>
          Min Rating
          <input
            type="number"
            step="0.1"
            name="rating_min"
            value={filters.rating_min}
            onChange={handleChange}
            min="0"
            max="5"
            required
          />
        </label>

        <label>
          Max Rating
          <input
            type="number"
            step="0.1"
            name="rating_max"
            value={filters.rating_max}
            onChange={handleChange}
            min="0"
            max="5"
            required
          />
        </label>
      </div>

      <div className="form-group">
        <label>
          Min Price ($)
          <input
            type="number"
            name="price_min"
            value={filters.price_min}
            onChange={handleChange}
            min="0"
            required
          />
        </label>

        <label>
          Max Price ($)
          <input
            type="number"
            name="price_max"
            value={filters.price_max}
            onChange={handleChange}
            min="0"
            required
          />
        </label>
      </div>

      <button type="submit" className="search-btn">
        Search Hotels
      </button>
    </form>
  );
}