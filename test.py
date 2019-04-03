import json
from migrate import Cache, MigrationControl, Model


m = MigrationControl()
m.check_migration(
    {
        "Test4": {
            "type": "model",
            "properties": {
                "title": {"type": "int", "max-length": "255"},
                "some": {"type": "varchar", "max-length": "255"},
            },
        },

        "Test6": {
            "type": "model",
            "properties": {
                "title": {"type": "int", "max-length": "255"},
                "some": {"type": "varchar", "max-length": "255"},
                "test": {"type": "foreign-key", "max-length": "255", "model": "Test4"},
            },
        }
    }
)



