import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Download, RefreshCw, AlertCircle, CheckCircle } from "lucide-react";

// Network Configuration - use environment variable or default to localhost
const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL || "http://localhost:5000";

interface SensorReading {
  timestamp: string;
  health_index: number;
  health_status: string;
  is_anomalous: boolean;
  anomaly_score: number;
  sensor_readings: {
    N: number;
    P: number;
    K: number;
    CO2: number;
    Temperature: number;
    Moisture: number;
    pH: number;
  };
}

const SensorMonitoring = () => {
  const { toast } = useToast();
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [latestReading, setLatestReading] = useState<SensorReading | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportFormat, setExportFormat] = useState<"csv" | "json">("csv");
  const [timeRange, setTimeRange] = useState("1h");

  // Fetch sensor data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch history
        const historyRes = await fetch(
          `${BACKEND_API_URL}/api/soil-health/history?limit=100`
        );
        if (historyRes.ok) {
          const historyData = await historyRes.json();
          setReadings(historyData.readings || []);
        }

        // Fetch latest
        const latestRes = await fetch(
          `${BACKEND_API_URL}/api/soil-health/latest`
        );
        if (latestRes.ok) {
          const latestData = await latestRes.json();
          setLatestReading(latestData);
        }

        setLoading(false);
      } catch (error) {
        console.error("Error fetching sensor data from", BACKEND_API_URL, error);
        toast({
          title: "Error",
          description: `Failed to fetch sensor data from ${BACKEND_API_URL}`,
          variant: "destructive",
        });
        setLoading(false);
      }
    };

    fetchData();

    // Poll every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [toast]);

  // Format data for charts
  const chartData = readings
    .reverse()
    .map((reading) => ({
      timestamp: new Date(reading.timestamp).toLocaleTimeString(),
      shortTime: new Date(reading.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      N: reading.sensor_readings.N,
      P: reading.sensor_readings.P,
      K: reading.sensor_readings.K,
      CO2: reading.sensor_readings.CO2,
      Temperature: reading.sensor_readings.Temperature,
      Moisture: reading.sensor_readings.Moisture,
      pH: reading.sensor_readings.pH,
      health_index: reading.health_index,
    }));

  // Export to CSV
  const exportToCSV = () => {
    if (readings.length === 0) {
      toast({
        title: "No Data",
        description: "No sensor readings available to export",
        variant: "destructive",
      });
      return;
    }

    const headers = [
      "Timestamp",
      "N",
      "P",
      "K",
      "CO2",
      "Temperature",
      "Moisture",
      "pH",
      "Health Index",
      "Health Status",
      "Is Anomalous",
      "Anomaly Score",
    ];

    const csvContent = [
      headers.join(","),
      ...readings.map((reading) =>
        [
          reading.timestamp,
          reading.sensor_readings.N,
          reading.sensor_readings.P,
          reading.sensor_readings.K,
          reading.sensor_readings.CO2,
          reading.sensor_readings.Temperature,
          reading.sensor_readings.Moisture,
          reading.sensor_readings.pH,
          reading.health_index,
          reading.health_status,
          reading.is_anomalous,
          reading.anomaly_score,
        ].join(",")
      ),
    ].join("\n");

    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent)
    );
    element.setAttribute("download", `sensor-readings-${Date.now()}.csv`);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);

    toast({
      title: "Success",
      description: "Sensor data exported to CSV",
    });
  };

  // Export to JSON
  const exportToJSON = () => {
    if (readings.length === 0) {
      toast({
        title: "No Data",
        description: "No sensor readings available to export",
        variant: "destructive",
      });
      return;
    }

    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(readings, null, 2))
    );
    element.setAttribute("download", `sensor-readings-${Date.now()}.json`);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);

    toast({
      title: "Success",
      description: "Sensor data exported to JSON",
    });
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case "Excellent":
        return "bg-green-100 text-green-800";
      case "Good":
        return "bg-blue-100 text-blue-800";
      case "Fair":
        return "bg-yellow-100 text-yellow-800";
      case "Poor":
        return "bg-orange-100 text-orange-800";
      case "Critical":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getHealthBgColor = (status: string) => {
    switch (status) {
      case "Excellent":
        return "bg-green-50 border-green-200";
      case "Good":
        return "bg-blue-50 border-blue-200";
      case "Fair":
        return "bg-yellow-50 border-yellow-200";
      case "Poor":
        return "bg-orange-50 border-orange-200";
      case "Critical":
        return "bg-red-50 border-red-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  if (loading && readings.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <p className="text-muted-foreground">Loading sensor data...</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            🌾 Soil Health Monitor
          </h2>
          <p className="text-muted-foreground">
            Real-time sensor readings and analysis
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Latest Reading Card */}
      {latestReading && (
        <Card className={`border-2 ${getHealthBgColor(latestReading.health_status)}`}>
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Latest Reading</CardTitle>
                <CardDescription>
                  {new Date(latestReading.timestamp).toLocaleString()}
                </CardDescription>
              </div>
              <Badge className={getHealthColor(latestReading.health_status)}>
                {latestReading.health_status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">
                  Health Index
                </p>
                <p className="text-2xl font-bold">
                  {latestReading.health_index}%
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">
                  Temperature
                </p>
                <p className="text-2xl font-bold">
                  {latestReading.sensor_readings.Temperature}°C
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">
                  Moisture
                </p>
                <p className="text-2xl font-bold">
                  {latestReading.sensor_readings.Moisture}%
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">
                  pH Level
                </p>
                <p className="text-2xl font-bold">
                  {latestReading.sensor_readings.pH.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Anomaly Indicator */}
            {latestReading.is_anomalous && (
              <div className="flex items-center gap-2 bg-red-100 border border-red-300 rounded-lg p-3 text-red-800">
                <AlertCircle className="h-5 w-5" />
                <span>
                  ⚠️ Anomaly detected (Score: {latestReading.anomaly_score.toFixed(2)})
                </span>
              </div>
            )}

            {!latestReading.is_anomalous && (
              <div className="flex items-center gap-2 bg-green-100 border border-green-300 rounded-lg p-3 text-green-800">
                <CheckCircle className="h-5 w-5" />
                <span>✓ All readings within normal range</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Nutrients Chart */}
      <Card>
        <CardHeader>
          <CardTitle>NPK Nutrients Level</CardTitle>
          <CardDescription>
            Nitrogen (N), Phosphorus (P), and Potassium (K) trends
          </CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="shortTime" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="N"
                  stroke="#3b82f6"
                  name="Nitrogen (ppm)"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="P"
                  stroke="#8b5cf6"
                  name="Phosphorus (ppm)"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="K"
                  stroke="#ec4899"
                  name="Potassium (ppm)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No data available
            </p>
          )}
        </CardContent>
      </Card>

      {/* Environmental Conditions */}
      <Card>
        <CardHeader>
          <CardTitle>Environmental Conditions</CardTitle>
          <CardDescription>Temperature, Moisture, and CO2 levels</CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="shortTime" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="Temperature"
                  fill="#fbbf24"
                  stroke="#f59e0b"
                  name="Temperature (°C)"
                />
                <Area
                  type="monotone"
                  dataKey="Moisture"
                  fill="#60a5fa"
                  stroke="#3b82f6"
                  name="Moisture (%)"
                />
                <Area
                  type="monotone"
                  dataKey="CO2"
                  fill="#34d399"
                  stroke="#10b981"
                  name="CO2 (ppm)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No data available
            </p>
          )}
        </CardContent>
      </Card>

      {/* pH and Health Index */}
      <Card>
        <CardHeader>
          <CardTitle>Soil Health Metrics</CardTitle>
          <CardDescription>pH level and overall health index</CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="shortTime" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="pH"
                  fill="#6366f1"
                  name="pH Level"
                  radius={[8, 8, 0, 0]}
                />
                <Bar
                  dataKey="health_index"
                  fill="#06b6d4"
                  name="Health Index (%)"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No data available
            </p>
          )}
        </CardContent>
      </Card>

      {/* Sensor Details Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Readings</CardTitle>
          <CardDescription>Latest sensor measurements</CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2 font-semibold">Time</th>
                    <th className="text-left p-2 font-semibold">N</th>
                    <th className="text-left p-2 font-semibold">P</th>
                    <th className="text-left p-2 font-semibold">K</th>
                    <th className="text-left p-2 font-semibold">Temp</th>
                    <th className="text-left p-2 font-semibold">Moisture</th>
                    <th className="text-left p-2 font-semibold">pH</th>
                    <th className="text-left p-2 font-semibold">Health</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.slice(-10).reverse().map((row, idx) => (
                    <tr key={idx} className="border-b hover:bg-muted/50">
                      <td className="p-2">{row.shortTime}</td>
                      <td className="p-2">{row.N}</td>
                      <td className="p-2">{row.P}</td>
                      <td className="p-2">{row.K}</td>
                      <td className="p-2">{row.Temperature}°C</td>
                      <td className="p-2">{row.Moisture}%</td>
                      <td className="p-2">{row.pH.toFixed(2)}</td>
                      <td className="p-2">
                        <Badge variant="outline">{row.health_index}%</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No data available
            </p>
          )}
        </CardContent>
      </Card>

      {/* Export Section */}
      <Card>
        <CardHeader>
          <CardTitle>Export Data</CardTitle>
          <CardDescription>Download sensor readings in various formats</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-3 flex-wrap">
          <Button onClick={exportToCSV} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download CSV ({readings.length} records)
          </Button>
          <Button onClick={exportToJSON} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download JSON ({readings.length} records)
          </Button>
        </CardContent>
      </Card>

      {/* Stats Summary */}
      {readings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Data Summary</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Readings</p>
              <p className="text-2xl font-bold">{readings.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg Health</p>
              <p className="text-2xl font-bold">
                {Math.round(
                  readings.reduce((sum, r) => sum + r.health_index, 0) /
                    readings.length
                )}
                %
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Anomalies</p>
              <p className="text-2xl font-bold">
                {readings.filter((r) => r.is_anomalous).length}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Anomaly Rate
              </p>
              <p className="text-2xl font-bold">
                {(
                  (readings.filter((r) => r.is_anomalous).length /
                    readings.length) *
                  100
                ).toFixed(1)}
                %
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SensorMonitoring;
