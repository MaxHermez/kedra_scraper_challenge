from dagster import ScheduleDefinition, define_asset_job
from dagster_repo.assets import landing_scrape, transform_docs
from dagster_repo.partitions import monthly

job = define_asset_job(
    name="wpr_monthly_job",
    selection=[landing_scrape, transform_docs],
    partitions_def=monthly,
)

schedule = ScheduleDefinition(
    name="wpr_monthly_schedule",
    job=job,
    cron_schedule="0 3 2 * *"
)
