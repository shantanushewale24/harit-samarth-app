/**
 * Soil Health API Service
 * Integrates with Python backend ML models
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

interface SensorReading {
  N: number;
  P: number;
  K: number;
  CO2: number;
  Temperature: number;
  Moisture: number;
  pH: number;
}

interface HealthAnalysis {
  timestamp: string;
  soil_health_index: number;
  health_status: string;
  is_anomalous: boolean;
  anomaly_score: number;
  critical_factors: string[];
  sensor_reading: SensorReading;
}

interface HealthIndexResponse {
  health_index: number;
  health_status: string;
  scale: string;
}

interface AnomalyResponse {
  is_anomalous: boolean;
  anomaly_score: number;
  severity: string;
}

interface CriticalFactorsResponse {
  critical_factors: string[];
  factor_count: number;
  status: string;
}

interface OptimalRanges {
  [key: string]: {
    min: number;
    max: number;
    unit: string;
    description: string;
  };
}

class SoilHealthService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch('/health');
    return response.json();
  }

  /**
   * Analyze soil health from sensor reading
   */
  async analyzeSoil(reading: SensorReading): Promise<HealthAnalysis> {
    const response = await fetch(`${this.baseUrl}/soil-health/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reading),
    });

    if (!response.ok) {
      throw new Error(`Failed to analyze soil: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get soil biological health index (1-100)
   */
  async getHealthIndex(reading: SensorReading): Promise<HealthIndexResponse> {
    const response = await fetch(`${this.baseUrl}/soil-health/health-index`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reading),
    });

    if (!response.ok) {
      throw new Error(`Failed to get health index: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Detect anomalies in sensor reading
   */
  async detectAnomaly(reading: SensorReading): Promise<AnomalyResponse> {
    const response = await fetch(`${this.baseUrl}/soil-health/anomaly`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reading),
    });

    if (!response.ok) {
      throw new Error(`Failed to detect anomaly: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get critical factors affecting soil health
   */
  async getCriticalFactors(reading: SensorReading): Promise<CriticalFactorsResponse> {
    const response = await fetch(`${this.baseUrl}/soil-health/critical-factors`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reading),
    });

    if (!response.ok) {
      throw new Error(`Failed to get critical factors: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get optimal ranges for all parameters
   */
  async getOptimalRanges(): Promise<{ optimal_ranges: OptimalRanges }> {
    const response = await fetch(`${this.baseUrl}/soil-health/optimal-ranges`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get optimal ranges: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Analyze multiple sensor readings in batch
   */
  async batchAnalyze(readings: SensorReading[]): Promise<{ count: number; analyses: HealthAnalysis[] }> {
    const response = await fetch(`${this.baseUrl}/soil-health/batch-analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ readings }),
    });

    if (!response.ok) {
      throw new Error(`Failed to batch analyze: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get health status color based on index
   */
  getHealthStatusColor(index: number): string {
    if (index >= 75) return '#10b981'; // Green
    if (index >= 60) return '#f59e0b'; // Amber
    if (index >= 45) return '#f97316'; // Orange
    if (index >= 30) return '#ef4444'; // Red
    return '#991b1b'; // Dark Red
  }

  /**
   * Get health status message
   */
  getHealthStatusMessage(status: string): string {
    const messages: { [key: string]: string } = {
      Excellent: 'Your soil is in excellent condition. Continue current practices.',
      Good: 'Your soil health is good. Monitor key parameters.',
      Fair: 'Your soil needs some attention. Review critical factors.',
      Poor: 'Your soil requires immediate intervention.',
      Critical: 'Your soil is in critical condition. Take urgent action.',
    };
    return messages[status] || 'Unknown status';
  }
}

export const soilHealthService = new SoilHealthService();
export type { SensorReading, HealthAnalysis, HealthIndexResponse, AnomalyResponse, CriticalFactorsResponse, OptimalRanges };
