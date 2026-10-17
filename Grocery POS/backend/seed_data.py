#!/usr/bin/env python
"""CLI helper to run database seeding directly from backend directory."""
import sys
import os

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))

from app.seeds.seed_data import seed_database

if __name__ == "__main__":
    seed_database()
