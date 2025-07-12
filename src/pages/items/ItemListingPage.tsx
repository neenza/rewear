import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '@/hooks/useRedux';
import { fetchItems } from '@/store/slices/itemsSlice';
import { Link } from 'react-router-dom';
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

export default function ItemListingPage() {
  const dispatch = useAppDispatch();
  const { items, isLoading, error, filters, pagination } = useAppSelector((state) => state.items);
  const [searchTerm, setSearchTerm] = useState(filters.searchTerm);
  const [selectedCategory, setSelectedCategory] = useState(filters.category || '');
  const [selectedSize, setSelectedSize] = useState(filters.size || '');
  const [selectedCondition, setSelectedCondition] = useState(filters.condition || '');
  
  useEffect(() => {
    loadItems();
  }, [pagination.currentPage]);
  
  const loadItems = () => {
    dispatch(fetchItems({
      page: pagination.currentPage,
      limit: pagination.limit,
      category: selectedCategory || undefined,
      size: selectedSize || undefined,
      condition: selectedCondition || undefined,
      searchTerm: searchTerm || undefined,
    }));
  };
  
  const handleSearch = () => {
    loadItems();
  };
  
  const handleFilter = () => {
    loadItems();
  };
  
  const handleNextPage = () => {
    if (pagination.currentPage < pagination.totalPages) {
      dispatch(fetchItems({
        page: pagination.currentPage + 1,
        limit: pagination.limit,
        category: selectedCategory || undefined,
        size: selectedSize || undefined,
        condition: selectedCondition || undefined,
        searchTerm: searchTerm || undefined,
      }));
    }
  };
  
  const handlePrevPage = () => {
    if (pagination.currentPage > 1) {
      dispatch(fetchItems({
        page: pagination.currentPage - 1,
        limit: pagination.limit,
        category: selectedCategory || undefined,
        size: selectedSize || undefined,
        condition: selectedCondition || undefined,
        searchTerm: searchTerm || undefined,
      }));
    }
  };
  
  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="flex flex-col space-y-4 mb-8">
          <h1 className="text-3xl font-bold">Browse Items</h1>
          
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
                  <SelectItem value="">All Categories</SelectItem>
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
                  <SelectItem value="">All Sizes</SelectItem>
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
                  <SelectItem value="">Any Condition</SelectItem>
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
              <Card className="h-full hover:shadow-lg transition-shadow">
                <div className="aspect-square overflow-hidden">
                  <img
                    src={item.images.length > 0 ? item.images.find(img => img.is_primary)?.image_url || item.images[0].image_url : 'https://via.placeholder.com/300'}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg line-clamp-1">{item.title}</CardTitle>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="flex flex-wrap gap-2 mb-2">
                    <Badge>{item.category}</Badge>
                    <Badge variant="outline">{item.size}</Badge>
                    <Badge variant="secondary">{item.condition}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">{item.description}</p>
                </CardContent>
                <CardFooter className="pt-0">
                  <div className="text-lg font-bold text-primary">{item.point_value} points</div>
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
        
        {items.length > 0 && (
          <div className="flex justify-between items-center mt-8">
            <Button
              onClick={handlePrevPage}
              disabled={pagination.currentPage === 1}
              variant="outline"
            >
              Previous
            </Button>
            
            <span>
              Page {pagination.currentPage} of {pagination.totalPages}
            </span>
            
            <Button
              onClick={handleNextPage}
              disabled={pagination.currentPage === pagination.totalPages}
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
