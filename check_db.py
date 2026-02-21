
import os
from sqlalchemy import create_engine, inspect

db_url = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"
engine = create_engine(db_url)
inspector = inspect(engine)

columns = inspector.get_columns('creations')
for column in columns:
    print(f"Column: {column['name']}, Nullable: {column['nullable']}, Type: {column['type']}")
