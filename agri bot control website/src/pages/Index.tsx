import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Navigation from "@/components/Navigation";
import heroImage from "@/assets/hero-robot.jpg";
import { useNavigate } from "react-router-dom";
import { 
  Sprout, 
  Camera, 
  TrendingUp, 
  Shield, 
  Clock, 
  Zap,
  CheckCircle,
  ArrowRight
} from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Camera,
      title: "AI-Powered Vision",
      description: "Advanced computer vision automatically identifies and harvests ripe vegetables"
    },
    {
      icon: TrendingUp,
      title: "Real-time Analytics",
      description: "Track harvest progress, yields, and efficiency with comprehensive dashboards"
    },
    {
      icon: Shield,
      title: "Precise Navigation",
      description: "GPS and sensor-guided movement ensures careful handling of crops"
    },
    {
      icon: Clock,
      title: "24/7 Operation",
      description: "Autonomous operation means continuous harvesting without human intervention"
    }
  ];

  const benefits = [
    "Increase harvest efficiency by 300%",
    "Reduce labor costs by up to 70%",
    "Minimize crop damage with gentle AI handling",
    "Real-time monitoring and notifications",
    "Detailed harvest reports and analytics"
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-farm-light to-background opacity-50"></div>
        <div className="container mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                  Smart Farming
                  <span className="text-primary block">Revolution</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-lg">
                  Autonomous agricultural robots that harvest vegetables with AI precision, 
                  monitor crop health, and provide real-time farming insights.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg" 
                  onClick={() => navigate("/auth")}
                  className="bg-gradient-to-r from-primary to-accent hover:shadow-lg transition-all"
                >
                  Start Farming Smart
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  onClick={() => navigate("/dashboard")}
                >
                  View Demo Dashboard
                </Button>
              </div>
            </div>
            
            <div className="relative">
              <img 
                src={heroImage} 
                alt="Smart farming robot in field" 
                className="rounded-2xl shadow-2xl w-full"
              />
              <div className="absolute -bottom-4 -right-4 bg-primary text-primary-foreground p-4 rounded-xl shadow-lg">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span className="font-semibold">300% More Efficient</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-farm-light/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Advanced Agricultural Technology
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our smart farming robots combine cutting-edge AI, computer vision, 
              and precision agriculture to revolutionize how you farm.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                  <CardHeader className="text-center">
                    <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-center">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-8">
                Why Choose AgriBot?
              </h2>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircle className="h-6 w-6 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-lg">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <Card className="p-8 bg-gradient-to-br from-primary/5 to-accent/5 border-0 shadow-lg">
              <CardHeader className="text-center pb-6">
                <Sprout className="h-12 w-12 text-primary mx-auto mb-4" />
                <CardTitle className="text-2xl">Ready to Transform Your Farm?</CardTitle>
                <CardDescription className="text-lg">
                  Join thousands of farmers who have already revolutionized their operations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  className="w-full"
                  size="lg"
                  onClick={() => navigate("/auth")}
                >
                  Get Started Today
                </Button>
                <p className="text-center text-sm text-muted-foreground">
                  No setup fees • 30-day free trial • Cancel anytime
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
