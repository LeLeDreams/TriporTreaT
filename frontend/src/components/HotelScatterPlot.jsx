// src/components/HotelScatterPlot.jsx
import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

export default function HotelScatterPlot({ filters }) {
    const [hotels, setHotels] = useState([]);

    useEffect(() => {
    if (!filters) return;

    const query = new URLSearchParams({
        min_price: filters.price_min,
        max_price: filters.price_max,
        min_rating: filters.rating_min,
        max_rating: filters.rating_max
    });

    fetch(`http://localhost:8000/api/hotels?${query.toString()}`)
        .then((res) => res.json())
        .then((data) => setHotels(data))
        .catch((err) => console.error("Error fetching hotel data:", err));
    }, [filters]);  // ✅ refetch when filters change


    if (hotels.length === 0) return <p>Loading...</p>;

    // Extract fields
    const ratings = hotels.map((h) => h.rating);
    const priceMin = hotels.map((h) => h.price_min);
    const priceMax = hotels.map((h) => h.price_max);
    const priceAvg = hotels.map((h) => h.price_avg);
    const names = hotels.map((h) => h.name);

    // ✅ Add jitter to ratings
    const jitteredRatings = ratings.map((r) => r + (Math.random() - 0.5) * 0.1);

    // ✅ Error bars
    const errorUpper = priceMax.map((max, i) => max - priceAvg[i]);
    const errorLower = priceAvg.map((avg, i) => avg - priceMin[i]);

    return (
        <Plot
            data={[
                {
                    x: jitteredRatings,
                    y: priceAvg,
                    text: names,
                    type: "scatter",
                    mode: "markers",
                    marker: { size: 8, opacity: 0.75 },

                    // ✅ Error bars
                    error_y: {
                        type: "data",
                        symmetric: false,
                        array: errorUpper,
                        arrayminus: errorLower,
                        thickness: 1.3,
                        width: 4,
                    },

                    hovertemplate:
                        "<b>%{text}</b><br>" +
                        "Rating: %{x:.2f}<br>" +
                        "Avg Price: %{y}<br>" +
                        "<extra></extra>",
                },
            ]}
            layout={{
                title: "Hotel Price Ranges vs Rating",
                xaxis: { title: "Rating" },
                yaxis: { title: "Price (Min–Avg–Max)" },
                width: 900,
                height: 600,
            }}
            config={{ responsive: true }}
        />
    );
}
