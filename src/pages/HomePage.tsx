import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '@/hooks/useRedux';
import MainLayout from '@/layouts/MainLayout';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  
  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="relative bg-gradient-warm py-24 overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
        <div className="absolute top-10 left-10 w-32 h-32 bg-primary/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-40 h-40 bg-accent/10 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto px-4 text-center relative z-10">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gradient">
            Sustainable Fashion Exchange
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto leading-relaxed">
            Give your clothes a second life and refresh your wardrobe through our
            community-driven fashion exchange platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Button 
              size="lg" 
              className="bg-gradient-primary hover:shadow-warm-lg hover-lift text-lg px-8 py-4"
              onClick={() => navigate('/items')}
            >
              Browse Items
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-2 border-primary/30 hover:bg-primary/10 hover-lift text-lg px-8 py-4"
              onClick={() => navigate(isAuthenticated ? '/items/new' : '/register')}
            >
              {isAuthenticated ? 'List an Item' : 'Join Now'}
            </Button>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">List Your Items</h3>
              <p className="text-muted-foreground">
                Take photos of clothing you no longer wear and list them on our platform.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Earn Points</h3>
              <p className="text-muted-foreground">
                When your items are approved, you'll receive points that you can use to get other items.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Swap & Enjoy</h3>
              <p className="text-muted-foreground">
                Use your points to request items from other members and refresh your wardrobe sustainably.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Why ReWear?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-background p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-3">Sustainable</h3>
              <p className="text-muted-foreground">
                Reduce fashion waste by giving clothes a second life instead of sending them to landfills.
              </p>
            </div>
            <div className="bg-background p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-3">Community-Driven</h3>
              <p className="text-muted-foreground">
                Connect with like-minded individuals who value sustainability and fashion.
              </p>
            </div>
            <div className="bg-background p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-3">Cost-Effective</h3>
              <p className="text-muted-foreground">
                Refresh your wardrobe without spending money on new clothes.
              </p>
            </div>
            <div className="bg-background p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-3">Quality Control</h3>
              <p className="text-muted-foreground">
                All items are reviewed before listing to ensure they meet our quality standards.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Join the Sustainable Fashion Movement?</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Start swapping today and be part of the solution to fashion waste.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
            >
              {isAuthenticated ? 'Go to Dashboard' : 'Sign Up Now'}
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => navigate('/items')}
            >
              Browse Collection
            </Button>
          </div>
        </div>
      </section>
    </MainLayout>
  );
}
