import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Wheat, CloudRain, Thermometer, Sprout, Loader2, Droplets, Wind, MapPin } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  condition?: string;
  description?: string;
  windSpeed: number;
  rainfall: number;
  last_updated?: string;
}

interface CropRecommendationItem {
  name: string;
  vernacular?: string;
  season?: string;
  summary?: string;
  expectedYield?: string;
  duration?: string;
  suitability: number;
  slug: string;
}

const fallbackCrops: CropRecommendationItem[] = [
  {
    name: "Rice",
    vernacular: "धान",
    season: "Kharif",
    summary: "High soil moisture and monsoon season",
    expectedYield: "4-5 tons/hectare",
    duration: "120-150 days",
    suitability: 95,
    slug: "rice"
  },
  {
    name: "Wheat",
    vernacular: "गेहूं",
    season: "Rabi",
    summary: "Good soil pH and winter conditions",
    expectedYield: "3-4 tons/hectare",
    duration: "110-130 days",
    suitability: 88,
    slug: "wheat"
  },
  {
    name: "Soybean",
    vernacular: "सोयाबीन",
    season: "Kharif",
    summary: "Suitable nitrogen levels",
    expectedYield: "2-3 tons/hectare",
    duration: "90-120 days",
    suitability: 82,
    slug: "soybean"
  }
];

const slugify = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

const CropRecommendation = () => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [recommendations, setRecommendations] = useState<CropRecommendationItem[]>(fallbackCrops);
  const [locationInput, setLocationInput] = useState("Chandigarh");
  const [activeLocation, setActiveLocation] = useState("Chandigarh");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  const fetchRecommendations = useCallback(async (location: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/crops/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location })
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Unable to fetch recommendations");
      }

      const data = await response.json();
      setWeather(data.weather || null);

      if (Array.isArray(data.recommendations) && data.recommendations.length > 0) {
        const mapped = data.recommendations.map((item: any) => ({
          name: item.crop,
          vernacular: item.vernacular,
          season: item.season,
          summary: item.summary,
          expectedYield: item.expected_yield,
          duration: item.duration,
          suitability: item.suitability ?? Math.round((item.probability ?? 0) * 100),
          slug: item.slug || slugify(item.crop)
        }));
        setRecommendations(mapped);
      } else {
        setRecommendations(fallbackCrops);
        toast({
          title: "Showing fallback recommendations",
          description: "ML model returned no matches. Displaying seasonal defaults.",
        });
      }
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Unable to fetch recommendations");
      setRecommendations(fallbackCrops);
      setWeather(null);
      toast({
        title: "Using seasonal defaults",
        description: "Live recommendations are unavailable right now.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchRecommendations(activeLocation);
  }, [activeLocation, fetchRecommendations]);

  const handleLocationSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = locationInput.trim();
    if (!trimmed) {
      toast({
        title: "Enter a location",
        description: "Please add your village, town, or district to personalize recommendations.",
        variant: "destructive",
      });
      return;
    }
    setActiveLocation(trimmed);
  };

  const activeRecommendations = recommendations.length ? recommendations : fallbackCrops;

  const getCurrentSeason = () => {
    const month = new Date().getMonth();
    if (month >= 5 && month <= 9) return "Kharif";
    if (month >= 10 || month <= 2) return "Rabi";
    return "Zaid";
  };

  const conditions = weather ? [
    { icon: Thermometer, label: "Temperature", value: `${weather.temperature?.toFixed(1)}°C`, color: "text-destructive" },
    { icon: Droplets, label: "Humidity", value: `${weather.humidity}%`, color: "text-sky" },
    { icon: Wind, label: "Wind Speed", value: `${weather.windSpeed} m/s`, color: "text-field" }
  ] : [
    { icon: CloudRain, label: "Rainfall", value: "Fetching...", color: "text-sky" },
    { icon: Thermometer, label: "Temperature", value: "Fetching...", color: "text-destructive" },
    { icon: Sprout, label: "Season", value: getCurrentSeason(), color: "text-field" }
  ];

  return (
    <section id="crops" className="py-16 bg-background">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Crop Recommendations
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            फसल सुझाव - Based on your soil health and weather conditions
          </p>
        </div>

        <div className="max-w-4xl mx-auto mb-8 space-y-4">
          <form onSubmit={handleLocationSubmit} className="flex flex-col md:flex-row items-center gap-3">
            <div className="flex-1 w-full">
              <Input
                value={locationInput}
                onChange={(event) => setLocationInput(event.target.value)}
                placeholder="Enter your village, town, or district"
                className="h-12"
              />
            </div>
            <Button type="submit" className="w-full md:w-auto h-12 min-w-[150px]" disabled={loading}>
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" /> Updating...
                </span>
              ) : (
                "Update location"
              )}
            </Button>
          </form>

          {error && (
            <Alert variant="destructive">
              <AlertTitle>Weather unavailable</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Card className="shadow-medium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Current Conditions
                {weather && (
                  <span className="text-sm font-normal text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-4 w-4" /> {weather.location}
                  </span>
                )}
              </CardTitle>
              <CardDescription>
                {weather ? `${weather.condition || ""} ${weather.description || ""}` : 'Environmental factors affecting crop selection'}
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
          {activeRecommendations.map((crop, index) => (
            <Card key={index} className="shadow-soft hover:shadow-strong transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <Wheat className="h-8 w-8 text-primary" />
                  <Badge variant="secondary">{crop.season || getCurrentSeason()}</Badge>
                </div>
                <CardTitle className="text-xl">
                  {crop.vernacular ? `${crop.name} (${crop.vernacular})` : crop.name}
                </CardTitle>
                <CardDescription>{crop.summary}</CardDescription>
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
                      <p className="font-medium text-foreground">{crop.expectedYield || '—'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Duration</p>
                      <p className="font-medium text-foreground">{crop.duration || '—'}</p>
                    </div>
                  </div>

                  <Button className="w-full" variant="outline" onClick={() => navigate(`/crops/${crop.slug}`, { state: { crop } })}>
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