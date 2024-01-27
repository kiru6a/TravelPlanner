from sqlalchemy import create_engine, text
import configparser


config = configparser.ConfigParser()
config.read("config.properties")

dbConnectionString = config.get("DEFAULT", "DB_CONNECTION_STRING")

engine = create_engine(dbConnectionString)


with engine.connect() as conn:
  result = conn.execute(text("select * from planner_user"))
  print(result.all())