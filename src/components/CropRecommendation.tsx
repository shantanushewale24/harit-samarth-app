import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wheat, CloudRain, Thermometer, Sprout, Loader2, Droplets, Wind } from "lucide-react";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  condition: string;
  description: string;
  windSpeed: number;
  rainfall: number;
}

const CropRecommendation = () => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        // Default coordinates for agricultural region (example: Punjab, India)
        const { data, error } = await supabase.functions.invoke('get-weather', {
          body: { lat: 30.7333, lon: 76.7794 } // Chandigarh coordinates
        });

        if (error) throw error;
        setWeather(data);
      } catch (error) {
        console.error('Error fetching weather:', error);
        toast({
          title: "Weather data unavailable",
          description: "Showing recommendations based on typical seasonal conditions",
          variant: "default",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [toast]);
  const recommendedCrops = [
    {
      name: "Rice (धान)",
      season: "Kharif",
      suitability: 95,
      reason: "High soil moisture and monsoon season",
      yield: "4-5 tons/hectare",
      duration: "120-150 days"
    },
    {
      name: "Wheat (गेहूं)",
      season: "Rabi",
      suitability: 88,
      reason: "Good soil pH and winter conditions",
      yield: "3-4 tons/hectare",
      duration: "110-130 days"
    },
    {
      name: "Soybean (सोयाबीन)",
      season: "Kharif",
      suitability: 82,
      reason: "Suitable nitrogen levels",
      yield: "2-3 tons/hectare",
      duration: "90-120 days"
    }
  ];

  const getCurrentSeason = () => {
    const month = new Date().getMonth();
    if (month >= 5 && month <= 9) return "Kharif 2024";
    if (month >= 10 || month <= 2) return "Rabi 2024-25";
    return "Zaid 2024";
  };

  const conditions = weather ? [
    { icon: Thermometer, label: "Temperature", value: `${weather.temperature}°C`, color: "text-destructive" },
    { icon: Droplets, label: "Humidity", value: `${weather.humidity}%`, color: "text-sky" },
    { icon: Wind, label: "Wind Speed", value: `${weather.windSpeed} m/s`, color: "text-field" }
  ] : [
    { icon: CloudRain, label: "Rainfall", value: "Loading...", color: "text-sky" },
    { icon: Thermometer, label: "Temperature", value: "Loading...", color: "text-destructive" },
    { icon: Sprout, label: "Season", value: getCurrentSeason(), color: "text-field" }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Crop Recommendations
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            फसल सुझाव - Based on your soil health and weather conditions
          </p>
        </div>

        <div className="max-w-4xl mx-auto mb-8">
          <Card className="shadow-medium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Current Conditions
                {weather && <span className="text-sm font-normal text-muted-foreground">- {weather.location}</span>}
              </CardTitle>
              <CardDescription>
                {weather ? `${weather.condition}: ${weather.description}` : 'Environmental factors affecting crop selection'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : (
                <div className="grid md:grid-cols-3 gap-6">
                  {conditions.map((condition, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full bg-secondary flex items-center justify-center ${condition.color}`}>
                        <condition.icon className="h-6 w-6" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{condition.label}</p>
                        <p className="font-semibold text-foreground">{condition.value}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {recommendedCrops.map((crop, index) => (
            <Card key={index} className="shadow-soft hover:shadow-strong transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <Wheat className="h-8 w-8 text-primary" />
                  <Badge variant="secondary">{crop.season}</Badge>
                </div>
                <CardTitle className="text-xl">{crop.name}</CardTitle>
                <CardDescription>{crop.reason}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Suitability</span>
                      <span className="text-sm font-semibold text-primary">{crop.suitability}%</span>
                    </div>
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full transition-all duration-1000"
                        style={{ width: `${crop.suitability}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Expected Yield</p>
                      <p className="font-medium text-foreground">{crop.yield}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Duration</p>
                      <p className="font-medium text-foreground">{crop.duration}</p>
                    </div>
                  </div>

                  <Button className="w-full" variant="outline">
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CropRecommendation;