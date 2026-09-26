from app.tasks.nasa_tasks import fetch_nasa_firms_data
import logging

logging.basicConfig(level=logging.INFO)

# Run the task directly (synchronously) to see the output
print("Running NASA FIRMS ingestion task manually...")
fetch_nasa_firms_data()
