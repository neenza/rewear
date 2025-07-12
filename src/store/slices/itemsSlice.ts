import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { getLocalItems, saveLocalItem, isDemoUser } from '@/utils/localItemStorage';

interface Item {
  id: number | string;
  title: string;
  description: string;
  category: string;
  type: string;
  size: string;
  condition: string;
  point_value: number;
  status: string;
  is_approved: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
  images: Image[];
  tags: string[];
  user: UserBasic;
}

interface Image {
  id: number | string;
  image_url: string;
  is_primary: boolean;
  item_id: number | string;
  created_at: string;
}

interface UserBasic {
  id: number;
  username: string;
  profile_picture?: string;
}

interface ItemsState {
  items: Item[];
  filteredItems: Item[];
  selectedItem: Item | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    category: string | null;
    size: string | null;
    condition: string | null;
    searchTerm: string;
  };
  pagination: {
    currentPage: number;
    totalPages: number;
    limit: number;
  };
}

const initialState: ItemsState = {
  items: [],
  filteredItems: [],
  selectedItem: null,
  isLoading: false,
  error: null,
  filters: {
    category: null,
    size: null,
    condition: null,
    searchTerm: '',
  },
  pagination: {
    currentPage: 1,
    totalPages: 1,
    limit: 12,
  },
};

// API base URL
const API_URL = 'http://localhost:8000/api';

// Get all items with optional filters
export const fetchItems = createAsyncThunk(
  'items/fetchItems',
  async (
    {
      page = 1,
      limit = 12,
      category,
      size,
      condition,
      searchTerm,
    }: {
      page?: number;
      limit?: number;
      category?: string;
      size?: string;
      condition?: string;
      searchTerm?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      // Construct query parameters
      const params = new URLSearchParams();
      params.append('skip', String((page - 1) * limit));
      params.append('limit', String(limit));
      
      if (category) params.append('category', category);
      if (size) params.append('size', size);
      if (condition) params.append('condition', condition);
      if (searchTerm) params.append('search', searchTerm);

      const response = await axios.get(`${API_URL}/items?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch items');
      }
      return rejectWithValue('Failed to fetch items. Please try again.');
    }
  }
);

// Get item by ID
export const fetchItemById = createAsyncThunk(
  'items/fetchItemById',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/items/${id}`);
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch item');
      }
      return rejectWithValue('Failed to fetch item. Please try again.');
    }
  }
);

// Create new item
export const createItem = createAsyncThunk(
  'items/createItem',
  async (
    {
      itemData,
      images,
      token,
    }: {
      itemData: {
        title: string;
        description: string;
        category: string;
        type: string;
        size: string;
        condition: string;
        point_value: number;
        tags: string[];
      };
      images: File[];
      token: string;
    },
    { rejectWithValue }
  ) => {
    try {
      // Create FormData for multipart/form-data request
      const formData = new FormData();
      formData.append('item_in', JSON.stringify(itemData));
      
      // Append each image
      images.forEach((image) => {
        formData.append('images', image);
      });

      const response = await axios.post(`${API_URL}/items`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to create item');
      }
      return rejectWithValue('Failed to create item. Please try again.');
    }
  }
);

// Update item
export const updateItem = createAsyncThunk(
  'items/updateItem',
  async (
    {
      id,
      itemData,
      token,
    }: {
      id: number;
      itemData: {
        title?: string;
        description?: string;
        category?: string;
        type?: string;
        size?: string;
        condition?: string;
        point_value?: number;
        tags?: string[];
      };
      token: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.put(`${API_URL}/items/${id}`, itemData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to update item');
      }
      return rejectWithValue('Failed to update item. Please try again.');
    }
  }
);

// Delete item
export const deleteItem = createAsyncThunk(
  'items/deleteItem',
  async (
    {
      id,
      token,
    }: {
      id: number;
      token: string;
    },
    { rejectWithValue }
  ) => {
    try {
      await axios.delete(`${API_URL}/items/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return id;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to delete item');
      }
      return rejectWithValue('Failed to delete item. Please try again.');
    }
  }
);

const itemsSlice = createSlice({
  name: 'items',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<ItemsState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    resetFilters: (state) => {
      state.filters = initialState.filters;
    },
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.pagination.currentPage = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearSelectedItem: (state) => {
      state.selectedItem = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch items cases
      .addCase(fetchItems.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchItems.fulfilled, (state, action: PayloadAction<Item[]>) => {
        state.isLoading = false;
        state.items = action.payload;
        state.filteredItems = action.payload;
        state.pagination.totalPages = Math.ceil(action.payload.length / state.pagination.limit);
      })
      .addCase(fetchItems.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch item by ID cases
      .addCase(fetchItemById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchItemById.fulfilled, (state, action: PayloadAction<Item>) => {
        state.isLoading = false;
        state.selectedItem = action.payload;
      })
      .addCase(fetchItemById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Create item cases
      .addCase(createItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createItem.fulfilled, (state, action: PayloadAction<Item>) => {
        state.isLoading = false;
        state.items.unshift(action.payload);
        state.filteredItems = [...state.items];
      })
      .addCase(createItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Update item cases
      .addCase(updateItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateItem.fulfilled, (state, action: PayloadAction<Item>) => {
        state.isLoading = false;
        state.items = state.items.map(item => 
          item.id === action.payload.id ? action.payload : item
        );
        state.filteredItems = [...state.items];
        if (state.selectedItem && state.selectedItem.id === action.payload.id) {
          state.selectedItem = action.payload;
        }
      })
      .addCase(updateItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Delete item cases
      .addCase(deleteItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteItem.fulfilled, (state, action: PayloadAction<number>) => {
        state.isLoading = false;
        state.items = state.items.filter(item => item.id !== action.payload);
        state.filteredItems = [...state.items];
        if (state.selectedItem && state.selectedItem.id === action.payload) {
          state.selectedItem = null;
        }
      })
      .addCase(deleteItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  setFilters, 
  resetFilters, 
  setCurrentPage, 
  clearError,
  clearSelectedItem,
} = itemsSlice.actions;

export default itemsSlice.reducer;
