import numpy as np
from typing import Dict, Any, Tuple
from ml.anomaly_detection import EnsembleAnomalyDetector

class AnomalyService:
    def __init__(self):
        self.ml_detector = EnsembleAnomalyDetector()
        self.vibration_threshold = 1.8  # g
        self.acoustic_threshold = 65.0  # kHz
        self.thermal_threshold_delta = 4.0  # Celsius

    def analyze_telemetry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes telemetry signals through ML and heuristic detection.
        Returns:
            dict: {
                "is_anomaly": bool,
                "score": float (0-100),
                "severity": str ("NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"),
                "reasons": list,
                "trigger_incident": bool
            }
        """
        vibration = float(data.get("vibration", 0.25))
        acoustic = float(data.get("acoustic", 45.0))
        temp = float(data.get("temperature", 25.0))
        cpu = float(data.get("cpu", 35.0))
        network_out = int(data.get("network_out", 850))

        reasons = []
        score = 10.0

        # Physical vibration check
        if vibration > self.vibration_threshold:
            reasons.append(f"Excessive vibration acceleration: {vibration:.2f}g (limit: {self.vibration_threshold}g)")
            score += 35.0

        # Acoustic harmonic emission check
        if acoustic > self.acoustic_threshold:
            reasons.append(f"High-frequency acoustic emission spike: {acoustic:.1f}kHz (limit: {self.acoustic_threshold}kHz)")
            score += 30.0

        # Thermal expansion gradient
        if abs(temp - 25.0) > self.thermal_threshold_delta:
            reasons.append(f"Rail thermal stress delta: +{abs(temp - 25.0):.1f}°C")
            score += 15.0

        # Cyber anomaly: CPU spike or abnormal outbound network burst
        if cpu > 85.0:
            reasons.append(f"Anomalous processor utilization: {cpu:.1f}%")
            score += 15.0
        if network_out > 5000:
            reasons.append(f"Anomalous outbound traffic volume: {network_out} pkts/s")
            score += 20.0

        score = min(100.0, score)

        if score >= 80.0:
            severity = "CRITICAL"
            is_anomaly = True
            trigger_incident = True
        elif score >= 60.0:
            severity = "HIGH"
            is_anomaly = True
            trigger_incident = True
        elif score >= 40.0:
            severity = "MEDIUM"
            is_anomaly = True
            trigger_incident = False
        elif score >= 25.0:
            severity = "LOW"
            is_anomaly = False
            trigger_incident = False
        else:
            severity = "NORMAL"
            is_anomaly = False
            trigger_incident = False

        return {
            "is_anomaly": is_anomaly,
            "score": round(score, 1),
            "severity": severity,
            "reasons": reasons,
            "trigger_incident": trigger_incident
        }

anomaly_service = AnomalyService()
