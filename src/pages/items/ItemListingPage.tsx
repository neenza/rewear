import { useEffect, useState } from 'react';
import { useAppDispatch } from '@/hooks/useRedux';
import { fetchItems } from '@/store/slices/itemsSlice';
import { Link } from 'react-router-dom';
import axios from 'axios';
import MainLayout from '@/layouts/MainLayout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

// Define interfaces for our data
interface Image {
  id: number;
  image_url: string;
  is_primary: boolean;
  item_id: number;
  created_at: string;
}

interface UserBasic {
  id: number;
  username: string;
  profile_picture?: string;
}

interface Item {
  id: number;
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

export default function ItemListingPage() {
  const dispatch = useAppDispatch();
  const [items, setItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSize, setSelectedSize] = useState('all');
  const [selectedCondition, setSelectedCondition] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [itemsPerPage] = useState(12);
  
  useEffect(() => {
    loadItems();
  }, [currentPage]);
  
  const loadItems = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Construct query parameters
      const params = new URLSearchParams();
      params.append('skip', String((currentPage - 1) * itemsPerPage));
      params.append('limit', String(itemsPerPage));
      
      if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
      if (selectedSize && selectedSize !== 'all') params.append('size', selectedSize);
      if (selectedCondition && selectedCondition !== 'all') params.append('condition', selectedCondition);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await axios.get(`/api/items?${params.toString()}`);
      // Check if response.data is an array (old format) or object with items property (new format)
      if (Array.isArray(response.data)) {
        setItems(response.data);
        setTotalPages(1); // Without total count info, assume 1 page
      } else {
        setItems(response.data.items || []);
        setTotalPages(Math.ceil(response.data.total / itemsPerPage) || 1);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load items. Please try again.');
      console.error('Error loading items:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSearch = () => {
    setCurrentPage(1); // Reset to first page when searching
    loadItems();
  };
  
  const handleFilter = () => {
    setCurrentPage(1); // Reset to first page when filtering
    loadItems();
  };
  
  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };
  
  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="flex flex-col space-y-4 mb-8">
          <h1 className="text-3xl font-bold text-gradient">Browse Items</h1>
          
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button onClick={handleSearch} className="whitespace-nowrap">
              Search
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Category</label>
              <Select
                value={selectedCategory}
                onValueChange={(value) => setSelectedCategory(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="tops">Tops</SelectItem>
                  <SelectItem value="bottoms">Bottoms</SelectItem>
                  <SelectItem value="dresses">Dresses</SelectItem>
                  <SelectItem value="outerwear">Outerwear</SelectItem>
                  <SelectItem value="shoes">Shoes</SelectItem>
                  <SelectItem value="accessories">Accessories</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Size</label>
              <Select
                value={selectedSize}
                onValueChange={(value) => setSelectedSize(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Sizes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sizes</SelectItem>
                  <SelectItem value="xs">XS</SelectItem>
                  <SelectItem value="s">S</SelectItem>
                  <SelectItem value="m">M</SelectItem>
                  <SelectItem value="l">L</SelectItem>
                  <SelectItem value="xl">XL</SelectItem>
                  <SelectItem value="xxl">XXL</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Condition</label>
              <Select
                value={selectedCondition}
                onValueChange={(value) => setSelectedCondition(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any Condition" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Any Condition</SelectItem>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="like_new">Like New</SelectItem>
                  <SelectItem value="good">Good</SelectItem>
                  <SelectItem value="fair">Fair</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <Button onClick={handleFilter} variant="outline" className="self-start">
            Apply Filters
          </Button>
        </div>
        
        {isLoading && <div className="text-center py-8">Loading items...</div>}
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {!isLoading && items.length === 0 && (
          <div className="text-center py-8">
            <p className="text-xl">No items found</p>
            <p className="text-gray-500 mt-2">Try different filters or check back later</p>
          </div>
        )}
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {items.map((item) => (
            <Link key={item.id} to={`/items/${item.id}`}>
              <Card className="h-full bg-gradient-card shadow-warm hover-lift border-0">
                <div className="aspect-square overflow-hidden rounded-t-lg">
                  <img
                    src={item.images.length > 0 ? item.images.find(img => img.is_primary)?.image_url || item.images[0].image_url : 'https://via.placeholder.com/300'}
                    alt={item.title}
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg line-clamp-1 text-gradient">{item.title}</CardTitle>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="flex flex-wrap gap-2 mb-3">
                    <Badge className="bg-primary/20 text-primary border-primary/30">{item.category}</Badge>
                    <Badge variant="outline" className="border-primary/30 text-primary">{item.size}</Badge>
                    <Badge variant="secondary" className="bg-accent/50 text-accent-foreground">{item.condition}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">{item.description}</p>
                  {item.user && (
                    <div className="mt-3 flex items-center text-sm text-muted-foreground">
                      <div className="w-6 h-6 rounded-full bg-gradient-primary flex items-center justify-center mr-2 shadow-warm">
                        {item.user.profile_picture ? 
                          <img src={item.user.profile_picture} alt={item.user.username} className="w-full h-full rounded-full" /> : 
                          <span className="text-xs text-primary-foreground font-medium">{item.user.username.charAt(0).toUpperCase()}</span>
                        }
                      </div>
                      <span className="font-medium">{item.user.username}</span>
                    </div>
                  )}
                </CardContent>
                <CardFooter className="pt-2">
                  <div className="w-full flex justify-between items-center">
                    <span className="text-xl font-bold text-gradient">{item.point_value} points</span>
                  </div>
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
        
        {items.length > 0 && (
          <div className="flex justify-between items-center mt-8">
            <Button
              onClick={handlePrevPage}
              disabled={currentPage === 1}
              variant="outline"
            >
              Previous
            </Button>
            
            <span>
              Page {currentPage} of {totalPages}
            </span>
            
            <Button
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
              variant="outline"
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
