# Gemini Model Rotater

`gemini-model-rotater` is a Python package designed to manage and rotate through multiple Gemini API models based on their rate limits. It loads model configurations from a JSON file and selects the best available model by evaluating remaining quotas for requests per minute and per day. The package supports incrementing usage after successful requests and swapping to alternative models when rate limits are exceeded (e.g., upon receiving a 429 error). Models are prioritized based on their ranking (lower numbers preferred), remaining quota, and history of rate limit exhaustion. This tool is ideal for applications interacting with APIs that impose strict rate limits across multiple models or accounts.

## Installation

Install the package using pip with the following command:

```bash
pip install gemini-model-rotater==1.0.0
```

**Note:** If the package is not available on PyPI, you may need to install it from a local source or repository (e.g., `pip install .` from the project directory). The above command assumes it’s published on PyPI.

## Usage

Here’s how to use the `gemini-model-rotater` package in your Python code:

```python
from gemini_model_rotater import ModelManager

# Initialize the ModelManager with a JSON file containing model configurations
manager = ModelManager("models.json")

# Get the best available model based on remaining quota and ranking
model = manager.get_available_model()
if model:
    print("Using model:", model.name)
    # Perform your API call here using model.name and model.top_k if applicable
    # Example: response = api_call(model.name, top_k=model.top_k)
    # After a successful request, increment the usage
    manager.increment_request(model.name)
else:
    print("No models available. Please wait for rate limits to reset.")

# If a 429 error occurs during the API call, swap to an alternative model
alternative_model = manager.swap_model(model.name)
if alternative_model:
    print("Swapped to model:", alternative_model.name)
    # Use the alternative model for the next request
else:
    print("No alternative models available.")
```

### Key Points
- **Automatic Resets:** The package automatically resets usage counters when the minute or day periods elapse, ensuring accurate tracking of available requests.
- **Handling 429 Errors:** If an API call returns a 429 error (rate limit exceeded), call `swap_model()` with the current model’s name to switch to another available model.
- **Model Selection:** Models are selected based on remaining requests (daily and minute), the number of times they’ve hit rate limits (`resource_exhausted_count`), and their `ranking` (lower is better).

## JSON File Format

The package expects a JSON file with a list of model configurations. Each model must include the following fields:

- **`name`**: A unique string identifier for the model.
- **`requests_per_minute`**: Integer maximum requests allowed per minute.
- **`requests_per_day`**: Integer maximum requests allowed per day.
- **`ranking`**: Integer preference order (lower values are prioritized).
- **`top_k`**: Integer model-specific parameter (e.g., for API calls; required by the code).

### Example `models.json`
```json
[
  {
    "name": "model_A",
    "requests_per_minute": 10,
    "requests_per_day": 100,
    "ranking": 1,
    "top_k": 5
  },
  {
    "name": "model_B",
    "requests_per_minute": 5,
    "requests_per_day": 50,
    "ranking": 2,
    "top_k": 3
  }
]
```

**Note:** Ensure all fields are present in the JSON file, as the `Model` class requires `top_k` during initialization. Missing fields may cause errors when loading the file.

## License

```text
MIT License

Copyright (c) 2025 Santosh Kanumuri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

