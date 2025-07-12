import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/hooks/useRedux';
import MainLayout from '@/layouts/MainLayout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getCurrentUser } from '@/store/slices/authSlice';
import axios from 'axios';

export default function DashboardPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading } = useAppSelector((state) => state.auth);
  const [activeTab, setActiveTab] = useState('overview');
  const [myItems, setMyItems] = useState<any[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [itemsError, setItemsError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    dispatch(getCurrentUser());
  }, [dispatch, isAuthenticated, navigate]);

  useEffect(() => {
    const fetchMyItems = async () => {
      if (!isAuthenticated) return;
      setItemsLoading(true);
      setItemsError(null);
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/items/my-items', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setMyItems(response.data.items || []);
      } catch (err: any) {
        setItemsError(err.response?.data?.detail || 'Failed to load your items.');
      } finally {
        setItemsLoading(false);
      }
    };
    fetchMyItems();
  }, [isAuthenticated]);

  if (isLoading) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Loading dashboard...</p>
        </div>
      </MainLayout>
    );
  }

  if (!user) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 text-center">
          <p className="text-xl">Please log in to view your dashboard</p>
          <Button 
            onClick={() => navigate('/login')} 
            className="mt-4"
          >
            Login
          </Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Manage your items, swaps, and account</p>
          </div>
          <div className="mt-4 md:mt-0">
            <Link to="/items/new">
              <Button>List New Item</Button>
            </Link>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle>Points Balance</CardTitle>
              <CardDescription>Your current reward points</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-primary">{user.points_balance}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle>My Items</CardTitle>
              <CardDescription>Items you have listed</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{myItems.length}</p>
            </CardContent>
            <CardFooter>
              <Link to="/dashboard/items">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </CardFooter>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle>Active Swaps</CardTitle>
              <CardDescription>Pending swap requests</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">0</p>
            </CardContent>
            <CardFooter>
              <Link to="/dashboard/swaps">
                <Button variant="outline" size="sm">View All</Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="items">My Items</TabsTrigger>
            <TabsTrigger value="swaps">My Swaps</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No recent activity</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 gap-4">
                  <Link to="/items/new">
                    <Card className="hover:bg-muted transition-colors">
                      <CardContent className="flex items-center p-4">
                        <div>
                          <h3 className="font-medium">List a New Item</h3>
                          <p className="text-sm text-muted-foreground">Add a new item to your listings</p>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                  <Link to="/items">
                    <Card className="hover:bg-muted transition-colors">
                      <CardContent className="flex items-center p-4">
                        <div>
                          <h3 className="font-medium">Browse Items</h3>
                          <p className="text-sm text-muted-foreground">Find items to swap</p>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                  <Link to="/dashboard/profile">
                    <Card className="hover:bg-muted transition-colors">
                      <CardContent className="flex items-center p-4">
                        <div>
                          <h3 className="font-medium">Edit Profile</h3>
                          <p className="text-sm text-muted-foreground">Update your profile details</p>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                </div>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="items" className="pt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">My Items</h2>
              <Link to="/items/new">
                <Button>List New Item</Button>
              </Link>
            </div>
            {itemsLoading ? (
              <div className="text-center py-12">
                <p className="text-xl mb-2">Loading your items...</p>
              </div>
            ) : itemsError ? (
              <div className="text-center py-12">
                <Alert variant="destructive" className="mb-6">
                  <AlertDescription>{itemsError}</AlertDescription>
                </Alert>
              </div>
            ) : myItems.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-xl mb-2">No items listed yet</p>
                <p className="text-muted-foreground mb-6">Start listing your items for others to discover</p>
                <Link to="/items/new">
                  <Button>List Your First Item</Button>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myItems.map((item) => (
                  <Card key={item.id}>
                    <CardHeader>
                      <CardTitle>{item.title}</CardTitle>
                      <CardDescription>{item.category} &middot; {item.size} &middot; {item.condition}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {item.images && item.images.length > 0 && (
                        <img
                          src={item.images[0].image_url}
                          alt={item.title}
                          className="w-full h-40 object-cover rounded mb-2"
                        />
                      )}
                      <p className="text-sm text-muted-foreground mb-2">{item.description}</p>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {item.tags && item.tags.map((tag: string, idx: number) => (
                          <Badge key={idx} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                      <div className="text-sm font-medium">Points: {item.point_value}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
          <TabsContent value="swaps" className="pt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">My Swaps</h2>
            </div>
            <div className="text-center py-12">
              <p className="text-xl mb-2">No swap requests</p>
              <p className="text-muted-foreground mb-6">Browse items to find something you like and initiate a swap</p>
              <Link to="/items">
                <Button>Browse Items</Button>
              </Link>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
