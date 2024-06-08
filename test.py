from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("select * from planner_user"))
    print(result.all())
