import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";
import { Sprout, BarChart3, Settings, LogOut } from "lucide-react";

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Home", icon: Sprout },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    { path: "/reports", label: "Reports", icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex items-center space-x-2">
          <Sprout className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">AgriBot</span>
        </div>
        
        <nav className="flex items-center space-x-6 text-sm font-medium">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex items-center space-x-2 transition-colors hover:text-foreground/80 ${
                  location.pathname === item.path
                    ? "text-foreground"
                    : "text-foreground/60"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/auth")}
          >
            Login
          </Button>
          <Button
            size="sm"
            onClick={() => navigate("/auth")}
          >
            Sign Up
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Navigation;