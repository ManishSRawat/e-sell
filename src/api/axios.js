import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:5000/api' });

// Simulate dynamic product data (fetching from a local JSON file)
const fetchProducts = async () => {
  // In a real app, you'd fetch from an API endpoint (e.g. api.get('/products'))
  // For demo, we simulate a fetch from a local JSON file (e.g. /public/products.json)
  // (You can later replace this with an actual fetch call.)
  const res = await fetch('/products.json');
  const data = await res.json();
  return data.products; // Assume products.json contains { products: [...] }
};

// Helper function for live search filtering (client-side filtering demo)
const filterProducts = (products, searchTerm) => {
  if (!searchTerm) return products;
  const term = searchTerm.toLowerCase();
  return products.filter(p => p.name.toLowerCase().includes(term) || (p.description && p.description.toLowerCase().includes(term)));
};

export { fetchProducts, filterProducts };
export default api; 