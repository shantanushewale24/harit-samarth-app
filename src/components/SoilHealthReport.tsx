import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Activity, Droplets, Leaf, TrendingUp } from "lucide-react";

const SoilHealthReport = () => {
  const soilHealthIndex = 72; // Example value

  const getHealthColor = (value: number) => {
    if (value >= 70) return "bg-field";
    if (value >= 40) return "bg-harvest";
    return "bg-destructive";
  };

  const recommendations = [
    {
      icon: Leaf,
      title: "Organic Matter",
      description: "Apply compost or vermicompost to improve soil structure",
      action: "Add 5-10 tons per hectare"
    },
    {
      icon: Droplets,
      title: "Water Retention",
      description: "Good moisture levels detected",
      action: "Maintain current irrigation schedule"
    },
    {
      icon: Activity,
      title: "Microbial Activity",
      description: "Enhance beneficial microbes with biofertilizers",
      action: "Apply Rhizobium or Azotobacter"
    }
  ];

  return (
    <section className="py-16 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Soil Health Report
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            मिट्टी की सेहत रिपोर्ट - Understand your soil's biological health and get actionable recommendations
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <Card className="shadow-medium hover:shadow-strong transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                Soil Biological Health Index
              </CardTitle>
              <CardDescription>Current soil health status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-3xl font-bold text-foreground">{soilHealthIndex}</span>
                    <span className="text-sm font-medium text-muted-foreground">out of 100</span>
                  </div>
                  <Progress value={soilHealthIndex} className="h-3" />
                  <p className="text-sm text-muted-foreground mt-2">
                    {soilHealthIndex >= 70 ? "Good" : soilHealthIndex >= 40 ? "Moderate" : "Needs Improvement"}
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                  <div>
                    <p className="text-xs text-muted-foreground">pH Level</p>
                    <p className="text-lg font-semibold text-foreground">6.5</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">N-P-K</p>
                    <p className="text-lg font-semibold text-foreground">240:45:180</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Organic %</p>
                    <p className="text-lg font-semibold text-foreground">2.8%</p>
                  </div>
                </div>

                <Button className="w-full" variant="default">
                  View Detailed Report
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-foreground mb-4">Practical Actions</h3>
            {recommendations.map((rec, index) => (
              <Card key={index} className="shadow-soft hover:shadow-medium transition-all duration-300">
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <rec.icon className="h-6 w-6 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground mb-1">{rec.title}</h4>
                      <p className="text-sm text-muted-foreground mb-2">{rec.description}</p>
                      <p className="text-sm font-medium text-primary">{rec.action}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default SoilHealthReport;