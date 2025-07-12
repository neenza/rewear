import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/hooks/useRedux';
import { createSwapRequest } from '@/store/slices/swapsSlice';
import MainLayout from '@/layouts/MainLayout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, ArrowRight, Gift, Coins } from 'lucide-react';
import axios from 'axios';

interface Item {
  id: number;
  title: string;
  description: string;
  category: string;
  type: string;
  size: string;
  condition: string;
  point_value: number;
  user_id: number;
  status: string;
  is_approved: boolean;
  created_at: string;
  updated_at: string | null;
  images: Array<{
    id: number;
    image_url: string;
    is_primary: boolean;
    item_id: number;
    created_at: string;
  }>;
  tags: string[];
  user: {
    id: number;
    email: string;
    username: string;
    profile_picture: string | null;
    points_balance: number;
    role: string;
    created_at: string;
    updated_at: string | null;
  } | null;
}

export default function NewSwapPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, token } = useAppSelector((state) => state.auth);
  const { isLoading, error } = useAppSelector((state) => state.swaps);
  
  const [targetItem, setTargetItem] = useState<Item | null>(null);
  const [userItems, setUserItems] = useState<Item[]>([]);
  const [swapType, setSwapType] = useState<'item' | 'points'>('points');
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [dataError, setDataError] = useState<string | null>(null);
  
  const itemId = searchParams.get('item_id');
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (!itemId) {
      navigate('/items');
      return;
    }
    
    const loadData = async () => {
      setIsLoadingData(true);
      setDataError(null);
      
      try {
        // Load target item
        const targetResponse = await axios.get(`/api/items/${itemId}`);
        const targetItemData = targetResponse.data;
        
        // Check if user is trying to swap their own item
        if (targetItemData.user_id === user?.id) {
          setDataError("You cannot swap your own item");
          return;
        }
        
        setTargetItem(targetItemData);
        
        // Load user's items for item swap
        const userItemsResponse = await axios.get('/api/items/my-items', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUserItems(userItemsResponse.data.items || []);
        
      } catch (err: any) {
        setDataError(err.response?.data?.detail || 'Failed to load data');
        console.error('Error loading data:', err);
      } finally {
        setIsLoadingData(false);
      }
    };
    
    loadData();
  }, [itemId, isAuthenticated, user, token, navigate]);
  
  const handleSubmit = async () => {
    if (!targetItem || !token) return;
    
    const swapData = {
      provider_item_id: targetItem.id,
      ...(swapType === 'item' && selectedItemId ? { requester_item_id: selectedItemId } : {}),
      ...(swapType === 'points' ? { points_used: targetItem.point_value } : {})
    };
    
    try {
      await dispatch(createSwapRequest({ swapData, token })).unwrap();
      navigate('/dashboard?tab=swaps');
    } catch (error) {
      // Error is handled by the reducer
    }
  };
  
  const getConditionLabel = (condition: string) => {
    const labels = {
      new: 'New',
      like_new: 'Like New',
      good: 'Good',
      fair: 'Fair',
    };
    return labels[condition as keyof typeof labels] || condition;
  };
  
  if (!isAuthenticated) {
    return null; // Will redirect to login
  }
  
  if (isLoadingData) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Loading swap details...</p>
        </div>
      </MainLayout>
    );
  }
  
  if (dataError) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8">
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{dataError}</AlertDescription>
          </Alert>
          <Button onClick={() => navigate('/items')} variant="outline">
            Back to Items
          </Button>
        </div>
      </MainLayout>
    );
  }
  
  if (!targetItem) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Item not found</p>
          <Button onClick={() => navigate('/items')} variant="outline" className="mt-4">
            Back to Items
          </Button>
        </div>
      </MainLayout>
    );
  }
  
  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigate(`/items/${targetItem.id}`)}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Item
            </Button>
            <h1 className="text-3xl font-bold">Request Swap</h1>
          </div>
          
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Target Item */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gift className="h-5 w-5" />
                  Item You Want
                </CardTitle>
                <CardDescription>Details of the item you're requesting</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {targetItem.images && targetItem.images.length > 0 && (
                  <div className="aspect-square overflow-hidden rounded-lg">
                    <img
                      src={targetItem.images[0].image_url}
                      alt={targetItem.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                
                <div>
                  <h3 className="font-semibold text-lg">{targetItem.title}</h3>
                  <p className="text-muted-foreground text-sm">{targetItem.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Category:</span>
                    <p className="capitalize">{targetItem.category}</p>
                  </div>
                  <div>
                    <span className="font-medium">Type:</span>
                    <p>{targetItem.type}</p>
                  </div>
                  <div>
                    <span className="font-medium">Size:</span>
                    <p className="uppercase">{targetItem.size}</p>
                  </div>
                  <div>
                    <span className="font-medium">Condition:</span>
                    <p>{getConditionLabel(targetItem.condition)}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Coins className="h-4 w-4 text-yellow-600" />
                  <span className="font-semibold">{targetItem.point_value} points</span>
                </div>
                
                {targetItem.tags && targetItem.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {targetItem.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Swap Options */}
            <Card>
              <CardHeader>
                <CardTitle>Swap Options</CardTitle>
                <CardDescription>Choose how you want to swap for this item</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      id="points"
                      name="swapType"
                      value="points"
                      checked={swapType === 'points'}
                      onChange={() => setSwapType('points')}
                      className="h-4 w-4"
                    />
                    <label htmlFor="points" className="flex items-center gap-2 cursor-pointer">
                      <Coins className="h-4 w-4 text-yellow-600" />
                      <span>Use Points ({targetItem.point_value} points)</span>
                    </label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      id="item"
                      name="swapType"
                      value="item"
                      checked={swapType === 'item'}
                      onChange={() => setSwapType('item')}
                      className="h-4 w-4"
                    />
                    <label htmlFor="item" className="flex items-center gap-2 cursor-pointer">
                      <Gift className="h-4 w-4 text-green-600" />
                      <span>Swap with an Item</span>
                    </label>
                  </div>
                </div>
                
                {swapType === 'points' && (
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm">
                      <strong>Your points balance:</strong> {user?.points_balance || 0} points
                    </p>
                    {user && user.points_balance < targetItem.point_value && (
                      <p className="text-sm text-red-600 mt-2">
                        You don't have enough points for this item.
                      </p>
                    )}
                  </div>
                )}
                
                {swapType === 'item' && (
                  <div className="space-y-4">
                    <Select
                      value={selectedItemId?.toString() || ''}
                      onValueChange={(value) => setSelectedItemId(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select an item to offer" />
                      </SelectTrigger>
                      <SelectContent>
                        {userItems.length === 0 ? (
                          <SelectItem value="" disabled>
                            No items available
                          </SelectItem>
                        ) : (
                          userItems.map((item) => (
                            <SelectItem key={item.id} value={item.id.toString()}>
                              {item.title} ({item.point_value} points)
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                    
                    {userItems.length === 0 && (
                      <p className="text-sm text-muted-foreground">
                        You need to list an item first to swap with items.
                      </p>
                    )}
                  </div>
                )}
                
                <div className="flex gap-4 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/items/${targetItem.id}`)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={
                      isLoading ||
                      (swapType === 'points' && user && user.points_balance < targetItem.point_value) ||
                      (swapType === 'item' && (!selectedItemId || userItems.length === 0))
                    }
                    className="flex-1"
                  >
                    {isLoading ? 'Creating Swap...' : 'Request Swap'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 