import React, { useEffect, useMemo, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { fetchCategories } from "../api";
import Loading from "./Loading";
import ErrorState from "./ErrorState";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend, Title);

function CategoryChart() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchCategories();
        if (mounted) {
          setRows(Array.isArray(data) ? data : []);
          setError(false);
        }
      } catch {
        if (mounted) setError(true);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const chartData = useMemo(
    () => ({
      labels: rows.map((row) => row.category),
      datasets: [
        {
          label: "Revenue",
          data: rows.map((row) => Number(row.total_revenue ?? 0)),
          backgroundColor: "#10b981",
          borderRadius: 8,
        },
      ],
    }),
    [rows],
  );

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Revenue by Product Category",
      },
      legend: {
        display: true,
        position: "top",
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Category",
        },
      },
      y: {
        title: {
          display: true,
          text: "Revenue (USD)",
        },
      },
    },
  };

  if (loading) return <Loading />;
  if (error) return <ErrorState />;

  return (
    <div className="h-80">
      <Bar data={chartData} options={chartOptions} />
    </div>
  );
}

export default CategoryChart;
