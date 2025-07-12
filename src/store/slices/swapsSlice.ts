import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

interface Swap {
  id: number;
  requester_id: number;
  provider_id: number;
  requester_item_id: number | null;
  provider_item_id: number;
  status: string;
  points_used: number;
  created_at: string;
  updated_at: string;
  requester_item: ItemBasic | null;
  provider_item: ItemBasic;
  requester: UserBasic;
  provider: UserBasic;
}

interface ItemBasic {
  id: number;
  title: string;
  primary_image?: string;
}

interface UserBasic {
  id: number;
  username: string;
  profile_picture?: string;
}

interface SwapsState {
  swaps: Swap[];
  selectedSwap: Swap | null;
  userSwaps: {
    requested: Swap[];
    provided: Swap[];
  };
  isLoading: boolean;
  error: string | null;
}

const initialState: SwapsState = {
  swaps: [],
  selectedSwap: null,
  userSwaps: {
    requested: [],
    provided: [],
  },
  isLoading: false,
  error: null,
};

// API base URL
const API_URL = 'http://localhost:8000/api';

// Get all swaps (admin only)
export const fetchAllSwaps = createAsyncThunk(
  'swaps/fetchAllSwaps',
  async (token: string, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/swaps`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch swaps');
      }
      return rejectWithValue('Failed to fetch swaps. Please try again.');
    }
  }
);

// Get user's swaps
export const fetchUserSwaps = createAsyncThunk(
  'swaps/fetchUserSwaps',
  async (token: string, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/swaps`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch user swaps');
      }
      return rejectWithValue('Failed to fetch user swaps. Please try again.');
    }
  }
);

// Get swap by ID
export const fetchSwapById = createAsyncThunk(
  'swaps/fetchSwapById',
  async ({ id, token }: { id: number; token: string }, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/swaps/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to fetch swap');
      }
      return rejectWithValue('Failed to fetch swap. Please try again.');
    }
  }
);

// Create new swap request
export const createSwapRequest = createAsyncThunk(
  'swaps/createSwapRequest',
  async (
    {
      swapData,
      token,
    }: {
      swapData: {
        provider_item_id: number;
        requester_item_id?: number;
        points_used?: number;
      };
      token: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.post(`${API_URL}/swaps`, swapData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to create swap request');
      }
      return rejectWithValue('Failed to create swap request. Please try again.');
    }
  }
);

// Update swap status (accept/reject/complete)
export const updateSwapStatus = createAsyncThunk(
  'swaps/updateSwapStatus',
  async (
    {
      id,
      status,
      token,
    }: {
      id: number;
      status: string;
      token: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.put(
        `${API_URL}/swaps/${id}`,
        { status },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data.detail || 'Failed to update swap status');
      }
      return rejectWithValue('Failed to update swap status. Please try again.');
    }
  }
);

const swapsSlice = createSlice({
  name: 'swaps',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSelectedSwap: (state) => {
      state.selectedSwap = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all swaps cases (admin)
      .addCase(fetchAllSwaps.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAllSwaps.fulfilled, (state, action: PayloadAction<Swap[]>) => {
        state.isLoading = false;
        state.swaps = action.payload;
      })
      .addCase(fetchAllSwaps.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch user swaps cases
      .addCase(fetchUserSwaps.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserSwaps.fulfilled, (state, action: PayloadAction<{ requested: Swap[]; provided: Swap[] }>) => {
        state.isLoading = false;
        state.userSwaps = action.payload;
      })
      .addCase(fetchUserSwaps.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch swap by ID cases
      .addCase(fetchSwapById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSwapById.fulfilled, (state, action: PayloadAction<Swap>) => {
        state.isLoading = false;
        state.selectedSwap = action.payload;
      })
      .addCase(fetchSwapById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Create swap request cases
      .addCase(createSwapRequest.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createSwapRequest.fulfilled, (state, action: PayloadAction<Swap>) => {
        state.isLoading = false;
        if (state.userSwaps.requested) {
          state.userSwaps.requested.unshift(action.payload);
        } else {
          state.userSwaps.requested = [action.payload];
        }
      })
      .addCase(createSwapRequest.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Update swap status cases
      .addCase(updateSwapStatus.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateSwapStatus.fulfilled, (state, action: PayloadAction<Swap>) => {
        state.isLoading = false;
        
        // Update in all relevant arrays
        if (state.selectedSwap && state.selectedSwap.id === action.payload.id) {
          state.selectedSwap = action.payload;
        }
        
        state.swaps = state.swaps.map(swap => 
          swap.id === action.payload.id ? action.payload : swap
        );
        
        state.userSwaps.requested = state.userSwaps.requested.map(swap => 
          swap.id === action.payload.id ? action.payload : swap
        );
        
        state.userSwaps.provided = state.userSwaps.provided.map(swap => 
          swap.id === action.payload.id ? action.payload : swap
        );
      })
      .addCase(updateSwapStatus.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearSelectedSwap } = swapsSlice.actions;
export default swapsSlice.reducer;
