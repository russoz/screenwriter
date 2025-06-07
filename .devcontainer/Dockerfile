# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later

# Use the official Microsoft Python devcontainer image from the Docker Hub
FROM mcr.microsoft.com/devcontainers/python:3

# Set the working directory in the container
WORKDIR /workspace

# Install poetry
RUN pip install -U pip \
 && pip install poetry pre-commit
