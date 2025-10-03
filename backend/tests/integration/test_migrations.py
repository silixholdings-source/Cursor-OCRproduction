import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

class TestDatabaseMigrations:
    """Test database migrations and schema"""
    
    @pytest.fixture(scope="class")
    def test_db_engine(self):
        """Create test database engine"""
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_erp_test")
        engine = create_engine(database_url)
        return engine
    
    @pytest.fixture(scope="class")
    def test_db_session(self, test_db_engine):
        """Create test database session"""
        Session = sessionmaker(bind=test_db_engine)
        session = Session()
        yield session
        session.close()
    
    def test_database_connection(self, test_db_engine):
        """Test database connection"""
        with test_db_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    def test_database_schema_exists(self, test_db_engine):
        """Test that database schema exists"""
        with test_db_engine.connect() as connection:
            # Check if information_schema exists (PostgreSQL)
            result = connection.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'public'
            """))
            assert result.fetchone() is not None
    
    def test_database_tables_created(self, test_db_engine):
        """Test that database tables are created"""
        with test_db_engine.connect() as connection:
            # This will be expanded when models are implemented
            # For now, just check that we can connect and query
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert "ai_erp" in db_name.lower()
    
    def test_migration_scripts_exist(self):
        """Test that migration scripts exist"""
        migrations_dir = "migrations"
        assert os.path.exists(migrations_dir), "Migrations directory should exist"
        
        # Check for alembic.ini
        alembic_ini = "alembic.ini"
        assert os.path.exists(alembic_ini), "alembic.ini should exist"
    
    def test_database_permissions(self, test_db_engine):
        """Test database user permissions"""
        with test_db_engine.connect() as connection:
            # Test basic CRUD permissions
            try:
                # Test CREATE
                connection.execute(text("CREATE TABLE test_permissions (id SERIAL PRIMARY KEY)"))
                
                # Test INSERT
                connection.execute(text("INSERT INTO test_permissions (id) VALUES (1)"))
                
                # Test SELECT
                result = connection.execute(text("SELECT id FROM test_permissions WHERE id = 1"))
                assert result.scalar() == 1
                
                # Test UPDATE
                connection.execute(text("UPDATE test_permissions SET id = 2 WHERE id = 1"))
                
                # Test DELETE
                connection.execute(text("DELETE FROM test_permissions WHERE id = 2"))
                
                # Cleanup
                connection.execute(text("DROP TABLE test_permissions"))
                connection.commit()
                
            except Exception as e:
                pytest.fail(f"Database permissions test failed: {e}")
    
    def test_database_connection_pool(self, test_db_engine):
        """Test database connection pool"""
        # Test multiple concurrent connections
        connections = []
        try:
            for i in range(5):
                conn = test_db_engine.connect()
                connections.append(conn)
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            for conn in connections:
                conn.close()
    
    def test_database_transactions(self, test_db_engine):
        """Test database transaction handling"""
        with test_db_engine.connect() as connection:
            try:
                # Start transaction
                trans = connection.begin()
                
                # Create test table
                connection.execute(text("CREATE TABLE test_transaction (id SERIAL PRIMARY KEY)"))
                
                # Insert data
                connection.execute(text("INSERT INTO test_transaction (id) VALUES (1)"))
                
                # Rollback transaction
                trans.rollback()
                
                # Verify rollback worked
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'test_transaction'
                """))
                assert result.fetchone() is None
                
            except Exception as e:
                pytest.fail(f"Transaction test failed: {e}")
    
    def test_database_indexes(self, test_db_engine):
        """Test database index creation"""
        with test_db_engine.connect() as connection:
            try:
                # Create test table with index
                connection.execute(text("""
                    CREATE TABLE test_indexes (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        email VARCHAR(100)
                    )
                """))
                
                # Create index
                connection.execute(text("CREATE INDEX idx_test_indexes_name ON test_indexes(name)"))
                
                # Verify index exists
                result = connection.execute(text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'test_indexes' AND indexname = 'idx_test_indexes_name'
                """))
                assert result.fetchone() is not None
                
                # Cleanup
                connection.execute(text("DROP TABLE test_indexes"))
                connection.commit()
                
            except Exception as e:
                pytest.fail(f"Index test failed: {e}")
