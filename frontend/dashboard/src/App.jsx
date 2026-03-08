import React from "react";
import Card from "./components/Card";
import RevenueChart from "./components/RevenueChart";
import CategoryChart from "./components/CategoryChart";
import TopCustomersTable from "./components/TopCustomersTable";
import RegionSummary from "./components/RegionSummary";

function App() {
  return (
    <div className="min-h-screen bg-slate-100">
      <div className="max-w-7xl mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Customer Analytics Dashboard</h1>
          <p className="mt-2 text-sm text-slate-600">Data pipeline + analytics dashboard</p>
        </header>

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card title="Revenue Trend">
            <RevenueChart />
          </Card>
          <Card title="Category Performance">
            <CategoryChart />
          </Card>
        </section>

        <section className="mt-8">
          <Card title="Top Customers">
            <TopCustomersTable />
          </Card>
        </section>

        <section className="mt-8">
          <Card title="Regional Analysis">
            <RegionSummary />
          </Card>
        </section>
      </div>
    </div>
  );
}

export default App;
