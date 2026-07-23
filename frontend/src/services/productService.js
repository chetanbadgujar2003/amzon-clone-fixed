import api from "./api";

// Get All Products
export const getProducts = async () => {
  const response = await api.get("/products/");
  return response.data;
};

// Get Product By ID
export const getProductById = async (id) => {
  const response = await api.get(`/products/${id}/`);
  return response.data;
};

// Search Products
export const searchProducts = async (keyword) => {
  const response = await api.get(`/products/search/${keyword}/`);
  return response.data;
};

// Get Products By Category
export const getProductsByCategory = async (category) => {
  const response = await api.get(`/products/category/${category}/`);
  return response.data;
};

// Create Product
export const createProduct = async (productData) => {
  const response = await api.post('/products/', productData);
  return response.data;
};