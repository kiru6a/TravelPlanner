from sqlalchemy import create_engine, text


dbConnectionString = "mysql+pymysql://avnadmin:AVNS_UX4e4F-e4ljxYcWQOcG@travel-planner-travel-planner.a.aivencloud.com:10904/travel_planner?charset=utf8mb4"

engine = create_engine(dbConnectionString)


with engine.connect() as conn:
  result = conn.execute(text("select * from planner_user"))
  print(result.all())