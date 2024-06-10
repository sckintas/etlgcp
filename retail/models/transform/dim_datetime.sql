-- Create a CTE to extract date and time components
WITH datetime_cte AS (
  SELECT DISTINCT
    InvoiceDate AS datetime_id,
    CASE
      WHEN LENGTH(CAST(InvoiceDate AS STRING)) = 16 THEN
        -- Date format: "DD/MM/YYYY HH:MM"
        PARSE_DATETIME('%d/%m/%Y %H:%M', CAST(InvoiceDate AS STRING))
      WHEN LENGTH(CAST(InvoiceDate AS STRING)) <= 14 THEN
        -- Date format: "MM/DD/YY HH:MM"
        PARSE_DATETIME('%m/%d/%y %H:%M', CAST(InvoiceDate AS STRING))
      ELSE
        NULL
    END AS date_part
  FROM {{ source('retail', 'raw_invoices') }}
  WHERE InvoiceDate IS NOT NULL
)

SELECT
  datetime_id,
  date_part AS datetime,
  EXTRACT(YEAR FROM date_part) AS year,
  EXTRACT(MONTH FROM date_part) AS month,
  EXTRACT(DAY FROM date_part) AS day,
  EXTRACT(HOUR FROM date_part) AS hour,
  EXTRACT(MINUTE FROM date_part) AS minute,
  EXTRACT(DAYOFWEEK FROM date_part) AS weekday
FROM datetime_cte
