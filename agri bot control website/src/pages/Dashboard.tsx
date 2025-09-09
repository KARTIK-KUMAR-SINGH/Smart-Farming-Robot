import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import Navigation from "@/components/Navigation";
import { 
  ArrowUp, 
  ArrowDown, 
  ArrowLeft, 
  ArrowRight, 
  Play, 
  Square, 
  Camera, 
  Package, 
  AlertTriangle,
  CheckCircle,
  Loader
} from "lucide-react";

const Dashboard = () => {
  const [robotStatus, setRobotStatus] = useState<"active" | "idle" | "error">("idle");
  const [boxCapacity, setBoxCapacity] = useState(65);
  const [vegetableCounts, setVegetableCounts] = useState({
    tomatoes: 142,
    carrots: 89,
    lettuce: 76,
    peppers: 54
  });

  const handleMovement = (direction: string) => {
    setRobotStatus("active");
    console.log(`Moving robot ${direction}`);
    
    // Simulate movement completion
    setTimeout(() => {
      setRobotStatus("idle");
    }, 2000);
  };

  const getStatusIcon = () => {
    switch (robotStatus) {
      case "active":
        return <Loader className="h-4 w-4 animate-spin" />;
      case "idle":
        return <CheckCircle className="h-4 w-4" />;
      case "error":
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (robotStatus) {
      case "active":
        return "bg-sky text-white";
      case "idle":
        return "bg-primary text-primary-foreground";
      case "error":
        return "bg-destructive text-destructive-foreground";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Farm Dashboard</h1>
            <p className="text-muted-foreground">Monitor and control your smart farming robot</p>
          </div>
          <Badge className={getStatusColor()}>
            {getStatusIcon()}
            <span className="ml-1 capitalize">{robotStatus}</span>
          </Badge>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Robot Control */}
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>Robot Movement</CardTitle>
              <CardDescription>Control robot direction</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-2 max-w-48 mx-auto">
                <div></div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleMovement("forward")}
                  disabled={robotStatus === "active"}
                >
                  <ArrowUp className="h-4 w-4" />
                </Button>
                <div></div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleMovement("left")}
                  disabled={robotStatus === "active"}
                >
                  <ArrowLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleMovement("stop")}
                  disabled={robotStatus === "active"}
                >
                  <Square className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleMovement("right")}
                  disabled={robotStatus === "active"}
                >
                  <ArrowRight className="h-4 w-4" />
                </Button>
                
                <div></div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleMovement("backward")}
                  disabled={robotStatus === "active"}
                >
                  <ArrowDown className="h-4 w-4" />
                </Button>
                <div></div>
              </div>
            </CardContent>
          </Card>

          {/* Live Feed */}
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Camera className="h-5 w-5 mr-2" />
                Live Camera Feed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Camera className="h-12 w-12 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Camera feed would appear here</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Box Capacity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Package className="h-5 w-5 mr-2" />
                Box Capacity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Current Fill</span>
                    <span>{boxCapacity}%</span>
                  </div>
                  <Progress value={boxCapacity} className="h-3" />
                </div>
                {boxCapacity > 90 && (
                  <div className="flex items-center text-sm text-amber-600">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Box nearly full!
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Vegetable Counts */}
        <Card>
          <CardHeader>
            <CardTitle>Vegetable Harvest Count</CardTitle>
            <CardDescription>Today's automated harvest progress</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {Object.entries(vegetableCounts).map(([vegetable, count]) => (
                <div key={vegetable} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{vegetable}</span>
                    <span className="text-2xl font-bold text-primary">{count}</span>
                  </div>
                  <Progress value={(count / 200) * 100} className="h-2" />
                  <p className="text-xs text-muted-foreground">Target: 200</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">2 minutes ago</span>
                <span>Robot harvested 5 tomatoes</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-accent rounded-full"></div>
                <span className="text-muted-foreground">5 minutes ago</span>
                <span>Moved to section B-3</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-harvest rounded-full"></div>
                <span className="text-muted-foreground">8 minutes ago</span>
                <span>Detected ripe carrots in current area</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;