IF EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'V_Demo2_Absences') DROP EXTERNAL TABLE [dbo].[V_Demo2_Absences] ;

	DECLARE @prmDynamicSQL1 nvarchar(max) = ''
	DECLARE @prmDynamicSQL2 nvarchar(max) = ''
	DECLARE @prmDateTime nvarchar(max) = (SELECT CONVERT(nvarchar(110),GETDATE(),21))

	SET @prmDynamicSQL1 = '
    CREATE EXTERNAL TABLE [dbo].[V_Demo2_Absences] 
	WITH (DATA_SOURCE = [ADLSGen2_SAS],LOCATION = N''STAGING/DEPLOY/'+@prmDateTime+''',FILE_FORMAT = [SynapseParquetFormat])
	AS 
    (
        SELECT CONVERT(int,''1'') AS [ABSENCEID],
CONVERT(nvarchar(4000),''1'') AS [DESCRIPTION],
CONVERT(int,''1'') AS [COLOR],
CONVERT(int,''1'') AS [CALCASWORKED],
CONVERT(int,''1'') AS [SHORTLONGABSENCES],
CONVERT(int,''1'') AS [DAYTOLERANCE],
CONVERT(int,''1'') AS [MORNINGTOLERANCE],
CONVERT(int,''1'') AS [AFTERNOONTOLERANCE],
CONVERT(int,''1'') AS [FROMTILLTOLERANCE],
CONVERT(int,''1'') AS [BREAKFROMABSENCE],
CONVERT(nvarchar(4000),''1'') AS [ABBREVIATION],
CONVERT(int,''1'') AS [STATUSASPRESENCE],
CONVERT(int,''1'') AS [APPROVAL_PCT4W],
CONVERT(int,''1'') AS [APPROVAL_WEB],
CONVERT(bit,''1'') AS [ISBREAK],
CONVERT(bit,''1'') AS [ISPAYED],
CONVERT(nvarchar(4000),''1'') AS [Description_TransKey],
CONVERT(nvarchar(4000),''1'') AS [Abbreviation_TransKey],
CONVERT(bit,''1'') AS [IsDeleted]'

	SET @prmDynamicSQL2 = '
			WHERE 1=2
    )'
	EXEC(@prmDynamicSQL1+@prmDynamicSQL2)