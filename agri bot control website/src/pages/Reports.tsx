import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Navigation from "@/components/Navigation";
import { Download, Calendar, TrendingUp, Package } from "lucide-react";

const Reports = () => {
  const dailyData = [
    { date: "2024-01-15", tomatoes: 142, carrots: 89, lettuce: 76, peppers: 54 },
    { date: "2024-01-14", tomatoes: 138, carrots: 92, lettuce: 81, peppers: 48 },
    { date: "2024-01-13", tomatoes: 156, carrots: 87, lettuce: 73, peppers: 61 },
    { date: "2024-01-12", tomatoes: 134, carrots: 95, lettuce: 88, peppers: 52 },
    { date: "2024-01-11", tomatoes: 149, carrots: 91, lettuce: 79, peppers: 57 },
  ];

  const weeklyTotals = {
    tomatoes: 719,
    carrots: 454,
    lettuce: 397,
    peppers: 272
  };

  const handleExportCSV = () => {
    console.log("Exporting CSV...");
    // CSV export logic would go here
  };

  const handleExportPDF = () => {
    console.log("Exporting PDF...");
    // PDF export logic would go here
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Harvest Reports</h1>
            <p className="text-muted-foreground">Analyze your farming data and export reports</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleExportCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button onClick={handleExportPDF}>
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </div>

        <Tabs defaultValue="daily" className="space-y-6">
          <TabsList>
            <TabsTrigger value="daily">Daily Reports</TabsTrigger>
            <TabsTrigger value="weekly">Weekly Summary</TabsTrigger>
            <TabsTrigger value="monthly">Monthly Overview</TabsTrigger>
          </TabsList>

          <TabsContent value="daily" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Today's Total</CardTitle>
                  <Package className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">361</div>
                  <p className="text-xs text-muted-foreground">
                    +12% from yesterday
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Top Performer</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Tomatoes</div>
                  <p className="text-xs text-muted-foreground">
                    142 harvested today
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Efficiency</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">94%</div>
                  <p className="text-xs text-muted-foreground">
                    Robot uptime today
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">4.5h</div>
                  <p className="text-xs text-muted-foreground">
                    vs manual harvesting
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Daily Harvest History</CardTitle>
                <CardDescription>Last 5 days of harvest data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dailyData.map((day, index) => (
                    <div key={day.date} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="font-medium">{new Date(day.date).toLocaleDateString()}</div>
                      <div className="flex space-x-6 text-sm">
                        <span>🍅 {day.tomatoes}</span>
                        <span>🥕 {day.carrots}</span>
                        <span>🥬 {day.lettuce}</span>
                        <span>🌶️ {day.peppers}</span>
                        <span className="font-medium">Total: {day.tomatoes + day.carrots + day.lettuce + day.peppers}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="weekly" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Weekly Summary</CardTitle>
                <CardDescription>January 11-15, 2024</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {Object.entries(weeklyTotals).map(([vegetable, total]) => (
                    <div key={vegetable} className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-primary">{total}</div>
                      <div className="text-sm text-muted-foreground capitalize">{vegetable}</div>
                      <div className="text-xs text-muted-foreground">
                        Avg: {Math.round(total / 5)}/day
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="monthly" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Overview</CardTitle>
                <CardDescription>January 2024</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Monthly reports will be available after the full month completes.</p>
                  <p className="text-sm text-muted-foreground mt-2">Current progress: 50% of month completed</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Reports;