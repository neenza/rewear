import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/hooks/useRedux';
import { fetchItemById } from '@/store/slices/itemsSlice';
import MainLayout from '@/layouts/MainLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { selectedItem, isLoading, error } = useAppSelector((state) => state.items);
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);
  const [activeTab, setActiveTab] = useState('details');
  
  useEffect(() => {
    if (id) {
      dispatch(fetchItemById(parseInt(id)));
    }
  }, [dispatch, id]);
  
  if (isLoading) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Loading item details...</p>
        </div>
      </MainLayout>
    );
  }
  
  if (error) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8">
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button 
            onClick={() => navigate('/items')} 
            variant="outline" 
            className="mt-4"
          >
            Back to Items
          </Button>
        </div>
      </MainLayout>
    );
  }
  
  if (!selectedItem) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Item not found</p>
          <Button 
            onClick={() => navigate('/items')} 
            variant="outline" 
            className="mt-4"
          >
            Back to Items
          </Button>
        </div>
      </MainLayout>
    );
  }
  
  const handleInitiateSwap = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    navigate(`/swaps/new?item_id=${selectedItem.id}`);
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
  
  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Image Gallery */}
          <div>
            <Carousel className="w-full">
              <CarouselContent>
                {selectedItem.images.length > 0 ? (
                  selectedItem.images.map((image) => (
                    <CarouselItem key={image.id}>
                      <div className="aspect-square w-full rounded-md overflow-hidden">
                        <img
                          src={image.image_url}
                          alt={selectedItem.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </CarouselItem>
                  ))
                ) : (
                  <CarouselItem>
                    <div className="aspect-square w-full rounded-md overflow-hidden bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-500">No images available</span>
                    </div>
                  </CarouselItem>
                )}
              </CarouselContent>
              {selectedItem.images.length > 1 && (
                <>
                  <CarouselPrevious />
                  <CarouselNext />
                </>
              )}
            </Carousel>
            
            {selectedItem.images.length > 1 && (
              <div className="flex mt-4 gap-2 overflow-x-auto pb-2">
                {selectedItem.images.map((image) => (
                  <div
                    key={image.id}
                    className="w-20 h-20 shrink-0 rounded-md overflow-hidden border-2 border-primary-50 hover:border-primary cursor-pointer"
                  >
                    <img
                      src={image.image_url}
                      alt={selectedItem.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Item Details */}
          <div>
            <h1 className="text-3xl font-bold mb-2">{selectedItem.title}</h1>
            
            <div className="flex items-center space-x-2 mb-4">
              <Avatar className="h-8 w-8">
                <AvatarImage src={selectedItem.user.profile_picture} />
                <AvatarFallback>{selectedItem.user.username.charAt(0).toUpperCase()}</AvatarFallback>
              </Avatar>
              <span className="text-sm text-muted-foreground">
                Listed by <span className="font-medium">{selectedItem.user.username}</span>
              </span>
            </div>
            
            <div className="text-2xl font-bold text-primary mb-6">
              {selectedItem.point_value} points
            </div>
            
            <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="description">Description</TabsTrigger>
                <TabsTrigger value="shipping">Shipping</TabsTrigger>
              </TabsList>
              <TabsContent value="details" className="pt-4">
                <div className="grid grid-cols-2 gap-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Category</p>
                    <p className="font-medium capitalize">{selectedItem.category}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Type</p>
                    <p className="font-medium capitalize">{selectedItem.type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Size</p>
                    <p className="font-medium uppercase">{selectedItem.size}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Condition</p>
                    <p className="font-medium">{getConditionLabel(selectedItem.condition)}</p>
                  </div>
                </div>
                
                {selectedItem.tags.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-muted-foreground mb-2">Tags</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedItem.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary">{tag}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="description" className="pt-4">
                <p className="whitespace-pre-wrap">{selectedItem.description}</p>
              </TabsContent>
              <TabsContent value="shipping" className="pt-4">
                <p>Shipping is arranged between members after a swap is confirmed.</p>
                <p className="mt-2">Please ensure you review our shipping guidelines before proceeding with any swap.</p>
              </TabsContent>
            </Tabs>
            
            <div className="flex flex-col gap-4">
              <Button 
                onClick={handleInitiateSwap} 
                size="lg" 
                disabled={selectedItem.user_id === user?.id}
              >
                {selectedItem.user_id === user?.id ? 'Your Item' : 'Request Swap'}
              </Button>
              
              {selectedItem.user_id === user?.id && (
                <div className="text-sm text-muted-foreground text-center">
                  You can't swap your own item
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
