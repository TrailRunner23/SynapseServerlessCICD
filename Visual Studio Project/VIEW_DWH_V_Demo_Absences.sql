CREATE OR ALTER VIEW DWH.V_Demo_Absences AS
SELECT
    TOP 100 *
FROM
    OPENROWSET(
        BULK 'https://tgdataplatformdev.dfs.core.windows.net/datalakedev/STAGING/ATPS/ABSENCES/ABSENCES.parquet',
        FORMAT = 'PARQUET'
    ) AS [result]