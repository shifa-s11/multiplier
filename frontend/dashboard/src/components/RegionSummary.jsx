import React, { useEffect, useState } from "react";
import { fetchRegions } from "../api";
import Loading from "./Loading";
import ErrorState from "./ErrorState";

function RegionSummary() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchRegions();
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

  if (loading) return <Loading />;
  if (error) return <ErrorState />;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {rows.map((row, index) => (
        <article key={`${row.region ?? "region"}-${index}`} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <h3 className="mb-3 text-base font-semibold text-slate-800">{row.region ?? "Unknown"}</h3>
          <p className="text-sm text-slate-600">Customers: <span className="font-medium text-slate-900">{Number(row.number_of_customers ?? 0)}</span></p>
          <p className="text-sm text-slate-600">Orders: <span className="font-medium text-slate-900">{Number(row.number_of_orders ?? 0)}</span></p>
          <p className="text-sm text-slate-600">Revenue: <span className="font-medium text-slate-900">{Number(row.total_revenue ?? 0).toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })}</span></p>
        </article>
      ))}
    </div>
  );
}

export default RegionSummary;
