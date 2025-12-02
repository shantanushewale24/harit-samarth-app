import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { Droplets, Thermometer, Gauge, Power, Wifi, WifiOff } from "lucide-react";
import mqtt from "mqtt";

interface SensorData {
  soilMoisture: number;
  soilPH: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  temperature: number;
  humidity: number;
}

const HardwareModule = () => {
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const [mqttBroker, setMqttBroker] = useState("mqtt://broker.hivemq.com");
  const [mqttTopic, setMqttTopic] = useState("agribio/sensors");
  const [client, setClient] = useState<mqtt.MqttClient | null>(null);
  const [sensorData, setSensorData] = useState<SensorData>({
    soilMoisture: 0,
    soilPH: 7.0,
    nitrogen: 0,
    phosphorus: 0,
    potassium: 0,
    temperature: 0,
    humidity: 0,
  });
  const [irrigationActive, setIrrigationActive] = useState(false);

  const connectToMQTT = () => {
    try {
      const mqttClient = mqtt.connect(mqttBroker);

      mqttClient.on("connect", () => {
        setIsConnected(true);
        mqttClient.subscribe(mqttTopic);
        toast({
          title: "Connected",
          description: "Successfully connected to Agribio hardware module",
        });
      });

      mqttClient.on("message", (topic, message) => {
        try {
          const data = JSON.parse(message.toString());
          setSensorData({
            soilMoisture: data.soilMoisture || 0,
            soilPH: data.soilPH || 7.0,
            nitrogen: data.nitrogen || 0,
            phosphorus: data.phosphorus || 0,
            potassium: data.potassium || 0,
            temperature: data.temperature || 0,
            humidity: data.humidity || 0,
          });
        } catch (error) {
          console.error("Error parsing MQTT message:", error);
        }
      });

      mqttClient.on("error", (error) => {
        toast({
          title: "Connection Error",
          description: error.message,
          variant: "destructive",
        });
      });

      setClient(mqttClient);
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Could not connect to MQTT broker",
        variant: "destructive",
      });
    }
  };

  const disconnect = () => {
    if (client) {
      client.end();
      setClient(null);
      setIsConnected(false);
      toast({
        title: "Disconnected",
        description: "Disconnected from hardware module",
      });
    }
  };

  const toggleIrrigation = (enabled: boolean) => {
    setIrrigationActive(enabled);
    if (client && isConnected) {
      client.publish("agribio/control/irrigation", JSON.stringify({ active: enabled }));
      toast({
        title: enabled ? "Irrigation Started" : "Irrigation Stopped",
        description: `Irrigation system ${enabled ? "activated" : "deactivated"}`,
      });
    }
  };

  useEffect(() => {
    return () => {
      if (client) {
        client.end();
      }
    };
  }, [client]);

  return (
    <section id="hardware" className="py-16 px-4 bg-muted/30">
      <div className="container mx-auto max-w-6xl">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-foreground">
          Agribio Hardware Module
        </h2>

        <div className="grid gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {isConnected ? (
                  <Wifi className="h-5 w-5 text-primary" />
                ) : (
                  <WifiOff className="h-5 w-5 text-muted-foreground" />
                )}
                MQTT Connection
              </CardTitle>
              <CardDescription>
                Connect to your Agribio hardware module via MQTT protocol
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="broker">MQTT Broker URL</Label>
                <Input
                  id="broker"
                  value={mqttBroker}
                  onChange={(e) => setMqttBroker(e.target.value)}
                  placeholder="mqtt://broker.hivemq.com"
                  disabled={isConnected}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="topic">MQTT Topic</Label>
                <Input
                  id="topic"
                  value={mqttTopic}
                  onChange={(e) => setMqttTopic(e.target.value)}
                  placeholder="agribio/sensors"
                  disabled={isConnected}
                />
              </div>
              <Button
                onClick={isConnected ? disconnect : connectToMQTT}
                className="w-full"
                variant={isConnected ? "destructive" : "default"}
              >
                {isConnected ? "Disconnect" : "Connect to Hardware"}
              </Button>
            </CardContent>
          </Card>

          {isConnected && (
            <>
              <div className="grid md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Droplets className="h-5 w-5 text-primary" />
                      Soil Sensors
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Moisture:</span>
                      <span className="font-semibold">{sensorData.soilMoisture}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">pH Level:</span>
                      <span className="font-semibold">{sensorData.soilPH}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Nitrogen (N):</span>
                      <span className="font-semibold">{sensorData.nitrogen} mg/kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Phosphorus (P):</span>
                      <span className="font-semibold">{sensorData.phosphorus} mg/kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Potassium (K):</span>
                      <span className="font-semibold">{sensorData.potassium} mg/kg</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Thermometer className="h-5 w-5 text-primary" />
                      Environmental Sensors
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Temperature:</span>
                      <span className="font-semibold">{sensorData.temperature}°C</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Humidity:</span>
                      <span className="font-semibold">{sensorData.humidity}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Power className="h-5 w-5 text-primary" />
                    Actuator Controls
                  </CardTitle>
                  <CardDescription>
                    Control your farm equipment remotely
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="irrigation">Irrigation System</Label>
                      <p className="text-sm text-muted-foreground">
                        {irrigationActive ? "Currently running" : "Currently off"}
                      </p>
                    </div>
                    <Switch
                      id="irrigation"
                      checked={irrigationActive}
                      onCheckedChange={toggleIrrigation}
                    />
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </section>
  );
};

export default HardwareModule;
