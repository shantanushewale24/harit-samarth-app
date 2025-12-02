import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, Droplets, Leaf, TrendingUp, AlertCircle, CheckCircle2, XCircle, RefreshCw, Clock, BookOpen, Zap, Microscope } from "lucide-react";
import { useState, useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const SoilHealthReport = () => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(60);
  const [activeTab, setActiveTab] = useState("overview");
  const [microbialHealth, setMicrobialHealth] = useState(0);

  // Calculate microbial health based on CO2 influx
  const calculateMicrobialHealth = (co2: number) => {
    // Optimal CO2: 400-600 ppm
    // Microbial health based on respiration rate (CO2)
    if (co2 < 350 || co2 > 750) {
      return Math.max(20, 100 - Math.abs(co2 - 500) / 5); // Low microbial activity
    }
    if (co2 >= 450 && co2 <= 550) {
      return 95; // Excellent microbial activity
    }
    return 75; // Good microbial activity
  };

  // Fetch latest soil health analysis from backend
  const fetchLatestAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
      const response = await fetch(`${apiUrl}/soil-health/latest`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
      
      // Calculate microbial health from CO2
      if (data.sensor_readings?.CO2) {
        const microbial = calculateMicrobialHealth(data.sensor_readings.CO2);
        setMicrobialHealth(Math.round(microbial));
      }
      
      setCountdown(60);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch soil analysis");
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Countdown timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          fetchLatestAnalysis(); // Auto-refresh when countdown reaches 0
          return 60;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Load analysis on component mount
  useEffect(() => {
    fetchLatestAnalysis();
  }, []);

  // Educational content about soil parameters
  const educationalContent = {
    pH: {
      title: "pH Level (Soil Acidity)",
      icon: Zap,
      benefits: [
        "Optimal Range: 6.5 - 7.5",
        "Controls nutrient availability to plants",
        "Affects microbial activity and diversity",
        "Influences pesticide effectiveness"
      ],
      why: "pH determines how available nutrients like nitrogen, phosphorus, and potassium are to your crops. Too acidic or alkaline soil reduces nutrient absorption.",
      tips: [
        "• Test soil pH annually",
        "• Add lime to raise pH (increase alkalinity)",
        "• Add sulfur to lower pH (increase acidity)",
        "• Most crops prefer slightly acidic to neutral pH"
      ]
    },
    Nitrogen: {
      title: "Nitrogen (N)",
      icon: Leaf,
      benefits: [
        "Essential for plant protein synthesis",
        "Promotes leaf and stem growth",
        "Improves crop yield significantly",
        "Key component of chlorophyll"
      ],
      why: "Nitrogen is crucial for photosynthesis and plant growth. It's the most commonly deficient nutrient in farms and directly impacts crop productivity.",
      tips: [
        "• Normal Range: 15-30 ppm",
        "• Deficiency signs: Yellowing leaves",
        "• Legumes naturally fix atmospheric nitrogen",
        "• Use compost or nitrogen fertilizers for supplementation"
      ]
    },
    Phosphorus: {
      title: "Phosphorus (P)",
      icon: TrendingUp,
      benefits: [
        "Strengthens root development",
        "Enhances flower and fruit formation",
        "Improves disease resistance",
        "Boosts energy transfer in plants"
      ],
      why: "Phosphorus is vital for root growth and energy metabolism. It helps plants resist stress and improves flowering and fruiting.",
      tips: [
        "• Normal Range: 10-25 ppm",
        "• Deficiency signs: Purple-red leaf discoloration",
        "• Bone meal is rich in phosphorus",
        "• Less mobile in soil - place near roots"
      ]
    },
    Potassium: {
      title: "Potassium (K)",
      icon: Activity,
      benefits: [
        "Regulates water uptake and retention",
        "Improves disease and drought resistance",
        "Enhances fruit quality and flavor",
        "Strengthens cell walls"
      ],
      why: "Potassium improves plant's ability to withstand stress, increases disease resistance, and enhances fruit quality and shelf life.",
      tips: [
        "• Normal Range: 100-200 ppm",
        "• Deficiency signs: Leaf margins browning",
        "• Wood ash is a natural potassium source",
        "• Essential for fruit and vegetable crops"
      ]
    },
    Moisture: {
      title: "Soil Moisture",
      icon: Droplets,
      benefits: [
        "Dissolves nutrients for plant uptake",
        "Regulates soil temperature",
        "Provides hydraulic support to plants",
        "Essential for seed germination"
      ],
      why: "Water is the medium through which plants absorb nutrients. Proper moisture balance prevents both drought stress and waterlogging.",
      tips: [
        "• Optimal Range: 40-60%",
        "• Too dry: Plant wilting, poor germination",
        "• Too wet: Root rot, fungal diseases",
        "• Check moisture 2-3 inches into soil"
      ]
    },
    Temperature: {
      title: "Soil Temperature",
      icon: TrendingUp,
      benefits: [
        "Controls microbial activity rate",
        "Affects nutrient availability",
        "Influences seed germination",
        "Impacts plant growth rate"
      ],
      why: "Soil temperature controls microbial populations and enzymatic reactions. Different crops have different optimal temperature ranges.",
      tips: [
        "• Optimal Range: 15-25°C",
        "• Microbes most active at 20-25°C",
        "• Too cold: Slow nutrient cycling",
        "• Too hot: Nutrient loss and water evaporation"
      ]
    },
    Microbial: {
      title: "Microbial Health (CO2 Respiration)",
      icon: Microscope,
      benefits: [
        "Indicates active soil microorganisms",
        "Shows nutrient cycling efficiency",
        "Reflects organic matter decomposition",
        "Predicts soil fertility and health"
      ],
      why: "Soil microbes are essential for nutrient cycling, disease suppression, and soil structure. CO2 influx (respiration) indicates microbial activity levels.",
      tips: [
        "• Healthy Range: 450-550 ppm CO2",
        "• Higher CO2 = more microbial activity",
        "• Add compost to boost microbial populations",
        "• Avoid excessive tilling - it kills microbes",
        "• Crop rotation maintains microbial diversity"
      ]
    },
    CO2: {
      title: "CO2 Level (Microbial Respiration)",
      icon: Zap,
      benefits: [
        "Indicates soil biological activity",
        "Shows decomposition rate of organic matter",
        "Reflects microbial population size",
        "Predicts soil health and fertility"
      ],
      why: "CO2 is produced by microbes as they decompose organic matter. Higher CO2 indicates more active, healthier soil biology.",
      tips: [
        "• Optimal Range: 400-600 ppm",
        "• Low CO2: Few microbes, infertile soil",
        "• High CO2: Very active microbes, rich soil",
        "• Organic matter boosts CO2 production",
        "• Measure regularly for soil health trends"
      ]
    }
  };

  const getHealthStatus = (value: number) => {
    if (value >= 70) return { text: "Excellent", color: "text-green-600", bg: "bg-green-50" };
    if (value >= 50) return { text: "Good", color: "text-blue-600", bg: "bg-blue-50" };
    if (value >= 30) return { text: "Fair", color: "text-yellow-600", bg: "bg-yellow-50" };
    return { text: "Poor", color: "text-red-600", bg: "bg-red-50" };
  };

  const sensorReadings = analysis?.sensor_readings || {};
  const lastUpdate = analysis?.timestamp ? new Date(analysis.timestamp).toLocaleTimeString() : "Loading...";

  const ChartComponent = ({ title, value, max = 100, unit = "", status }: any) => (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <p className="text-sm font-semibold text-foreground">{title}</p>
        <p className="text-lg font-bold text-primary">{value}{unit}</p>
      </div>
      <Progress value={(value / max) * 100} className="h-3" />
      <p className="text-xs text-muted-foreground">{status}</p>
    </div>
  );

  return (
    <section className="py-16 bg-secondary/30" id="soil">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Soil Health Dashboard
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            मिट्टी की सेहत - Real-time soil analysis with educational insights
          </p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Countdown Timer Card */}
        <Card className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Clock className="h-6 w-6 text-blue-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Next Reading In</p>
                  <p className="text-2xl font-bold text-blue-600">{countdown}s</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Last Update</p>
                <p className="text-lg font-semibold text-foreground">{lastUpdate}</p>
              </div>
              <Button 
                onClick={fetchLatestAnalysis}
                disabled={loading}
                variant="outline"
                size="sm"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
            <Progress value={(countdown / 60) * 100} className="mt-4 h-2" />
          </CardContent>
        </Card>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="education">Learn</TabsTrigger>
            <TabsTrigger value="microbial">Microbial</TabsTrigger>
            <TabsTrigger value="metrics" className="hidden lg:block">Metrics</TabsTrigger>
            <TabsTrigger value="recommendations" className="hidden lg:block">Tips</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Health Index Card */}
              <Card className="shadow-medium">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Overall Health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-4xl font-bold text-primary">
                        {analysis?.soil_health_index || 0}/100
                      </p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Status: {analysis?.health_status || "Loading..."}
                      </p>
                    </div>
                    <Progress value={analysis?.soil_health_index || 0} className="h-3" />
                    {analysis?.is_anomalous && (
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>Anomaly detected</AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Microbial Health Card */}
              <Card className="shadow-medium bg-gradient-to-br from-emerald-50 to-teal-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Microscope className="h-5 w-5 text-emerald-600" />
                    Microbial Health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-4xl font-bold text-emerald-600">
                        {microbialHealth}/100
                      </p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Based on CO2: {sensorReadings.CO2 || "-"} ppm
                      </p>
                    </div>
                    <Progress value={microbialHealth} className="h-3" />
                    <p className="text-xs text-emerald-700 font-semibold">
                      {microbialHealth >= 80 ? "🟢 Excellent Microbial Activity" : 
                       microbialHealth >= 60 ? "🟡 Good Microbial Activity" :
                       "🔴 Needs Improvement"}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Status Card */}
              <Card className="shadow-medium">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    Quick Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Anomalous</span>
                      {analysis?.is_anomalous ? (
                        <XCircle className="h-4 w-4 text-red-600" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Critical Factors</span>
                      <span className="text-xs font-semibold bg-amber-100 text-amber-800 px-2 py-1 rounded">
                        {analysis?.critical_factors?.length || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Anomaly Score</span>
                      <span className="text-sm font-bold">
                        {(analysis?.anomaly_score || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Charts Tab */}
          <TabsContent value="charts" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Sensor Readings Charts */}
              <Card>
                <CardHeader>
                  <CardTitle>Nutrient Levels</CardTitle>
                  <CardDescription>NPK and essential elements</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ChartComponent 
                    title="Nitrogen (N)" 
                    value={sensorReadings.N} 
                    max={40} 
                    unit=" ppm"
                    status={sensorReadings.N ? (sensorReadings.N < 15 || sensorReadings.N > 30 ? "⚠️ Adjust" : "✓ Optimal") : "-"}
                  />
                  <ChartComponent 
                    title="Phosphorus (P)" 
                    value={sensorReadings.P} 
                    max={30} 
                    unit=" ppm"
                    status={sensorReadings.P ? (sensorReadings.P < 10 || sensorReadings.P > 25 ? "⚠️ Adjust" : "✓ Optimal") : "-"}
                  />
                  <ChartComponent 
                    title="Potassium (K)" 
                    value={sensorReadings.K} 
                    max={250} 
                    unit=" ppm"
                    status={sensorReadings.K ? (sensorReadings.K < 100 || sensorReadings.K > 200 ? "⚠️ Adjust" : "✓ Optimal") : "-"}
                  />
                </CardContent>
              </Card>

              {/* Physical Properties Charts */}
              <Card>
                <CardHeader>
                  <CardTitle>Physical Properties</CardTitle>
                  <CardDescription>Soil conditions</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ChartComponent 
                    title="pH Level" 
                    value={sensorReadings.pH} 
                    max={9} 
                    unit=""
                    status={sensorReadings.pH ? (sensorReadings.pH < 6.5 || sensorReadings.pH > 7.5 ? "⚠️ Needs Adjustment" : "✓ Optimal") : "-"}
                  />
                  <ChartComponent 
                    title="Moisture Content" 
                    value={sensorReadings.Moisture} 
                    max={100} 
                    unit="%"
                    status={sensorReadings.Moisture ? (sensorReadings.Moisture < 40 || sensorReadings.Moisture > 60 ? "⚠️ Adjust" : "✓ Optimal") : "-"}
                  />
                  <ChartComponent 
                    title="Soil Temperature" 
                    value={sensorReadings.Temperature} 
                    max={35} 
                    unit="°C"
                    status={sensorReadings.Temperature ? (sensorReadings.Temperature < 15 || sensorReadings.Temperature > 25 ? "⚠️ Monitor" : "✓ Optimal") : "-"}
                  />
                </CardContent>
              </Card>

              {/* Biological Properties */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Biological Properties</CardTitle>
                  <CardDescription>Microbial activity and CO2 respiration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ChartComponent 
                    title="CO2 Level (Microbial Respiration)" 
                    value={sensorReadings.CO2} 
                    max={800} 
                    unit=" ppm"
                    status={sensorReadings.CO2 ? (sensorReadings.CO2 < 400 || sensorReadings.CO2 > 700 ? "⚠️ Low Activity" : "✓ Active Microbes") : "-"}
                  />
                  <ChartComponent 
                    title="Microbial Health Index" 
                    value={microbialHealth} 
                    max={100} 
                    unit="/100"
                    status={microbialHealth >= 80 ? "🟢 Excellent" : microbialHealth >= 60 ? "🟡 Good" : "🔴 Needs Work"}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Education Tab */}
          <TabsContent value="education" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(educationalContent).map(([key, content]: any) => {
                const Icon = content.icon;
                return (
                  <Card key={key} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Icon className="h-5 w-5 text-primary" />
                        {content.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="font-semibold text-sm text-foreground mb-2">Why it matters:</p>
                        <p className="text-sm text-muted-foreground">{content.why}</p>
                      </div>

                      <div>
                        <p className="font-semibold text-sm text-foreground mb-2">Key Benefits:</p>
                        <ul className="space-y-1">
                          {content.benefits.map((benefit: string, idx: number) => (
                            <li key={idx} className="text-sm text-muted-foreground flex gap-2">
                              <span className="text-primary">•</span> {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <p className="font-semibold text-sm text-foreground mb-2">Farmer Tips:</p>
                        <ul className="space-y-1">
                          {content.tips.map((tip: string, idx: number) => (
                            <li key={idx} className="text-xs text-muted-foreground">{tip}</li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Microbial Health Tab */}
          <TabsContent value="microbial" className="space-y-6">
            <Card className="bg-gradient-to-br from-emerald-50 to-teal-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Microscope className="h-6 w-6 text-emerald-600" />
                  Soil Microbial Health Guide
                </CardTitle>
                <CardDescription>Understanding soil biology and CO2 respiration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">What is Microbial Health?</h3>
                  <p className="text-muted-foreground mb-4">
                    Microbial health refers to the population and activity of microorganisms (bacteria, fungi, actinomycetes) in your soil. 
                    These organisms are essential for nutrient cycling, disease suppression, and soil structure formation.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">How We Measure It (CO2 Respiration)</h3>
                  <p className="text-muted-foreground mb-4">
                    CO2 influx is a direct indicator of microbial respiration. When microbes consume organic matter, they release CO2. 
                    Higher CO2 = more active microbes = healthier, more fertile soil.
                  </p>
                  <div className="bg-white p-4 rounded-lg border">
                    <p className="font-semibold mb-2">CO2 Levels Interpretation:</p>
                    <ul className="space-y-2 text-sm">
                      <li><strong className="text-green-600">450-550 ppm:</strong> Excellent microbial activity</li>
                      <li><strong className="text-blue-600">400-450 ppm:</strong> Good microbial activity</li>
                      <li><strong className="text-yellow-600">350-400 ppm:</strong> Moderate activity - consider adding compost</li>
                      <li><strong className="text-red-600">&lt;350 ppm:</strong> Low activity - soil needs organic matter</li>
                    </ul>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Why Microbial Health Matters for Farmers</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex gap-2"><span className="text-emerald-600 font-bold">→</span> <strong>Better Nutrient Cycling:</strong> Microbes break down organic matter and release nutrients plants can use</li>
                    <li className="flex gap-2"><span className="text-emerald-600 font-bold">→</span> <strong>Disease Suppression:</strong> Healthy microbial populations prevent harmful pathogens</li>
                    <li className="flex gap-2"><span className="text-emerald-600 font-bold">→</span> <strong>Improved Soil Structure:</strong> Microbes produce compounds that hold soil particles together</li>
                    <li className="flex gap-2"><span className="text-emerald-600 font-bold">→</span> <strong>Better Water Retention:</strong> Structured soil holds more water for plants</li>
                    <li className="flex gap-2"><span className="text-emerald-600 font-bold">→</span> <strong>Higher Yields:</strong> Healthy soil biology = healthier crops = better production</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">How to Improve Microbial Health</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex gap-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">TIP 1</span> Add compost and organic matter - it's food for microbes</li>
                    <li className="flex gap-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">TIP 2</span> Avoid excessive tilling - it disrupts microbial networks</li>
                    <li className="flex gap-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">TIP 3</span> Use crop rotation - different crops support different microbes</li>
                    <li className="flex gap-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">TIP 4</span> Plant cover crops - they feed soil biology</li>
                    <li className="flex gap-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">TIP 5</span> Reduce chemical pesticides - they kill beneficial microbes</li>
                  </ul>
                </div>

                <Alert>
                  <BookOpen className="h-4 w-4" />
                  <AlertDescription>
                    💡 Your current microbial health: <strong>{microbialHealth}/100</strong> - {
                      microbialHealth >= 80 ? "Excellent! Your soil is very active and fertile." :
                      microbialHealth >= 60 ? "Good! Your soil biology is healthy. Keep maintaining it." :
                      "Needs improvement. Consider adding compost and reducing chemical inputs."
                    }
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Metrics Tab */}
          <TabsContent value="metrics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries({
                "N-P-K": `${sensorReadings.N || 0}:${sensorReadings.P || 0}:${sensorReadings.K || 0}`,
                "pH": sensorReadings.pH || "-",
                "Moisture": `${sensorReadings.Moisture || 0}%`,
                "Temperature": `${sensorReadings.Temperature || 0}°C`,
                "CO2": `${sensorReadings.CO2 || 0} ppm`,
                "Microbial Health": `${microbialHealth}/100`
              }).map(([label, value]) => (
                <Card key={label}>
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground">{label}</p>
                    <p className="text-2xl font-bold text-primary mt-2">{value}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Actionable Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis?.critical_factors && analysis.critical_factors.length > 0 ? (
                  <div className="space-y-3">
                    <p className="text-sm font-semibold">Areas needing attention:</p>
                    {analysis.critical_factors.map((factor: string, idx: number) => {
                      const content = educationalContent[factor as keyof typeof educationalContent];
                      return (
                        <Alert key={idx} className="border-l-4 border-l-amber-500 bg-amber-50">
                          <AlertCircle className="h-4 w-4 text-amber-600" />
                          <AlertDescription className="ml-2">
                            <strong>{factor}</strong> needs attention. {content?.tips?.[0]}
                          </AlertDescription>
                        </Alert>
                      );
                    })}
                  </div>
                ) : (
                  <Alert className="border-l-4 border-l-green-500 bg-green-50">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <AlertDescription className="ml-2">
                      ✓ All parameters are within optimal ranges. Maintain current practices!
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  );
};

export default SoilHealthReport;
