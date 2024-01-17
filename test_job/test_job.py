import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame
from awsglue import DynamicFrame
 
 
def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
 
 
# Script generated for node Custom transform
def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    newdf = dfc.select(list(dfc.keys())[0]).toDF()
    newdata = DynamicFrame.fromDF(newdf, glueContext, "newdata")
    return DynamicFrameCollection(
        {"CustomTransform0": newdata.coalesce(1)}, glueContext
    )
 
 
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
 
# Script generated for node S3 bucket Emp
S3bucketEmp_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": '"', "withHeader": True, "separator": "\t"},
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://sid-nfh-10301/test_source/emp.txt"],
        "recurse": True,
    },
    transformation_ctx="S3bucketEmp_node1",
)
 
# Script generated for node Amazon S3 Dept
AmazonS3Dept_node1637084080372 = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": '"', "withHeader": True, "separator": "\t"},
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://sid-nfh-10301/test_source/dept.txt"],
        "recurse": True,
    },
    transformation_ctx="AmazonS3Dept_node1637084080372",
)
 
# Script generated for node ApplyMapping (to rename column)
ApplyMappingtorenamecolumn_node2 = ApplyMapping.apply(
    frame=S3bucketEmp_node1,
    mappings=[
        ("ID", "long", "ID", "long"),
        ("First_Name", "string", "First_Name", "string"),
        ("Last_Name", "string", "Last_Name", "string"),
        ("Dept", "long", "Dept_Fk", "long"),
    ],
    transformation_ctx="ApplyMappingtorenamecolumn_node2",
)
 
# Script generated for node Join
Join_node1637084138436 = Join.apply(
    frame1=ApplyMappingtorenamecolumn_node2,
    frame2=AmazonS3Dept_node1637084080372,
    keys1=["Dept_Fk"],
    keys2=["Dept"],
    transformation_ctx="Join_node1637084138436",
)
 
# Script generated for node SQL
SqlQuery0 = """
select First_Name||' '||Last_name as full_name, Dept_name from myDataSource
 
"""
SQL_node1637084168048 = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={"myDataSource": Join_node1637084138436},
    transformation_ctx="SQL_node1637084168048",
)
 
# Script generated for node Custom transform
Customtransform_node1637084217456 = MyTransform(
    glueContext,
    DynamicFrameCollection(
        {"SQL_node1637084168048": SQL_node1637084168048}, glueContext
    ),
)
 
# Script generated for node Select From Collection
SelectFromCollection_node1637084479632 = SelectFromCollection.apply(
    dfc=Customtransform_node1637084217456,
    key=list(Customtransform_node1637084217456.keys())[0],
    transformation_ctx="SelectFromCollection_node1637084479632",
)
 
# Script generated for node Amazon S3
AmazonS3_node1637084486751 = glueContext.write_dynamic_frame.from_options(
    frame=SelectFromCollection_node1637084479632,
    connection_type="s3",
    format="csv",
    connection_options={
        "path": "s3://sid-nfh-10301/test_dest/",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1637084486751",
)
 
job.commit()