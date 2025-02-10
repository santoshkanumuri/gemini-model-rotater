
import json
from datetime import datetime, timedelta

class Model:
    def __init__(self, name: str, requests_per_minute: int, requests_per_day: int, ranking: int):
        self.name = name
        self.requests_per_minute_limit = requests_per_minute
        self.requests_per_day_limit = requests_per_day
        self.ranking = ranking

        # Usage counters
        self.current_minute_usage = 0
        self.current_day_usage = 0

        # Timestamps for resetting the usage counters
        self.last_minute_reset = datetime.now()
        self.last_day_reset = datetime.now()

        # Count of times a 429 (resource exhausted) error has occurred
        self.resource_exhausted_count = 0

    def reset_minute_usage(self):
        self.current_minute_usage = 0
        self.last_minute_reset = datetime.now()

    def reset_day_usage(self):
        self.current_day_usage = 0
        self.last_day_reset = datetime.now()

    def update_usage_if_needed(self):
        now = datetime.now()
        if now - self.last_minute_reset >= timedelta(minutes=1):
            self.reset_minute_usage()
        if now - self.last_day_reset >= timedelta(days=1):
            self.reset_day_usage()

    def can_make_request(self) -> bool:
        """
        Returns True if the model still has remaining quota.
        """
        self.update_usage_if_needed()
        return (self.current_minute_usage < self.requests_per_minute_limit and
                self.current_day_usage < self.requests_per_day_limit)

    def increment_usage(self):
        """
        Call this after every request.
        """
        self.update_usage_if_needed()
        self.current_minute_usage += 1
        self.current_day_usage += 1

    def available_requests(self) -> int:
        """
        Returns the minimum number of remaining requests (minute or day).
        """
        self.update_usage_if_needed()
        remaining_minute = self.requests_per_minute_limit - self.current_minute_usage
        remaining_day = self.requests_per_day_limit - self.current_day_usage
        return min(remaining_minute, remaining_day)

    def __repr__(self):
        return (f"Model(name={self.name}, "
                f"minute_usage={self.current_minute_usage}/{self.requests_per_minute_limit}, "
                f"day_usage={self.current_day_usage}/{self.requests_per_day_limit}, "
                f"resource_exhausted_count={self.resource_exhausted_count}, "
                f"ranking={self.ranking})")


class ModelManager:
    def __init__(self, json_file: str):
        """
        Initialize the manager with a JSON file containing model details.
        """
        self.models = []
        self.load_models(json_file)

    def load_models(self, json_file: str):
        with open(json_file, 'r') as f:
            data = json.load(f)
        for model_data in data:
            model = Model(
                name=model_data["name"],
                requests_per_minute=model_data["requests_per_minute"],
                requests_per_day=model_data["requests_per_day"],
                ranking=model_data["ranking"]
            )
            self.models.append(model)

    def get_sorted_available_models(self, exclude_model_name: str = None):
        """
        Returns a sorted list of models that can make a request.
        Sorted by:
         1. Highest available daily requests (desc)
         2. Highest available minute requests (desc)
         3. Least resource exhausted count (asc)
         4. Lower ranking (asc)
        """
        available_models = [
            m for m in self.models
            if m.can_make_request() and (exclude_model_name is None or m.name != exclude_model_name)
        ]
        available_models.sort(key=lambda m: (
            -(m.requests_per_day_limit - m.current_day_usage),      # Highest available daily requests
            -(m.requests_per_minute_limit - m.current_minute_usage),  # Highest available minute requests
            m.resource_exhausted_count,                               # Least 429 error count
            m.ranking                                               # Lower ranking is preferred
        ))
        return available_models

    def get_available_model(self) -> Model:
        """
        Returns the best available model based on:
          1. Highest available daily requests.
          2. Highest available minute requests.
          3. Least resource exhausted count.
          4. Lower ranking.
        Returns None if no model is available.
        """
        # Update usage for all models.
        for model in self.models:
            model.update_usage_if_needed()

        sorted_models = self.get_sorted_available_models()
        if sorted_models:
            return sorted_models[0]
        return None

    def increment_request(self, model_name: str):
        """
        Increment the request count for the model with the given name.
        """
        for model in self.models:
            if model.name == model_name:
                model.increment_usage()
                return
        raise ValueError(f"Model with name {model_name} not found.")

    def swap_model(self, current_model_name: str) -> Model:
        """
        When a 429 error is encountered, call this method to select a new model.
        It first increments the resource exhausted count for the current model,
        refreshes all usage counters, and then returns the best available alternative
        (i.e. with available limits) based on:
          1. Highest available daily requests.
          2. Highest available minute requests.
          3. Least resource exhausted count.
          4. Lower ranking.
        If no alternative is available, it will return the current model if it
        has recovered or None otherwise.
        """
        # Update usage for all models.
        for model in self.models:
            model.update_usage_if_needed()

        # Increment resource exhausted count for the current model.
        current_model = self.get_model_by_name(current_model_name)
        if current_model:
            current_model.resource_exhausted_count += 1

        # Look for an alternative model that is not the current one.
        alternative_models = self.get_sorted_available_models(exclude_model_name=current_model_name)
        if alternative_models:
            return alternative_models[0]
        else:
            # If no alternative is available, check if the current model has recovered.
            if current_model and current_model.can_make_request():
                return current_model
            else:
                return None

    def get_model_by_name(self, model_name: str) -> Model:
        for model in self.models:
            if model.name == model_name:
                return model
        return None
