import React, { useEffect, useMemo, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { fetchRevenue } from "../api";
import Loading from "./Loading";
import ErrorState from "./ErrorState";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Title);

function RevenueChart() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [startMonth, setStartMonth] = useState("");
  const [endMonth, setEndMonth] = useState("");

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchRevenue();
        const safeRows = Array.isArray(data) ? data : [];
        if (mounted) {
          const sorted = [...safeRows].sort((a, b) =>
            String(a.order_year_month ?? "").localeCompare(String(b.order_year_month ?? "")),
          );
          setRows(sorted);
          if (sorted.length > 0) {
            setStartMonth(String(sorted[0].order_year_month ?? ""));
            setEndMonth(String(sorted[sorted.length - 1].order_year_month ?? ""));
          }
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

  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const month = String(row.order_year_month ?? "");
      const afterStart = startMonth ? month >= startMonth : true;
      const beforeEnd = endMonth ? month <= endMonth : true;
      return afterStart && beforeEnd;
    });
  }, [rows, startMonth, endMonth]);

  const chartData = useMemo(
    () => ({
      labels: filteredRows.map((row) => row.order_year_month),
      datasets: [
        {
          label: "Revenue",
          data: filteredRows.map((row) => Number(row.total_revenue ?? 0)),
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.2)",
          pointBackgroundColor: "#2563eb",
          tension: 0.25,
        },
      ],
    }),
    [filteredRows],
  );

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Monthly Revenue Trend",
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
          text: "Month",
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
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="text-sm font-medium text-slate-700">
          Start month
          <input
            type="month"
            value={startMonth}
            onChange={(event) => setStartMonth(event.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          End month
          <input
            type="month"
            value={endMonth}
            onChange={(event) => setEndMonth(event.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </label>
      </div>
      <div className="h-80">
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}

export default RevenueChart;
