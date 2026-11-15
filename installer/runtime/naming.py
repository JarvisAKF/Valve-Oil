from __future__ import annotations


REPOSITORY_URL = "https://github.com/thelegendtubaguy/valve-oil"
ISSUES_URL = f"{REPOSITORY_URL}/issues"
BUNDLE_NAME_PREFIX = "tltg-optimized-macros"
# The release archive: valve-oil.tar.gz, or valve-oil-dev.tar.gz for dev builds.
ARCHIVE_NAME_PREFIX = "valve-oil"
ARCHIVE_NAME = f"{ARCHIVE_NAME_PREFIX}.tar.gz"
# The bundle's folder, in the archive and in the printer user's home.
BUNDLE_ROOT_NAME = "valve-oil"
# Installs from 26.11.12.2 and earlier live in ~/tltg-optimized-macros and update themselves from the archive's
# earlier name, which they accept only with the earlier folder at its root. Releases also publish that archive.
LEGACY_BUNDLE_ROOT_NAME = BUNDLE_NAME_PREFIX
LEGACY_ARCHIVE_NAME = f"{BUNDLE_NAME_PREFIX}.tar.gz"
INSTALL_BACKUP_LABEL_PREFIX = f"{BUNDLE_NAME_PREFIX}-before-optimize"
UNINSTALL_BACKUP_LABEL_PREFIX = f"{BUNDLE_NAME_PREFIX}-before-uninstall"
