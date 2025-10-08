class HealthCalculator:
    """
    Calculates the overall system health score based on weighted metrics.
    """

    def __init__(self):
        # Define the weight of each metric in the final score.
        # The sum of weights should ideally be 1.0.
        self.weights = {
            'cpu': 0.25,
            'memory': 0.25,
            'disk': 0.20,
            'battery': 0.15,
            'temperature': 0.15,
        }

    def _normalize_metric(self, key, value):
        """
        Normalizes a raw metric value to a 0-100 score where 100 is healthy.
        For metrics like CPU, Memory, Disk, and Temp, lower is better.
        For Battery, higher is better.
        """
        if value is None:
            return 0, 0  # Return 0 score and 0 weight if metric is not available

        score = 0
        if key in ['cpu', 'memory', 'disk']:
            # Inverse score: 100% usage = 0 score
            score = 100 - value
        elif key == 'temperature':
            # A more nuanced scale for temperature.
            if value < 60:
                score = 100
            elif value < 80:
                score = 100 - (value - 60) * 2.5  # Scale from 100 down to 50
            elif value < 95:
                score = 50 - (value - 80) * 3   # Scale from 50 down to 5
            else:
                score = 0  # Critical temperature
        elif key == 'battery':
            # Direct score: 100% battery = 100 score
            score = value

        return score, self.weights[key]

    def get_score_status(self, score):
        """Determines the status text, color, and emoji based on the score."""
        if score > 80:
            return {'text': 'EXCELLENT', 'color': '#27ae60', 'emoji': '✅'}
        elif score > 60:
            return {'text': 'GOOD', 'color': '#f39c12', 'emoji': '👍'}
        elif score > 40:
            return {'text': 'FAIR', 'color': '#e67e22', 'emoji': '⚠️'}
        else:
            return {'text': 'CRITICAL', 'color': '#e74c3c', 'emoji': '🚨'}

    def calculate_health_score(self, metrics):
        """
        Calculates the final weighted health score from all available metrics.
        """
        total_score = 0
        total_weight = 0

        for key, data in metrics.items():
            if data and key in self.weights:
                normalized_score, weight = self._normalize_metric(
                    key, data['value'])
                total_score += normalized_score * weight
                total_weight += weight

        # Adjust the score based on the available metrics
        if total_weight == 0:
            final_score = 0
        else:
            final_score = total_score / total_weight

        score_status = self.get_score_status(final_score)

        return final_score, score_status
