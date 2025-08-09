# Kedra Scraper Challenge

## Overview

This project implements a web scraping and data processing pipeline for legal documents published on the Workplace Relations website. It was developed as a solution to a coding assignment, using **Scrapy** for crawling, **Dagster** for orchestration, **MongoDB** for metadata storage, and **MinIO** (S3-compatible object storage) for file storage. The pipeline scrapes "decisions" (legal case documents) from the Workplace Relations site, stores the raw HTML/PDF files and metadata, then cleans and transforms the HTML documents for easier analysis. The system is designed with monthly data partitions and can be run on a schedule (monthly) or on-demand via a web UI.

## Features

* **Scrapy Web Scraping:** Crawls Workplace Relations decisions with monthly partitions, capturing metadata (ID, date, topic, title, description) and downloading HTML/PDF/DOCX files.

* **Data Storage:** Saves metadata in MongoDB and files in MinIO (`landing-docs` for raw files) with storage paths and SHA-256 hashes.

* **Processing:** Cleans HTML documents with BeautifulSoup, stores cleaned files in `clean-docs` bucket, and writes updated metadata (including new file hash) to MongoDB.

* **Dagster Orchestration:** Two assets (`landing_scrape` and `transform_docs`) run sequentially with monthly partitions and scheduling. UI supports manual runs and monitoring.

* **Configurable & Portable:** Uses `.env` files for configuration. Docker setups for MongoDB, MinIO, Postgres, and Dagster enable easy local or containerized deployment.


## Project Structure

```text
├── src/
│   └── wpr/                     # Scrapy project for Workplace Relations (WPR) scraping
├── dagster_repo/                # Dagster project components
├── docker/                      # Dockerfiles and Compose configurations
│       └── .env.dagster         # Docker Compose to launch infrastructure services (Mongo, MinIO, Postgres)
├── .env.example                 # Example environment variables for local run (Mongo URI, MinIO keys, etc.)
└── docker/.env.dagster          # Example environment variables for Docker deployment (service creds and names)
```

## Installation & Setup

1. **Prerequisites:** Make sure you have **Python 3.10+** installed and Docker running on your system. This project uses **uv** (Astral's ultra-fast environment manager) to manage dependencies, so you will need to install `uv` if not already available. You can [follow installation instructions provided by Astral](https://docs.astral.sh/uv/getting-started/installation/).

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/MaxHermez/kedra_scraper_challenge.git
   cd kedra_scraper_challenge
   ```

3. **Configure Environment Variables:** Copy the example environment files and adjust if needed:

   ```bash
   cp .env.example .env               # Base configuration (MongoDB, MinIO settings for local/infra)
   cp docker/.env.dagster docker/.env # Dagster container environment (service names, creds)
   ```

   By default, the example env files are set up for local usage with Docker using placeholder credentials

4. **Install Python Dependencies:** Use **uv** to create an isolated environment and install the required packages:

   ```bash
   uv sync
   ```

5. **Launch Infrastructure Services:** Before running the pipeline, start the supporting services using Docker Compose:

   ```bash
   cd docker
   docker compose -f docker-compose.infra.yml --env-file .env up -d
   ```

   This will spin up the **MongoDB** database, **MinIO** object storage, and a **Postgres** instance (for Dagster's own metadata storage) in the background. The services are defined in `docker-compose.infra.yml` and use the settings from your `.env` file. Once up, MongoDB will be listening on port 27017 and MinIO on port 9000 (with a web console on 9001).

## Usage

You can run the pipeline either in development mode (locally on your machine with the Dagster UI) or within Docker containers. Both approaches require that the infrastructure services are running (as started in the setup step above).

### Running Locally (Dagster Development)

For interactive development and testing, you can use Dagster's development server:

> **_NOTE:_** If you want to persist Dagster's state between runs, you should either use the Docker setup or set the `DAGSTER_HOME` environment variable to a local directory.

1. **Start the Dagster UI:** In the project root, run:

   ```bash
   dagster dev -m dagster_repo
   ```

   This will launch the Dagster web UI and scheduler using the assets and definitions in the `dagster_repo` module. By default, Dagster will bind to port 3000.

2. **Open the Dagster UI:** Visit [http://localhost:3000](http://localhost:3000) in your browser. You should see the Dagster instance with the assets and job loaded (look for assets named **landing\_scrape** and **transform\_docs**, and a job called **wpr\_monthly\_job**).

3. **Run a Pipeline Job:** From the Dagster UI, you can manually launch the pipeline:

   * Navigate to the **Assets** or **Jobs** panel and find `wpr_monthly_job`. This job encompasses both the scraping and transformation steps.
   * Click "Launch Run" (or materialize assets) and select a partition (e.g., a specific month) if prompted. The pipeline is partitioned by month; for example, you might choose the partition for `2025-06-01` (June 2025) to scrape and process decisions from that month. If you don't select a partition, Dagster may run for the default or latest partition.
   * Confirm to start the run. You can monitor the progress in real-time in the Dagster UI. The `landing_scrape` asset will execute first (running the Scrapy spider to fetch data), followed by `transform_docs` (processing the fetched documents).

4. **Scheduled Runs:** The project includes a schedule (`wpr_monthly_schedule`) that is set to run the job on the 2nd of each month at 03:00 AM (server time). If the Dagster scheduler is running, it will automatically kick off monthly runs according to this schedule. You can enable or disable this schedule in the Dagster UI under the "Schedules" section. (Ensure the Dagster daemon is running if you want scheduled runs; in `dagster dev` mode, the scheduler should be active.)

5. **Inspecting Results:** After a run completes, you can verify that:

   * **MongoDB** contains the new records: The raw scraped metadata should be in the configured raw collection, and processed records in the configured processed collection of the MongoDB database. Each record includes fields like `decision_id`, `topic`, dates, description, etc., along with file storage info.
   * **MinIO** contains the files: Using the MinIO console (at [http://localhost:9001](http://localhost:9001)) or another S3 browser, check the buckets:

     * The **landing-docs** bucket will have raw files (HTML or PDFs) stored under a prefix (such as `raw/<partition_date>/...`). Filenames are hashed, so you'll see non-human-friendly keys, but the structure groups them by partition (month).
     * The **clean-docs** bucket will have cleaned HTML files (for decisions that were HTML originally) under a similar partitioned structure. Binary files (PDF/DOC) are typically copied as-is to the clean bucket with their original format.
   * **Dagster logs:** The Dagster UI will show logs for each step, which can be useful to see what was scraped or any issues encountered.

### Running via Docker

To run the entire pipeline in Docker (which is closer to a production deployment scenario, but with some differences), follow these steps:

1. **Build and Start the Pipeline Container:** Use Docker Compose to build the Dagster pipeline image and run it alongside the infrastructure services:

   ```bash
   cd docker
   docker compose -f docker-compose.yml --env-file ./.env up --build
   ```

   This will build the image (using `Dockerfile_wpr`) and start a container running the Dagster code (service named `dagster_wpr`). It will connect to the MongoDB, MinIO, and Postgres services that were launched earlier (they all share the same Docker network).

2. **Access Dagster UI:** Once the `dagster_wpr` container is up, the Dagster web UI should be accessible on [http://localhost:3000](http://localhost:3000) (as defined in the compose file port mapping). Open this in your browser to interact with the pipeline just as in local mode.

3. **Run Jobs or Monitor Schedule:** In the Dagster UI (running from inside the container), you can manually trigger runs of `wpr_monthly_job` or let the schedule run it automatically each month. The behavior and outcome are the same as described in the local running section. All data will persist in the Dockerized MongoDB and MinIO. The Dagster instance inside the container will use the configuration from `docker/.env` (which you set up earlier) for connecting to those services.

4. **Shutting Down:** To stop the pipeline container and associated services, you can bring down the Docker Compose setups:

   * Stop the pipeline and UI container with **Ctrl+C** if it’s in the foreground, or with `docker compose down` (when run in detached mode).
   * To stop the infrastructure services, run:

     ```bash
     docker compose -f docker-compose.infra.yml --env-file .env down
     ```

     (Add `-v` if you also want to remove the named volumes created for persistence, e.g. MongoDB data.)
