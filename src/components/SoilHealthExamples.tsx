/**
 * Soil Health Dashboard - Frontend Integration Guide
 * Complete guide for integrating the ML backend with React components
 */

import { soilHealthService, type SensorReading } from '@/services/soilHealthService';
import { useState, useEffect, useCallback } from 'react';

/**
 * EXAMPLE 1: Basic Soil Health Display Component
 */
export function SoilHealthCard() {
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample sensor reading (in real app, this would come from IoT sensors)
  const sensorReading: SensorReading = {
    N: 22,
    P: 18,
    K: 150,
    CO2: 500,
    Temperature: 22,
    Moisture: 55,
    pH: 7.2
  };

  const analyzeSoil = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await soilHealthService.analyzeSoil(sensorReading);
      setHealthData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    analyzeSoil();
  }, [analyzeSoil]);

  if (loading) return <div>Analyzing soil health...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (!healthData) return null;

  const healthIndex = healthData.soil_health_index;
  const statusColor = soilHealthService.getHealthStatusColor(healthIndex);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Soil Health Index</h2>
      
      {/* Health Score Gauge */}
      <div className="flex items-center gap-4 mb-6">
        <div 
          className="w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold text-white"
          style={{ backgroundColor: statusColor }}
        >
          {healthIndex}
        </div>
        <div>
          <p className="text-lg font-semibold">{healthData.health_status}</p>
          <p className="text-gray-600">
            {soilHealthService.getHealthStatusMessage(healthData.health_status)}
          </p>
        </div>
      </div>

      {/* Anomaly Status */}
      {healthData.is_anomalous && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
          <p className="text-yellow-800 font-semibold">⚠️ Anomaly Detected</p>
          <p className="text-yellow-700">Score: {healthData.anomaly_score.toFixed(2)}</p>
        </div>
      )}

      {/* Critical Factors */}
      {healthData.critical_factors.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Factors Needing Attention:</h3>
          <ul className="list-disc list-inside text-red-600">
            {healthData.critical_factors.map((factor: string, idx: number) => (
              <li key={idx}>{factor}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/**
 * EXAMPLE 2: Real-time Sensor Monitoring
 */
export function RealtimeSensorMonitor() {
  const [readings, setReadings] = useState<any[]>([]);
  const [latestAnalysis, setLatestAnalysis] = useState<any>(null);

  // Simulate receiving sensor data every 30 minutes
  useEffect(() => {
    const interval = setInterval(async () => {
      // In real app, fetch from IoT gateway
      const newReading: SensorReading = {
        N: 20 + Math.random() * 4,
        P: 16 + Math.random() * 4,
        K: 145 + Math.random() * 10,
        CO2: 490 + Math.random() * 20,
        Temperature: 20 + Math.random() * 6,
        Moisture: 50 + Math.random() * 10,
        pH: 7.0 + (Math.random() - 0.5) * 0.4
      };

      try {
        const analysis = await soilHealthService.analyzeSoil(newReading);
        setReadings(prev => [...prev, analysis]);
        setLatestAnalysis(analysis);

        // Alert on anomalies
        if (analysis.is_anomalous) {
          console.warn('Anomaly detected:', analysis);
          // Show notification to user
        }
      } catch (err) {
        console.error('Failed to analyze reading:', err);
      }
    }, 30 * 60 * 1000); // Every 30 minutes

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Real-time Monitoring</h2>
      
      <div className="grid grid-cols-2 gap-4">
        {latestAnalysis && (
          <>
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-gray-600">Latest Health Score</p>
              <p className="text-3xl font-bold">{latestAnalysis.soil_health_index}</p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-gray-600">Status</p>
              <p className="text-xl font-bold">{latestAnalysis.health_status}</p>
            </div>
          </>
        )}
      </div>

      {/* Health Score Trend Chart */}
      <div className="h-64 bg-gray-50 rounded p-4">
        {/* Use Chart.js or Recharts for visualization */}
        <p className="text-gray-500">Health Index Trend</p>
        {readings.length > 0 && (
          <p className="text-sm">
            Last {readings.length} readings: {readings[0].soil_health_index} → {readings[readings.length - 1].soil_health_index}
          </p>
        )}
      </div>

      {/* Recent Readings */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th>Time</th>
              <th>Health</th>
              <th>Status</th>
              <th>Anomaly</th>
            </tr>
          </thead>
          <tbody>
            {readings.slice(-5).reverse().map((reading, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="p-2">{new Date(reading.timestamp).toLocaleTimeString()}</td>
                <td className="p-2">{reading.soil_health_index}</td>
                <td className="p-2">{reading.health_status}</td>
                <td className="p-2">{reading.is_anomalous ? '⚠️ Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * EXAMPLE 3: Parameter Comparison with Optimal Ranges
 */
export function ParameterComparison() {
  const [optimalRanges, setOptimalRanges] = useState<any>(null);
  const [currentReading, setCurrentReading] = useState<SensorReading | null>(null);

  useEffect(() => {
    const fetchRanges = async () => {
      const { optimal_ranges } = await soilHealthService.getOptimalRanges();
      setOptimalRanges(optimal_ranges);
    };
    fetchRanges();
  }, []);

  if (!optimalRanges || !currentReading) return null;

  const getParameterStatus = (param: string, value: number) => {
    const range = optimalRanges[param];
    if (value < range.min) return 'low';
    if (value > range.max) return 'high';
    return 'optimal';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'optimal': return 'bg-green-100 text-green-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Parameter Analysis</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(optimalRanges).map(([param, range]: [string, any]) => {
          const currentValue = currentReading[param as keyof SensorReading];
          const status = getParameterStatus(param, currentValue);

          return (
            <div key={param} className="border rounded p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">{range.description}</h3>
                <span className={`px-2 py-1 rounded text-sm font-semibold ${getStatusColor(status)}`}>
                  {status.toUpperCase()}
                </span>
              </div>

              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span>Current: {currentValue}</span>
                  <span className="text-gray-600">{range.unit}</span>
                </div>
                {/* Progress bar */}
                <div className="h-2 bg-gray-200 rounded">
                  <div 
                    className={`h-full rounded ${status === 'optimal' ? 'bg-green-500' : status === 'low' ? 'bg-blue-500' : 'bg-orange-500'}`}
                    style={{
                      width: `${Math.max(0, Math.min(100, ((currentValue - range.critical_min) / (range.critical_max - range.critical_min)) * 100))}%`
                    }}
                  />
                </div>
              </div>

              <div className="text-xs text-gray-600">
                <p>Optimal: {range.min}-{range.max} {range.unit}</p>
                <p>Critical: {range.critical_min}-{range.critical_max} {range.unit}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * EXAMPLE 4: Batch Analysis for Historical Data
 */
export function HistoricalAnalysis() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const analyzeHistoricalData = useCallback(async () => {
    setLoading(true);
    
    // Sample 7 days of readings (48 per day at 30-min intervals)
    const readings: SensorReading[] = Array.from({ length: 336 }, (_, i) => ({
      N: 20 + Math.sin(i / 50) * 4 + Math.random(),
      P: 16 + Math.sin(i / 60) * 3 + Math.random(),
      K: 150 + Math.sin(i / 40) * 15 + Math.random() * 5,
      CO2: 500 + Math.sin(i / 100) * 50 + Math.random() * 10,
      Temperature: 20 + Math.sin(i / 20) * 4 + Math.random() * 2,
      Moisture: 50 + Math.sin(i / 80) * 10 + Math.random() * 3,
      pH: 7.0 + Math.sin(i / 120) * 0.3 + (Math.random() - 0.5) * 0.1
    }));

    try {
      const result = await soilHealthService.batchAnalyze(readings);
      setAnalyses(result.analyses);
    } catch (err) {
      console.error('Batch analysis failed:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    analyzeHistoricalData();
  }, [analyzeHistoricalData]);

  if (loading) return <div>Analyzing historical data...</div>;

  const averageHealth = analyses.length > 0
    ? Math.round(analyses.reduce((sum, a) => sum + a.soil_health_index, 0) / analyses.length)
    : 0;

  const anomalyCount = analyses.filter(a => a.is_anomalous).length;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Historical Analysis (7 Days)</h2>
      
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-gray-600">Average Health</p>
          <p className="text-3xl font-bold">{averageHealth}</p>
        </div>
        <div className="bg-orange-50 p-4 rounded">
          <p className="text-gray-600">Anomalies Detected</p>
          <p className="text-3xl font-bold">{anomalyCount}</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <p className="text-gray-600">Total Readings</p>
          <p className="text-3xl font-bold">{analyses.length}</p>
        </div>
      </div>

      {/* Health Status Distribution */}
      <div className="bg-white p-4 rounded border">
        <h3 className="font-semibold mb-4">Health Status Distribution</h3>
        {['Excellent', 'Good', 'Fair', 'Poor', 'Critical'].map(status => {
          const count = analyses.filter(a => a.health_status === status).length;
          const percentage = (count / analyses.length) * 100;
          return (
            <div key={status} className="mb-3">
              <div className="flex justify-between mb-1">
                <span>{status}</span>
                <span>{count} ({percentage.toFixed(1)}%)</span>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div 
                  className="h-full rounded bg-blue-500"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * EXAMPLE 5: Alert Management
 */
export function AlertSystem() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [sensorReading, setSensorReading] = useState<SensorReading>({
    N: 22, P: 18, K: 150, CO2: 500,
    Temperature: 22, Moisture: 55, pH: 7.2
  });

  const checkHealthAndAlert = useCallback(async () => {
    try {
      const analysis = await soilHealthService.analyzeSoil(sensorReading);
      const newAlerts: any[] = [];

      // Check for critical health
      if (analysis.soil_health_index < 30) {
        newAlerts.push({
          severity: 'critical',
          message: 'Soil health is critical!',
          timestamp: new Date()
        });
      }

      // Check for anomalies
      if (analysis.is_anomalous && analysis.anomaly_score > 0.7) {
        newAlerts.push({
          severity: 'warning',
          message: 'High anomaly detected in sensor readings',
          timestamp: new Date()
        });
      }

      // Check for critical factors
      if (analysis.critical_factors.length > 0) {
        newAlerts.push({
          severity: 'info',
          message: `${analysis.critical_factors.length} factors need attention`,
          timestamp: new Date()
        });
      }

      setAlerts(newAlerts);
    } catch (err) {
      console.error('Alert check failed:', err);
    }
  }, [sensorReading]);

  useEffect(() => {
    checkHealthAndAlert();
  }, [checkHealthAndAlert]);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Alerts & Notifications</h2>
      
      {alerts.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded p-4">
          <p className="text-green-800">✓ All systems normal</p>
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert, idx) => (
            <div 
              key={idx}
              className={`rounded p-4 border ${
                alert.severity === 'critical' ? 'bg-red-50 border-red-200' :
                alert.severity === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex justify-between">
                <span className="font-semibold">{alert.message}</span>
                <span className="text-xs text-gray-500">
                  {alert.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default {
  SoilHealthCard,
  RealtimeSensorMonitor,
  ParameterComparison,
  HistoricalAnalysis,
  AlertSystem
};
