// localItemStorage.ts
// A utility for storing item data locally in the browser for demo mode
import { v4 as uuidv4 } from 'uuid';

// Types to match API response structures
export interface LocalImage {
  id: string;
  image_url: string;
  is_primary: boolean;
  item_id: string;
  created_at: string;
}

export interface LocalUser {
  id: number;
  username: string;
  profile_picture?: string;
}

export interface LocalItem {
  id: string;
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
  images: LocalImage[];
  tags: string[];
  user: LocalUser;
}

export interface ItemData {
  title: string;
  description: string;
  category: string;
  type: string;
  size: string;
  condition: string;
  point_value: number;
  tags: string[];
}

// Constants
const LOCAL_ITEMS_KEY = 'rewear_demo_items';
const DEMO_USER_ID = 1; // This should match the ID of your demo user

// Helper to convert a File to base64 string
export const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
  });
};

// Helper to check if user is demo user
export const isDemoUser = (user: any): boolean => {
  return user && (user.email === 'demo@example.com' || user.id === DEMO_USER_ID);
};

// Get all locally stored items
export const getLocalItems = (): LocalItem[] => {
  const itemsJson = localStorage.getItem(LOCAL_ITEMS_KEY);
  return itemsJson ? JSON.parse(itemsJson) : [];
};

// Save an item locally
export const saveLocalItem = async (
  itemData: ItemData,
  imageFiles: File[],
  user: LocalUser
): Promise<LocalItem> => {
  // Create a new local item
  const now = new Date().toISOString();
  const itemId = uuidv4();
  
  // Convert all images to base64
  const imagePromises = imageFiles.map(async (file, index) => {
    const base64 = await fileToBase64(file);
    return {
      id: uuidv4(),
      image_url: base64,
      is_primary: index === 0,
      item_id: itemId,
      created_at: now
    };
  });
  
  const images = await Promise.all(imagePromises);
  
  const newItem: LocalItem = {
    id: itemId,
    title: itemData.title,
    description: itemData.description,
    category: itemData.category,
    type: itemData.type,
    size: itemData.size,
    condition: itemData.condition,
    point_value: itemData.point_value,
    status: 'pending',
    is_approved: true, // Auto-approve local items for demo
    user_id: user.id,
    created_at: now,
    updated_at: now,
    images,
    tags: itemData.tags,
    user
  };
  
  // Get existing items and add the new one
  const existingItems = getLocalItems();
  existingItems.push(newItem);
  
  // Save back to localStorage
  localStorage.setItem(LOCAL_ITEMS_KEY, JSON.stringify(existingItems));
  
  return newItem;
};

// Filter local items based on criteria
export const filterLocalItems = (
  items: LocalItem[],
  category?: string,
  size?: string,
  condition?: string,
  searchTerm?: string
): LocalItem[] => {
  return items.filter(item => {
    // Category filter
    if (category && category !== 'all' && item.category !== category) return false;
    
    // Size filter
    if (size && size !== 'all' && item.size !== size) return false;
    
    // Condition filter
    if (condition && condition !== 'all' && item.condition !== condition) return false;
    
    // Search term
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      const titleMatch = item.title.toLowerCase().includes(search);
      const descMatch = item.description.toLowerCase().includes(search);
      if (!titleMatch && !descMatch) return false;
    }
    
    return true;
  });
};

// Delete a local item
export const deleteLocalItem = (itemId: string): boolean => {
  const items = getLocalItems();
  const filteredItems = items.filter(item => item.id !== itemId);
  
  if (filteredItems.length !== items.length) {
    localStorage.setItem(LOCAL_ITEMS_KEY, JSON.stringify(filteredItems));
    return true;
  }
  
  return false;
};
