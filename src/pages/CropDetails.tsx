import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, ArrowLeft, Droplets, Thermometer, Wind, Sprout } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface CropProfile {
  crop: string;
  slug: string;
  vernacular?: string;
  summary?: string;
  expected_yield?: string;
  duration?: string;
  season?: string;
  soil_type?: string;
  climate_zone?: string;
  irrigation?: string;
  risks?: Record<string, string>;
  management?: string[];
  ph_range?: [number, number];
  monsoon_intensity?: string;
}

const CropDetails = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const locationState = useLocation() as { state?: { crop?: CropProfile } };
  const initialProfile = locationState?.state?.crop;
  const [profile, setProfile] = useState<CropProfile | null>(initialProfile || null);
  const [loading, setLoading] = useState(!initialProfile);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!profile && slug) {
      const controller = new AbortController();
      const fetchDetails = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await fetch(`${API_BASE_URL}/crops/details/${slug}`, {
            signal: controller.signal,
          });
          if (!response.ok) {
            const message = await response.text();
            throw new Error(message || "Unable to load crop details");
          }
          const data = await response.json();
          setProfile({ ...data, slug: data.slug || slug });
        } catch (err) {
          if ((err as Error).name === "AbortError") return;
          setError(err instanceof Error ? err.message : "Unable to load crop details");
        } finally {
          setLoading(false);
        }
      };

      fetchDetails();
      return () => controller.abort();
    }
  }, [slug, profile]);

  if (loading) {
    return (
      <section className="py-24 flex justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-3xl">
          <Alert variant="destructive">
            <AlertTitle>Unable to load crop</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button className="mt-6" variant="outline" onClick={() => navigate(-1)}>
            Go back
          </Button>
        </div>
      </section>
    );
  }

  if (!profile) {
    return null;
  }

  const displayName = profile.vernacular ? `${profile.crop} (${profile.vernacular})` : profile.crop;
  const risks = profile.risks || {};

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4 max-w-4xl space-y-6">
        <Button variant="ghost" className="w-fit flex items-center gap-2" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" /> Back to recommendations
        </Button>

        <Card className="shadow-medium">
          <CardHeader>
            <Badge variant="secondary" className="w-fit mb-2">
              {profile.season || "Seasonal"}
            </Badge>
            <CardTitle className="text-3xl">{displayName}</CardTitle>
            <CardDescription>{profile.summary}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="flex items-center gap-3">
                <Thermometer className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Duration</p>
                  <p className="text-foreground font-semibold">{profile.duration || "—"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Droplets className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Expected Yield</p>
                  <p className="text-foreground font-semibold">{profile.expected_yield || "—"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Wind className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Irrigation</p>
                  <p className="text-foreground font-semibold">{profile.irrigation || "Adaptive"}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sprout className="h-5 w-5" /> Agronomy snapshot
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Soil type</span>
                <span className="font-medium">{profile.soil_type || "Well-drained"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Climate zone</span>
                <span className="font-medium">{profile.climate_zone || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">pH range</span>
                <span className="font-medium">
                  {profile.ph_range ? `${profile.ph_range[0]} - ${profile.ph_range[1]}` : "6.0 - 7.5"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Monsoon intensity</span>
                <span className="font-medium">{profile.monsoon_intensity || "Moderate"}</span>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle>Risk profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {Object.keys(risks).length ? (
                Object.entries(risks).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-muted-foreground capitalize">{key} risk</span>
                    <span className="font-medium">{value || "Moderate"}</span>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">Risk profile will appear once available.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {profile.management && profile.management.length > 0 && (
          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle>Cultivation checklist</CardTitle>
              <CardDescription>Practical field actions suggested for this crop</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-6 space-y-2 text-sm text-foreground">
                {profile.management.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </section>
  );
};

export default CropDetails;
