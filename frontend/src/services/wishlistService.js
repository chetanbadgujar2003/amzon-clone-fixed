import api from "./api";

// Get Wishlist
export const getWishlist = async () => {
  const response = await api.get("/wishlist/");
  return response.data;
};

// Add Product
export const addWishlist = async (product) => {
  const response = await api.post("/wishlist/", product);
  return response.data;
};

// Remove Product
export const removeWishlist = async (id) => {
  const response = await api.delete(`/wishlist/${id}`);
  return response.data;
};

// Clear Wishlist
export const clearWishlist = async () => {
  const response = await api.delete("/wishlist");
  return response.data;
};