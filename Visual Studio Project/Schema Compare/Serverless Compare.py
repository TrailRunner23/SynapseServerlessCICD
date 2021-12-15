import pyodbc
import pandas as pd
import os
import json


with open(os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))+"/PersonalCredentials.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

username = jsonObject['username']
password = jsonObject['password']
server = jsonObject['server']
database = jsonObject['database']
wdir = jsonObject['wdir']

driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';Authentication=ActiveDirectoryInteractive')

sql = """
SELECT *
FROM (
    SELECT 
    N'VIEW' AS Type, s.name AS TABLE_SCHEMA, V.Name AS TABLE_NAME, 
	REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(M .Definition
	,'CREATE VIEW','CREATE OR ALTER VIEW')
	,'CREATE  VIEW','CREATE OR ALTER VIEW')
	,'CREATE   VIEW','CREATE OR ALTER VIEW')
	,'CREATE    VIEW','CREATE OR ALTER VIEW')
	,'CREATE     VIEW','CREATE OR ALTER VIEW')
	,'CREATE      VIEW','CREATE OR ALTER VIEW')
	,'CREATE        VIEW','CREATE OR ALTER VIEW')
	,'CREATE         VIEW','CREATE OR ALTER VIEW')
	,'CREATE          VIEW','CREATE OR ALTER VIEW')
	AS Definition
    FROM sys.views V
    INNER JOIN sys.sql_modules M
    ON V. object_id = M.object_id
    INNER JOIN sys.schemas S
    ON S.schema_id = v.schema_id
    
    UNION ALL

    SELECT 
    N'TABLE' AS Type, CC.TABLE_SCHEMA, CC.TABLE_NAME, 
    'IF EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '''+CC.TABLE_SCHEMA+''' AND TABLE_NAME = '''+CC.TABLE_NAME+''') DROP EXTERNAL TABLE ['+CC.TABLE_SCHEMA+'].['+CC.TABLE_NAME+'] ;

	DECLARE @prmDynamicSQL1 nvarchar(max) = ''''
	DECLARE @prmDynamicSQL2 nvarchar(max) = ''''
	DECLARE @prmDateTime nvarchar(max) = (SELECT CONVERT(nvarchar(110),GETDATE(),21))

	SET @prmDynamicSQL1 = ''
    CREATE EXTERNAL TABLE ['+CC.TABLE_SCHEMA+'].['+CC.TABLE_NAME+'] 
	WITH (DATA_SOURCE = [ADLSGen2_SAS],LOCATION = N''''STAGING/DEPLOY/''+@prmDateTime+'''''',FILE_FORMAT = [SynapseParquetFormat])
	AS 
    (
        SELECT ' + SUBSTRING(CC.ColumnList, 0, 4000 - CHARINDEX(',', REVERSE(LEFT(CC.ColumnList, 4000))) + 2)+'''

	SET @prmDynamicSQL2 = ''' + SUBSTRING(CC.ColumnList, 4000 - CHARINDEX(',', REVERSE(LEFT(CC.ColumnList, 4000))) + 2, LEN(CC.ColumnList)) + '
			WHERE 1=2
    )''
	EXEC(@prmDynamicSQL1+@prmDynamicSQL2)'
    AS Definition
	FROM (
		SELECT CC.TABLE_SCHEMA, CC.TABLE_NAME, 
		STRING_AGG('CONVERT('+CASE 
            WHEN CC.DATA_TYPE LIKE '%int%' THEN CC.DATA_TYPE
            WHEN CC.DATA_TYPE LIKE '%char%' THEN CC.DATA_TYPE+'('+CONVERT(nvarchar(10),ABS(CC.CHARACTER_MAXIMUM_LENGTH))+')'
            WHEN CC.DATA_TYPE LIKE '%decimal%' THEN CC.DATA_TYPE+'(38,20)'
            WHEN CC.DATA_TYPE LIKE 'varbinary' THEN CC.DATA_TYPE+'(64)'
            ELSE CC.DATA_TYPE
            END +',''''1'''') AS ['+CONVERT(nvarchar(max),CC.COLUMN_NAME)+']'
            ,','+CHAR(10)) AS ColumnList
		FROM sys.external_tables V
		INNER JOIN sys.schemas S
		ON S.schema_id = V.schema_id
		INNER JOIN INFORMATION_SCHEMA.COLUMNS CC
		ON CC.TABLE_NAME = V.name
		AND CC.TABLE_SCHEMA = S.name
		GROUP BY CC.TABLE_SCHEMA, CC.TABLE_NAME, V.location
		) CC
    ) A 
ORDER By Type, TABLE_SCHEMA, TABLE_NAME
"""
dfA = pd.read_sql(sql,cnxn)

# for (dirpath, dirnames, filenames) in walk(wdir):

if os.path.exists(wdir+'DeployScript.sql'):
    os.remove(wdir+'DeployScript.sql')

f = open(wdir+'DeployScript.sql','a')

for i in range(len(dfA)):
    fileName = dfA["Type"][i]+'_'+dfA["TABLE_SCHEMA"][i]+'_'+dfA["TABLE_NAME"][i]+'.sql'
    print(fileName)
    ## Step 1 Create TMP file: 
    f = open(wdir+"TMP_"+fileName, "w") # 'w' overwrites existing content
    f.write(dfA["Definition"][i].replace(r'\r\n', r'\n'))
    f.close()
    newContent = open(wdir+"TMP_"+fileName,'r').read()
    ## Step 2 Read Existing file: 
    try:
        originalContent = open(wdir+fileName,'r').read()
    except:
        originalContent = ""
    ## Step 3 Compare
    if originalContent != newContent:
        print('Diff in file ',dfA["Type"][i]+'_'+dfA["TABLE_SCHEMA"][i]+'_'+dfA["TABLE_NAME"][i])
        f = open(wdir+fileName, "w") # 'w' overwrites existing content
        f.write(dfA["Definition"][i])
        f.close()
    ## Step 4 Create Deploy File
    f = open(wdir+'DeployScript.sql','a')
    f.write("PRINT('-- Start "+fileName+"')\n")
    f.write("GO\n")
    f.write(":r $(filepath)\\"+fileName+"\n")
    f.write("GO\n")
    f.write("PRINT('-- End "+fileName+"')\n")
    f.write("GO\n")
    f.close()
    ## Step 5 Clean-Up TMP files
    os.remove(wdir+"TMP_"+fileName)
