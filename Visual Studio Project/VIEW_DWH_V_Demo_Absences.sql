CREATE OR ALTER VIEW DWH.V_Demo_Absences AS
SELECT
    TOP 100 *
FROM [dbo].[V_Demo2_Absences] 
CROSS JOIN [DWH].[V_Demo2_Absences] 