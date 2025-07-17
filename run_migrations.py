#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Run database migrations."""
import logging
from migrations import run_migration

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration()
