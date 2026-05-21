import collections

class DriftMonitor:
    def __init__(self, window_size=30, threshold=0.60):
        """
        Monitors AI Confidence scores over a rolling window to detect Data Drift.
        """
        self.window_size = window_size
        self.threshold = threshold
        self.history = collections.deque(maxlen=window_size)

    def update(self, frame_confidences: list[float]) -> dict:
        """
        Takes the confidences of the current frame, updates the rolling average,
        and evaluates if data drift is occurring.
        """
        # Only update the rolling average if detections actually occurred
        if frame_confidences:
            frame_avg = sum(frame_confidences) / len(frame_confidences)
            self.history.append(frame_avg)

        # If we have no history at all yet, return defaults
        if not self.history:
            return {"avg_confidence": 0.0, "drift_detected": False}

        # Calculate Rolling Average
        rolling_avg = sum(self.history) / len(self.history)
        
        # Drift is triggered if confidence falls below the strict threshold
        drift_detected = rolling_avg < self.threshold

        return {
            "avg_confidence": round(rolling_avg, 2),
            "drift_detected": drift_detected
        }
