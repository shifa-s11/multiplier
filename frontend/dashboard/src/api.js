const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://customer-analytics-backend.onrender.com/api";

async function fetchJson(path) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Network error");
  }
}

export function fetchRevenue() {
  return fetchJson("/revenue");
}

export function fetchTopCustomers() {
  return fetchJson("/top-customers");
}

export function fetchCategories() {
  return fetchJson("/categories");
}

export function fetchRegions() {
  return fetchJson("/regions");
}
