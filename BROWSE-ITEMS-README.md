# ReWear Item Browsing Feature

This feature allows all users to browse items in the ReWear platform without requiring login.

## Features

- Public access: Browse items without authentication
- Search functionality: Search items by keyword
- Filtering: Filter items by category, size, and condition
- Pagination: Browse through multiple pages of items
- Item details: View detailed information about each item
- Responsive design: Works on mobile and desktop

## Technical Implementation

The item browsing feature uses:

1. **Direct API calls**: Makes HTTP requests directly to the backend API
2. **Local state management**: Uses React's useState for managing component state
3. **Axios**: For making HTTP requests
4. **React Router**: For navigation between pages

## User Flow

1. User accesses the "/items" route or clicks "Browse Items" from the navigation
2. The ItemListingPage loads and displays available items
3. User can:
   - Search for specific items
   - Filter by category, size, or condition
   - Navigate between pages
   - Click on an item to view details
4. When viewing item details, unauthenticated users see a "Login to Swap" button
5. Authenticated users see "Request Swap" or "Your Item" buttons depending on ownership

## Components

- **ItemListingPage**: Main page for browsing items
- **ItemDetailPage**: Page for viewing detailed item information
- **MainLayout**: Common layout with navigation that includes Browse Items link

## API Endpoints Used

- `GET /api/items`: Retrieves list of items with optional filters
- `GET /api/items/{id}`: Retrieves details for a specific item

## Security

- The browse functionality is accessible to all users without authentication
- Swap actions require authentication
- User-specific information is only displayed to authenticated users
