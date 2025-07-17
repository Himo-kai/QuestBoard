"""Database migration package."""

def run_migration():
    """Run all pending migrations."""
    from pathlib import Path
    import importlib.util
    import logging
    
    logger = logging.getLogger(__name__)
    logger.propagate = False  # Prevent duplicate logs
    migrations_dir = Path(__file__).parent
    
    # Find all migration files
    migration_files = sorted(
        [f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"]
    )
    
    if not migration_files:
        logger.info("No migrations to run")
        return
    
    logger.info(f"Found {len(migration_files)} migration(s) to run")
    
    # Run each migration
    for migration_file in migration_files:
        module_name = migration_file.stem
        spec = importlib.util.spec_from_file_location(module_name, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        logger.info(f"Running migration: {module_name}")
        try:
            module.run_migration()
            logger.info(f"Migration {module_name} completed successfully")
        except Exception as e:
            logger.error(f"Error running migration {module_name}: {e}")
            raise
