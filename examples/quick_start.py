"""Quick‑start example for Flop Technocore Toolkit."""

from flop_technocore import TechnocoreClient

# Replace with your real key or rely on .flopconfig.yaml
client = TechnocoreClient(api_key="YOUR_API_KEY")

status = client.get_status()
print("Platform status:", status)
