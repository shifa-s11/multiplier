import React, { useEffect, useMemo, useState } from "react";
import { fetchTopCustomers } from "../api";
import Loading from "./Loading";
import ErrorState from "./ErrorState";

const SORTABLE_COLUMNS = {
  name: "name",
  region: "region",
  total_spend: "total_spend",
};

function TopCustomersTable() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [query, setQuery] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: SORTABLE_COLUMNS.total_spend, direction: "desc" });

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchTopCustomers();
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

  function requestSort(key) {
    setSortConfig((prev) => {
      if (prev.key === key) {
        return { key, direction: prev.direction === "asc" ? "desc" : "asc" };
      }
      return { key, direction: "asc" };
    });
  }

  const filteredAndSortedRows = useMemo(() => {
    const loweredQuery = query.trim().toLowerCase();
    const filtered = rows.filter((row) => {
      const name = String(row.name ?? "").toLowerCase();
      const region = String(row.region ?? "").toLowerCase();
      return name.includes(loweredQuery) || region.includes(loweredQuery);
    });

    const sorted = [...filtered].sort((a, b) => {
      const { key, direction } = sortConfig;
      const multiplier = direction === "asc" ? 1 : -1;

      if (key === SORTABLE_COLUMNS.total_spend) {
        return (Number(a.total_spend ?? 0) - Number(b.total_spend ?? 0)) * multiplier;
      }

      const valueA = String(a[key] ?? "").toLowerCase();
      const valueB = String(b[key] ?? "").toLowerCase();
      return valueA.localeCompare(valueB) * multiplier;
    });

    return sorted;
  }, [query, rows, sortConfig]);

  if (loading) return <Loading />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-4">
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search by name or region"
        className="w-full rounded-md border px-3 py-2 text-sm"
      />

      <div className="max-h-[420px] overflow-auto border rounded-lg">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 bg-slate-100 text-slate-700">
            <tr>
              <th className="px-4 py-3 text-left font-medium">
                <button type="button" onClick={() => requestSort(SORTABLE_COLUMNS.name)}>Name</button>
              </th>
              <th className="px-4 py-3 text-left font-medium">
                <button type="button" onClick={() => requestSort(SORTABLE_COLUMNS.region)}>Region</button>
              </th>
              <th className="px-4 py-3 text-right font-medium">
                <button type="button" onClick={() => requestSort(SORTABLE_COLUMNS.total_spend)}>Total Spend</button>
              </th>
              <th className="px-4 py-3 text-left font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedRows.map((row, index) => (
              <tr key={`${row.customer_id ?? "unknown"}-${index}`} className="odd:bg-white even:bg-slate-50 hover:bg-gray-100">
                <td className="px-4 py-3">{row.name ?? "-"}</td>
                <td className="px-4 py-3">{row.region ?? "Unknown"}</td>
                <td className="px-4 py-3 text-right font-medium">
                  {Number(row.total_spend ?? 0).toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                    maximumFractionDigits: 0,
                  })}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                      row.churned ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
                    }`}
                  >
                    {row.churned ? "Churned" : "Active"}
                  </span>
                </td>
              </tr>
            ))}
            {filteredAndSortedRows.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={4}>
                  No customers found.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TopCustomersTable;
