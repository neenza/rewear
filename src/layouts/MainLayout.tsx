import { ReactNode, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAppDispatch, useAppSelector } from '@/hooks/useRedux';
import { getCurrentUser, logout } from '@/store/slices/authSlice';

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, isAuthenticated]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('');
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold">ReWear</span>
            </Link>
            <nav className="hidden md:flex gap-6">
              <Link to="/" className="text-sm font-medium transition-colors hover:text-primary">
                Home
              </Link>
              <Link to="/items" className="text-sm font-medium transition-colors hover:text-primary">
                Browse Items
              </Link>
              {isAuthenticated && (
                <Link to="/items/new" className="text-sm font-medium transition-colors hover:text-primary">
                  List an Item
                </Link>
              )}
              {isAuthenticated && user?.role === 'admin' && (
                <Link to="/admin" className="text-sm font-medium transition-colors hover:text-primary">
                  Admin
                </Link>
              )}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user?.profile_picture} alt={user?.username} />
                      <AvatarFallback>{user?.username ? getInitials(user.username) : 'U'}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <div className="flex flex-col space-y-1 p-2">
                    <p className="text-sm font-medium">{user?.username}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                    <p className="text-xs text-muted-foreground">Points: {user?.points_balance}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/dashboard">Dashboard</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/profile">Profile</Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>Log out</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex gap-2">
                <Button variant="ghost" asChild>
                  <Link to="/login">Login</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">Sign Up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t">
        <div className="container flex flex-col gap-4 py-10 md:flex-row md:justify-between">
          <div>
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold">ReWear</span>
            </Link>
            <p className="mt-2 text-sm text-muted-foreground">
              Sustainable fashion exchange platform
              <br />
              &copy; {new Date().getFullYear()} ReWear. All rights reserved.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-medium">Platform</h4>
              <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
                Home
              </Link>
              <Link to="/browse" className="text-sm text-muted-foreground hover:text-foreground">
                Browse Items
              </Link>
              <Link to="/about" className="text-sm text-muted-foreground hover:text-foreground">
                About Us
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-medium">Help</h4>
              <Link to="/faq" className="text-sm text-muted-foreground hover:text-foreground">
                FAQ
              </Link>
              <Link to="/contact" className="text-sm text-muted-foreground hover:text-foreground">
                Contact
              </Link>
              <Link to="/terms" className="text-sm text-muted-foreground hover:text-foreground">
                Terms
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-medium">Social</h4>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noreferrer"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Twitter
              </a>
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noreferrer"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Instagram
              </a>
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noreferrer"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Facebook
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
