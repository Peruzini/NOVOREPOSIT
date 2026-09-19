USE WAREHOUSE __WAREHOUSE__;
USE DATABASE __DATABASE__;
USE SCHEMA __DATABASE__.__SCHEMA__;
-- Upload build/fleet_daily.csv to FLEET_STAGE via Snowsight, keeping its name.
-- First load must target the empty table created by 01_setup.sql.
SELECT COUNT(*) AS ROWS_BEFORE_LOAD FROM FLEET_DAILY;
COPY INTO FLEET_DAILY FROM @FLEET_STAGE
  FILES=('fleet_daily.csv') FILE_FORMAT=(FORMAT_NAME=FLEET_CSV)
  ON_ERROR='ABORT_STATEMENT' FORCE=FALSE;
-- Do not use FORCE=TRUE or load a renamed copy: the PK is not enforced.
